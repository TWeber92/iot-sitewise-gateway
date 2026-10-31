class AdminRepository:
    def __init__(self, client):
        self.client = client

    def put_asset(self, asset_id, data):
        self.client.put_asset(asset_id, data)
