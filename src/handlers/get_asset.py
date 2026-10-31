import json
from src.main import Main
import os


def lambda_handler(event, context):
    controller = Main(os.environ).asset_controller
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "GET:/api/asset/hierarchy": lambda: controller.get_asset_hierarchy(event),
        "GET:/api/asset/metric/lat-val": lambda: controller.get_asset_metric_latest_value(
            event
        ),
        "GET:/api/asset/prop/hist/val": lambda: controller.get_asset_property_historical_values(
            event
        ),
    }

    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return handler()
