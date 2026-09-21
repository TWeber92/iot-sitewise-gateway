from datetime import datetime
import json

from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset


def get_property_aggregates(client, asset: Asset, body: dict) -> dict:
    start_time = datetime.strptime(body["startTime"], "%Y-%m-%d")
    end_time = datetime.strptime(body["endTime"], "%Y-%m-%d")
    interval = body["interval"]

    asset_response = client.describe_asset(assetId=asset.asset_id)
    asset_properties = {
        prop["id"]: prop["name"] for prop in asset_response["assetProperties"]
    }

    properties_needed = set(body["propertiesNeeded"])
    asset_properties_aggregates = {}

    for prop_id, prop_name in asset_properties.items():
        if prop_name not in properties_needed:
            continue

        prop_val = client.get_asset_property_value(
            assetId=asset.asset_id, propertyId=prop_id
        )

        if "stringValue" in prop_val["propertyValue"]["value"]:
            aggregate_types = ["COUNT"]
        else:
            aggregate_types = body["aggregateTypes"]

        aggregates = client.get_asset_property_aggregates(
            assetId=asset.asset_id,
            propertyId=prop_id,
            aggregateTypes=aggregate_types,
            resolution=interval,
            startDate=int(start_time.timestamp()),
            endDate=int(end_time.timestamp()),
            maxResults=10,
        )

        if not aggregates["aggregatedValues"]:
            asset_properties_aggregates[prop_name] = {}
            continue

        aggregate_values = {}
        for aggregate in aggregates["aggregatedValues"]:
            agg_type = list(aggregate["value"].keys())[0]
            agg_value = aggregate["value"][agg_type]
            aggregate_values[agg_type] = agg_value
            break  # only the first (latest) value

        asset_properties_aggregates[prop_name] = aggregate_values

    return asset_properties_aggregates


def lambda_handler(event, context):
    client = get_sitewise_client()
    body = event["body"]
    asset = Asset(body["assetId"])

    results = get_property_aggregates(client, asset, body)

    return {
        "statusCode": 200,
        "body": json.dumps(results),
    }
