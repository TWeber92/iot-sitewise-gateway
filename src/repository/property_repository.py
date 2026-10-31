class PropertyRepository:
    def __init__(self, client):
        self.client = client

    def get_aggregates_for_properties(
        self,
        asset_id: str,
        properties_needed: list,
        aggregate_types: list,
        interval: str,
        start_ts: int,
        end_ts: int,
    ) -> list:
        asset_response = self.client.describe_asset(assetId=asset_id)
        asset_properties = {
            prop["id"]: prop["name"]
            for prop in asset_response.get("assetProperties", [])
        }

        results = []
        properties_needed_set = set(properties_needed)

        for prop_id, prop_name in asset_properties.items():
            if prop_name not in properties_needed_set:
                continue

            prop_val = self.client.get_asset_property_value(
                assetId=asset_id, propertyId=prop_id
            )

            if "stringValue" in prop_val.get("propertyValue", {}).get("value", {}):
                types_to_use = ["COUNT"]
            else:
                types_to_use = aggregate_types

            aggregates = self.client.get_asset_property_aggregates(
                assetId=asset_id,
                propertyId=prop_id,
                aggregateTypes=types_to_use,
                resolution=interval,
                startDate=start_ts,
                endDate=end_ts,
                maxResults=10,
            )

            results.append(
                {
                    "property_name": prop_name,
                    "aggregates": aggregates.get("aggregatedValues", []),
                }
            )

        return results
