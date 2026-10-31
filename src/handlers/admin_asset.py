import json
from src.main import Main
import os


def lambda_handler(event, context):
    controller = Main(os.environ).admin_controller
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "POST:/api/admin/asset": lambda: controller.create_asset(event),
        "PUT:/api/admin/asset": lambda: controller.update_asset(event),
    }

    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return handler()
