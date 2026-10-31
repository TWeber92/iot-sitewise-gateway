from src.models.line_hierarchy import Hierarchy


class HierarchyService:
    def __init__(self, repo):
        self.repo = repo

    def build_node(self, event) -> dict:
        body = event["body"]
        parent_asset_id = body["parentAssetId"]
        property_names = body.get("propertyNames", [])

        depth = body.get("depth")
        if depth is None:
            depth = Hierarchy[body["hierarchy"]].value

        return self._build_tree_recursive(parent_asset_id, property_names, depth)

    def _build_tree_recursive(
        self, asset_id: str, property_names: list, depth: int
    ) -> dict:
        asset_details = self.repo.get_asset_details(asset_id)

        node = {
            "id": asset_details["assetId"],
            "name": asset_details["assetName"],
            "properties": self.repo.get_node_properties(asset_id, property_names),
            "children": [],
        }
        if depth <= 0:
            return node

        child_ids = self.repo.get_immediate_children(asset_id)
        for child_id in child_ids:
            child_node = self._build_tree_recursive(child_id, property_names, depth - 1)
            node["children"].append(child_node)

        return node
