class AdminService:
    def __init__(self, repo):
        self.repo = repo

    def create_asset(self, event):
        body = event["body"]
        asset_id = body["id"]
        self.repo.put_asset(asset_id, body)
        return {"message": f"Asset {asset_id} created"}
