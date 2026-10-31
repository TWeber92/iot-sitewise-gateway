from src.models.child import Child


class ChildService:
    def __init__(self, repo):
        self.repo = repo

    def get_child_assets(self, event) -> dict:
        body = event["body"]
        parent_asset_id = body["parent_asset_id"]
        child_names = set(body["childNames"])

        all_children = self.repo.get_all_children(parent_asset_id)

        child_assets = []
        for child_data in all_children:
            if child_data["name"] in child_names:
                child = Child(child_data["id"], child_data["name"])
                child_assets.append(child.to_dict())

        return {child["name"]: child["id"] for child in child_assets}
