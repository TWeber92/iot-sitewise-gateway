from datetime import datetime
from src.models.property_historical_values import PropertyHistoricalValues
from src.models.asset import Asset
from src.models.query_params import QueryParams
from src.models.child import Child


class AssetService:
    def __init__(self, client):
        self.client = client

    def get_asset_hierarchy(self, event) -> dict:
        body = event["body"]
        asset = Asset(body["assetId"])
        line_suffixes = body["lineSuffixes"]
        parent_line = {}
        children = []

        parent_asset = self.client.describe_asset(assetId=asset.asset_id)
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

        for hierarchy in parent_asset["assetHierarchies"]:
            response = self.client.list_associated_assets(
                assetId=asset.asset_id,
                hierarchyId=hierarchy["id"],
                traversalDirection="CHILD",
                maxResults=25,
            )
            for asset_summary in response["assetSummaries"]:
                child_asset = self.client.describe_asset(assetId=asset_summary["id"])
                child = Child(asset_summary["id"], child_asset["assetName"])
                grandchildren = []
                for h in child_asset["assetHierarchies"]:
                    gchild = Child(h["id"], h["name"])
                    grandchildren.append(gchild.to_dict())
                children.append(
                    {"child": child.to_dict(), "grandchildren": grandchildren}
                )
        return {"parent": parent_line, "children": children}

    def get_asset_metric_latest_value(self, event) -> list:
        body = event["body"]
        asset = Asset(body["assetId"])
        allowed_suffixes = body["allowed_suffixes"].split(",")
        asset_details = self.client.describe_asset(assetId=asset.asset_id)

        property_values = []
        for prop in asset_details["assetProperties"]:
            if not any(prop["name"].endswith(suffix) for suffix in allowed_suffixes):
                continue

            response = self.client.get_asset_property_value(
                assetId=asset.asset_id, propertyId=prop["id"]
            )
            for value_key in response["propertyValue"]["value"]:
                latest_value = response["propertyValue"]["value"][value_key]
                property_values.append(
                    {"name": prop["name"], "value": round(latest_value, 2)}
                )
        return {prop["name"]: prop["value"] for prop in property_values}

    def get_asset_property_historical_values(self, event):
        body = event["body"]
        asset_response = self.client.describe_asset(assetId=body["assetId"])
        asset = Asset(asset_response["assetId"], asset_response["assetName"])

        start_date = datetime.strptime(body["startDate"], "%Y-%m-%d")
        end_date = datetime.strptime(body["endDate"], "%Y-%m-%d")

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
                start_date=int(start_date.timestamp()),
                end_date=int(end_date.timestamp()),
                max_results=body["maxResults"],
            )
            results.append(self._get_asset_historical_values(asset, query_params))
        return results

    def _get_formatted_date(self, date_in_seconds):
        dt = datetime.fromtimestamp(date_in_seconds)
        return dt.strftime("%Y-%m-%d %I:%M:%S %p")

    def _get_asset_historical_values(
        self, asset: Asset, query_params: QueryParams
    ) -> dict:
        result = PropertyHistoricalValues.from_query_params(asset, query_params)

        paginator = self.client.get_paginator("get_asset_property_value_history")
        page_iterator = paginator.paginate(
            assetId=query_params.asset_id,
            propertyId=query_params.property_id,
            startDate=query_params.start_date,
            endDate=query_params.end_date,
            qualities=query_params.qualities,
            timeOrdering=query_params.time_ordering,
            PaginationConfig={"MaxItems": query_params.max_results, "PageSize": 250},
        )

        for page in page_iterator:
            for value in page["assetPropertyValueHistory"]:
                for key in value["value"].keys():
                    result.values.append(
                        {
                            "timestamp": str(value["timestamp"]),
                            "formattedTime": self._get_formatted_date(
                                value["timestamp"]["timeInSeconds"]
                            ),
                            "value": round(value["value"][key], 2),
                        }
                    )

        return result.to_dict()
