class ChildController:
    def __init__(self, service):
        self.service = service

    def get_child_assets(self, event):
        data = self.service.get_child_assets(event)
        return {"statusCode": 200, "data": data}
