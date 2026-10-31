class HierarchyController:
    def __init__(self, service):
        self.service = service

    def get_hierarchy_properties(self, event):
        data = self.service.build_node(event)
        return {"statusCode": 200, "data": data}
