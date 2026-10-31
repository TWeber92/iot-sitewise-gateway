class AdminController:
    def __init__(self, service):
        self.service = service

    def create_asset(self, event):
        data = self.service.create_asset(event)
        return {"statusCode": 201, "data": data}
