import json
from src.main import Main
import os


def lambda_handler(event, context):
    controller = Main(os.environ).property_controller
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "GET:/api/property/agg": lambda: controller.get_property_aggregates(event),
    }
    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return handler()
