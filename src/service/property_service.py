from datetime import datetime


class PropertyService:
    def __init__(self, repo):
        self.repo = repo

    def get_property_aggregates(self, event) -> dict:
        body = event["body"]
        asset_id = body["assetId"]

        start_time = datetime.strptime(body["startTime"], "%Y-%m-%d")
        end_time = datetime.strptime(body["endTime"], "%Y-%m-%d")
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())

        raw_results = self.repo.get_aggregates_for_properties(
            asset_id=asset_id,
            properties_needed=body["propertiesNeeded"],
            aggregate_types=body["aggregateTypes"],
            interval=body["interval"],
            start_ts=start_ts,
            end_ts=end_ts,
        )

        asset_properties_aggregates = {}
        for result in raw_results:
            prop_name = result["property_name"]
            aggregates = result["aggregates"]

            if not aggregates:
                asset_properties_aggregates[prop_name] = {}
                continue

            aggregate_values = {}
            for aggregate in aggregates:
                agg_type = list(aggregate["value"].keys())[0]
                agg_value = aggregate["value"][agg_type]
                aggregate_values[agg_type] = agg_value
                break

            asset_properties_aggregates[prop_name] = aggregate_values

        return asset_properties_aggregates
