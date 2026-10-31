class AssetController:
    def __init__(self, service):
        self.service = service

    def get_asset_hierarchy(self, event):
        data = self.service.get_asset_hierarchy(event)
        return {"statusCode": 200, "data": data}

    def get_asset_metric_latest_value(self, event):
        data = self.service.get_asset_metric_latest_value(event)
        return {"statusCode": 200, "data": data}

    def get_asset_property_historical_values(self, event):
        data = self.service.get_asset_property_historical_values(event)
        return {"statusCode": 200, "data": data}
