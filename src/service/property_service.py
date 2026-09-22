from datetime import datetime

from src.models.asset import Asset


class PropertyService:
    def __init__(self, client):
        self.client = client

    def get_property_aggregates(self, event) -> dict:
        body = event["body"]
        asset = Asset(body["assetId"])
        start_time = datetime.strptime(body["startTime"], "%Y-%m-%d")
        end_time = datetime.strptime(body["endTime"], "%Y-%m-%d")
        interval = body["interval"]

        asset_response = self.client.describe_asset(assetId=asset.asset_id)
        asset_properties = {
            prop["id"]: prop["name"] for prop in asset_response["assetProperties"]
        }

        properties_needed = set(body["propertiesNeeded"])
        asset_properties_aggregates = {}

        for prop_id, prop_name in asset_properties.items():
            if prop_name not in properties_needed:
                continue

            prop_val = self.client.get_asset_property_value(
                assetId=asset.asset_id, propertyId=prop_id
            )

            if "stringValue" in prop_val["propertyValue"]["value"]:
                aggregate_types = ["COUNT"]
            else:
                aggregate_types = body["aggregateTypes"]

            aggregates = self.client.get_asset_property_aggregates(
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
