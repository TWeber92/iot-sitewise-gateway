import os
import json
import boto3
import random
from datetime import datetime, timedelta, timezone
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "s3",
    endpoint_url="https://s3-standard.oortech.com",
    aws_access_key_id=os.environ["OORT_ACCESS_KEY"],
    aws_secret_access_key=os.environ["OORT_SECRET_KEY"],
    region_name="us-east-1",
    config=Config(
        signature_version="s3v4",
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    ),
)
BUCKET = os.environ["OORT_BUCKET"]


def now_ts(offset_hours=0):
    return int((datetime.now(timezone.utc) + timedelta(hours=offset_hours)).timestamp())


def generate_history(base_val, variance, points=6, is_int=False):
    """Generates TQV (time-quality-value) history."""
    history = []
    for i in range(points):
        offset = -6 + i
        val = base_val + random.uniform(-variance, variance)
        if is_int:
            val = int(val)
            val_obj = {"integerValue": val}
        else:
            val = round(val, 2)
            val_obj = {"doubleValue": val}

        history.append(
            {"timestamp": {"timeInSeconds": now_ts(offset)}, "value": val_obj}
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
        "latest": {
            "speed": speed,
            "machineDowntime": downtime,
        },
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
        "latest": props,  # For simplicity, latest mirrors the base props
        "history": history,
        "aggregates": aggregates,
    }


# ---------------------------------------------------------
# 3. BUILD THE TREE
# ---------------------------------------------------------
# Authentic UUIDs from actual Hannover project format
LINE_1_ID = "057bdfea-2dc4-4d21-8d0f-c54ffec0e36c"
LINE_2_ID = "b6b0ca76-56d2-4df1-985b-45bdd70672ff"

line_1 = make_line(
    LINE_1_ID,
    "Extrusion Line 1",
    "ACTIVE",
    120,
    0,
    children=[
        {"id": "0d53c0b9-a190-4e44-a023-fe941b99f0d7", "name": "Extruder A"},
        {"id": "98ecadb1-7ec7-446f-9fb8-6bc611beba54", "name": "Extruder B"},
    ],
)

line_2 = make_line(
    LINE_2_ID,
    "Extrusion Line 2",
    "MAINTENANCE",
    0,
    45,
    children=[
        {"id": "e7de3d56-e300-498a-a890-bac851b75468", "name": "Extruder C"},
    ],
)

# Create the machine assets with realistic industrial values
extruder_a = make_machine(
    "0d53c0b9-a190-4e44-a023-fe941b99f0d7",
    "Extruder A",
    "ACTIVE",
    base_temp=215.4,
    base_torque=12.3,
)
extruder_b = make_machine(
    "98ecadb1-7ec7-446f-9fb8-6bc611beba54",
    "Extruder B",
    "ACTIVE",
    base_temp=218.1,
    base_torque=12.1,
)
extruder_c = make_machine(
    "e7de3d56-e300-498a-a890-bac851b75468",
    "Extruder C",
    "MAINTENANCE",
    base_temp=180.0,
    base_torque=8.5,
)

# ---------------------------------------------------------
# 4. UPLOAD
# ---------------------------------------------------------
assets = [line_1, line_2, extruder_a, extruder_b, extruder_c]

for asset in assets:
    key = f"sitewise/assets/{asset['id']}.json"
    client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(asset),
        ContentType="application/json",
    )
    print(f"Uploaded: {key}")

print("Seed complete. Real-world extrusion data is now in OORT.")
