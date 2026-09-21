import json

from src.handlers.get_asset_hierarchy import lambda_handler as get_asset_hierarchy
from src.handlers.get_asset_metric_latest_value import (
    lambda_handler as get_asset_metric_latest_value,
)
from src.handlers.get_asset_property_historical_values import (
    lambda_handler as get_asset_property_historical_values,
)
from src.handlers.get_child_assets import lambda_handler as get_child_assets
from src.handlers.get_hierarchy_properties import (
    lambda_handler as get_hierarchy_properties,
)
from src.handlers.get_property_aggregates import (
    lambda_handler as get_property_aggregates,
)

ROUTES = {
    "GET:/api/hierarchy": get_asset_hierarchy,
    "GET:/api/children": get_child_assets,
    "GET:/api/properties": get_hierarchy_properties,
    "GET:/api/latest": get_asset_metric_latest_value,
    "POST:/api/aggregates": get_property_aggregates,
    "POST:/api/historical": get_asset_property_historical_values,
}


def route(method: str, path: str, raw_body: str = None):
    """Dispatch an HTTP-like request to the matching Lambda handler.

    Returns a dict shaped like a Lambda response: {"statusCode": int, "body": str}.
    """
    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"No route for {method} {path}"}),
        }

    body = json.loads(raw_body) if raw_body else {}
    event = {"body": body}

    try:
        return handler(event, {})
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
