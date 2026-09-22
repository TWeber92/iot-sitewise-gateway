import json

from src.models.line_hierarchy import Hierarchy


class HierarchyService:
    def __init__(self, client):
        self.client = client

    def _get_asset_properties(self, asset_id: str, property_names: list) -> list:
        response = self.client.describe_asset(assetId=asset_id)
        props = response["assetProperties"]

        if property_names:
            names_set = set(property_names)
            props = [p for p in props if p["name"] in names_set]

        values = []
        for prop in props:
            value_response = self.client.get_asset_property_value(
                assetId=asset_id,
                propertyId=prop["id"],
            )
            if "propertyValue" in value_response:
                raw = value_response["propertyValue"]["value"]
                for key in raw:
                    latest = raw[key]
                    values.append(
                        {
                            "propertyName": prop["name"],
                            "latestValue": (
                                latest if isinstance(latest, str) else round(latest, 2)
                            ),
                        }
                    )
            else:
                values.append({"propertyName": prop["name"], "latestValue": None})

        return values

    def build_node(self, event) -> dict:
        body = event["body"]
        if body.get("depth") is None:
            body["depth"] = Hierarchy[body["hierarchy"]].value
        parent_details = self.client.describe_asset(assetId=body["parentAssetId"])
        asset_id = parent_details["assetId"]
        asset_name = parent_details["assetName"]
        property_names = body["propertyNames"]
        depth = body["depth"]
        node = {
            "id": asset_id,
            "name": asset_name,
            "properties": self._get_asset_properties(asset_id, property_names),
            "children": [],
        }

        if depth <= 0:
            return node
        asset_details = self.client.describe_asset(assetId=asset_id)
        for hierarchy in asset_details["assetHierarchies"]:
            response = self.client.list_associated_assets(
                assetId=asset_id,
                hierarchyId=hierarchy["id"],
                traversalDirection="CHILD",
                maxResults=100,
            )
            for child_summary in response["assetSummaries"]:
                child_event = {
                    "body": {
                        "parentAssetId": child_summary["id"],
                        "propertyNames": property_names,
                        "hierarchy": body["hierarchy"],
                        "depth": depth - 1,
                    }
                }
                child_node = self.build_node(child_event)
                node["children"].append(child_node)

        return node
