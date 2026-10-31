class ChildRepository:
    def __init__(self, client):
        self.client = client

    def get_all_children(self, parent_asset_id: str, max_results: int = 100) -> list:
        children = []
        parent_details = self.client.describe_asset(assetId=parent_asset_id)

        for hierarchy in parent_details.get("assetHierarchies", []):
            response = self.client.list_associated_assets(
                assetId=parent_asset_id,
                hierarchyId=hierarchy["id"],
                traversalDirection="CHILD",
                maxResults=max_results,
            )
            for asset_summary in response.get("assetSummaries", []):
                child_details = self.client.describe_asset(assetId=asset_summary["id"])
                children.append(
                    {"id": child_details["assetId"], "name": child_details["assetName"]}
                )

        return children
