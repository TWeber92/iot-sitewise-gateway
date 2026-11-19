import os
import json
import random
from datetime import datetime, timedelta, timezone

import boto3
from botocore.client import Config
from dotenv import load_dotenv

# ---------------------------------------------------------
# Deterministic history settings
# ---------------------------------------------------------
# Fixed anchor so the data always falls inside a known window (2025) and
# never drifts with the day the script is run. Noon avoids sitting exactly
# on a "2025-01-01 00:00 UTC" boundary, which an exclusive startDate drops.
BASE_TIME = datetime(2025, 1, 1, 12, tzinfo=timezone.utc)
rng = random.Random(42)  # fixed seed: same values on every run


def generate_history(base_val, variance, points=50, step_hours=24, is_int=False):
    """Generates TQV (time-quality-value) history, oldest first.

    Every 10th point is BAD quality so a qualities=["GOOD"] filter has work
    to do: 50 points -> 45 GOOD, 5 BAD.
    """
    history = []
    for i in range(points):
        ts = int((BASE_TIME + timedelta(hours=i * step_hours)).timestamp())
        val = base_val + rng.uniform(-variance, variance)
        if is_int:
            val_obj = {"integerValue": int(val)}
        else:
            val_obj = {"doubleValue": round(val, 2)}

        history.append(
            {
                "timestamp": {"timeInSeconds": ts, "offsetInNanos": 0},
                "value": val_obj,
                "quality": "BAD" if i % 10 == 9 else "GOOD",
            }
        )
    return history


# ---------------------------------------------------------
# 1. THE LINE ASSETS (Parent)
# ---------------------------------------------------------
def make_line(asset_id, name, status, speed, downtime, children):
    return {
        "id": asset_id,
        "name": name,
        "status": status,
        "properties": {
            "lineName": name,
            "lineId": asset_id,
            "lineStatus": 1 if status == "ACTIVE" else 0,
            "speed": speed,
            "maintenance": "scheduled" if status == "MAINTENANCE" else "ok",
            "schedule": "24/7",
            "machineDowntime": downtime,
        },
        "hierarchies": [{"id": f"{asset_id}-hierarchy", "name": "Contains Machines"}],
        "children": children,
        "history": {
            "speed": generate_history(speed, 5, is_int=True) if speed > 0 else [],
            "machineDowntime": generate_history(downtime, 2, is_int=True),
        },
        "aggregates": {
            "speed": [{"value": {"AVERAGE": speed}}],
            "machineDowntime": [{"value": {"SUM": downtime}}],
        },
    }


# ---------------------------------------------------------
# 2. THE MACHINE ASSETS (Children)
# ---------------------------------------------------------
def make_machine(asset_id, name, status, base_temp, base_torque):
    # Authentic property names based on your assetMeasurements list
    props = {
        "X1 Servo Motor Temperature": base_temp,
        "X1 Positioning Average Torque": base_torque,
        "X1 Insulation Resistance": 500.0,
    }

    history = {
        "X1 Servo Motor Temperature": generate_history(base_temp, 2.5),
        "X1 Positioning Average Torque": generate_history(base_torque, 0.5),
    }

    aggregates = {
        "X1 Servo Motor Temperature": [
            {"value": {"AVERAGE": base_temp, "MAX": base_temp + 3}}
        ],
        "X1 Positioning Average Torque": [{"value": {"AVERAGE": base_torque}}],
    }

    return {
        "id": asset_id,
        "name": name,
        "status": status,
        "properties": props,
        "hierarchies": [],
        "children": [],
        "history": history,
        "aggregates": aggregates,
    }


# ---------------------------------------------------------
# 3. BUILD THE TREE
# ---------------------------------------------------------
# Authentic UUIDs from actual Hannover project format
LINE_1_ID = "057bdfea-2dc4-4d21-8d0f-c54ffec0e36c"
LINE_2_ID = "b6b0ca76-56d2-4df1-985b-45bdd70672ff"
EXTRUDER_A_ID = "0d53c0b9-a190-4e44-a023-fe941b99f0d7"
EXTRUDER_B_ID = "98ecadb1-7ec7-446f-9fb8-6bc611beba54"
EXTRUDER_C_ID = "e7de3d56-e300-498a-a890-bac851b75468"


def build_assets():
    line_1 = make_line(
        LINE_1_ID,
        "Extrusion Line 1",
        "ACTIVE",
        120,
        0,
        children=[
            {"id": EXTRUDER_A_ID, "name": "Extruder A"},
            {"id": EXTRUDER_B_ID, "name": "Extruder B"},
        ],
    )

    line_2 = make_line(
        LINE_2_ID,
        "Extrusion Line 2",
        "MAINTENANCE",
        0,
        45,
        children=[
            {"id": EXTRUDER_C_ID, "name": "Extruder C"},
        ],
    )

    extruder_a = make_machine(
        EXTRUDER_A_ID, "Extruder A", "ACTIVE", base_temp=215.4, base_torque=12.3
    )
    extruder_b = make_machine(
        EXTRUDER_B_ID, "Extruder B", "ACTIVE", base_temp=218.1, base_torque=12.1
    )
    extruder_c = make_machine(
        EXTRUDER_C_ID, "Extruder C", "MAINTENANCE", base_temp=180.0, base_torque=8.5
    )

    return [line_1, line_2, extruder_a, extruder_b, extruder_c]


# ---------------------------------------------------------
# 4. UPLOAD
# ---------------------------------------------------------
def main():
    load_dotenv()

    client = boto3.client(
        "s3",
        endpoint_url="https://s3.cloud.fx.land",
        aws_access_key_id=f"JWT:{os.environ['FULA_JWT']}",
        aws_secret_access_key="not-used",
        region_name="us-east-1",
        config=Config(
            signature_version="s3v4",
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )
    bucket = os.environ["OORT_BUCKET"]

    for asset in build_assets():
        key = f"sitewise/assets/{asset['id']}.json"
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(asset),
            ContentType="application/json",
        )
        print(f"Uploaded: {key}")

    print("Seed complete. Real-world extrusion data is now in OORT.")


if __name__ == "__main__":
    main()
