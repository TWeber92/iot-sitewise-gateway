class HierarchyRepository:
    def __init__(self, client):
        self.client = client

    def get_node_properties(self, asset_id: str, property_names: list) -> list:
        response = self.client.describe_asset(assetId=asset_id)
        props = response.get("assetProperties", [])

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

    def get_immediate_children(self, asset_id: str) -> list:
        asset_details = self.client.describe_asset(assetId=asset_id)
        children = []

        for hierarchy in asset_details.get("assetHierarchies", []):
            response = self.client.list_associated_assets(
                assetId=asset_id,
                hierarchyId=hierarchy["id"],
                traversalDirection="CHILD",
                maxResults=100,
            )
            for child_summary in response.get("assetSummaries", []):
                children.append(child_summary["id"])

        return children

    def get_asset_details(self, asset_id: str) -> dict:
        return self.client.describe_asset(assetId=asset_id)
