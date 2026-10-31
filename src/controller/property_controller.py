class PropertyController:
    def __init__(self, service):
        self.service = service

    def get_property_aggregates(self, event):
        data = self.service.get_property_aggregates(event)
        return {"statusCode": 200, "data": data}
