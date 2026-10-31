from datetime import datetime
from src.models.property_historical_values import PropertyHistoricalValues
from src.models.asset import Asset
from src.models.query_params import QueryParams


class AssetService:
    def __init__(self, repo):
        self.repo = repo

    def get_asset_hierarchy(self, event) -> dict:
        body = event["body"]
        asset_id = body["assetId"]
        line_suffixes = body["lineSuffixes"]
        data = self.repo.get_asset_with_children(asset_id)
        parent_asset = data["parent_asset"]
        children = data["children"]
        parent_line = {}
        for key in parent_asset:
            for suffix in line_suffixes:
                if key.lower().endswith(suffix):
                    if key.lower().endswith("assetmodelid"):
                        continue
                    parent_key = "line" + suffix.capitalize()
                    parent_line[parent_key] = (
                        parent_asset[key]
                        if not parent_key.endswith("Status")
                        else parent_asset[key]["state"]
                    )
        return {"parent": parent_line, "children": children}

    def get_asset_metric_latest_value(self, event) -> dict:
        body = event["body"]
        asset_id = body["assetId"]
        allowed_suffixes = body["allowed_suffixes"].split(",")
        property_values = self.repo.get_latest_property_values(
            asset_id, allowed_suffixes
        )
        formatted_values = [
            {"name": pv["name"], "value": round(pv["value"], 2)}
            for pv in property_values
        ]
        return {prop["name"]: prop["value"] for prop in formatted_values}

    def get_asset_property_historical_values(self, event):
        body = event["body"]
        asset_response = self.repo.get_asset_details(body["assetId"])
        asset = Asset(asset_response["assetId"], asset_response["assetName"])

        start_date = datetime.strptime(body["startDate"], "%Y-%m-%d")
        end_date = datetime.strptime(body["endDate"], "%Y-%m-%d")
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())

        property_names = body["propertyNames"]
        if not property_names:
            property_names = [
                prop["name"] for prop in asset_response["assetProperties"]
            ]
        property_names_set = set(property_names)

        results = []

        for prop in asset_response["assetProperties"]:
            if prop["name"] not in property_names_set:
                continue
            query_params = QueryParams(
                asset_id=asset_response["assetId"],
                property_name=prop["name"],
                property_id=prop["id"],
                qualities=body["qualities"],
                time_ordering=body["timeOrdering"],
                start_date=start_ts,
                end_date=end_ts,
                max_results=body["maxResults"],
            )
            raw_values = self.repo.get_raw_historical_values(
                asset_id=query_params.asset_id,
                property_id=query_params.property_id,
                start_date=query_params.start_date,
                end_date=query_params.end_date,
                qualities=query_params.qualities,
                time_ordering=query_params.time_ordering,
                max_results=query_params.max_results,
            )
            result = PropertyHistoricalValues.from_query_params(asset, query_params)
            for value in raw_values:
                value_dict = value["value"]
                val_key = list(value_dict.keys())[0]

                result.values.append(
                    {
                        "timestamp": str(value["timestamp"]),
                        "formattedTime": self._get_formatted_date(
                            value["timestamp"]["timeInSeconds"]
                        ),
                        "value": round(value_dict[val_key], 2),
                    }
                )
            results.append(result.to_dict())

        return results

    def _get_formatted_date(self, date_in_seconds):
        dt = datetime.fromtimestamp(date_in_seconds)
        return dt.strftime("%Y-%m-%d %I:%M:%S %p")
