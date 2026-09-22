import json

from src.handlers.get_asset import lambda_handler as get_asset
from src.handlers.get_child import lambda_handler as get_child
from src.handlers.get_hierarchy import lambda_handler as get_hierarchy
from src.handlers.get_property import lambda_handler as get_property

ROUTES = {
    "GET:/api/asset": get_asset,
    "GET:/api/child": get_child,
    "GET:/api/property": get_property,
    "GET:/api/hierarchy": get_hierarchy,
}


def route(method: str, path: str, raw_body: str = None):
    """Dispatch an HTTP-like request to the matching Lambda handler.

    Returns a dict shaped like a Lambda response: {"statusCode": int, "body": str}.
    """
    parts = path.strip("/").split("/")[:2]  # ['api', 'asset']
    key = f"{method}:/{'/'.join(parts)}"  # 'GET:/api/asset'
    handler = ROUTES.get(key)
    if handler is None:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"No route for {method} {path}"}),
        }

    event = {
        "body": raw_body,
        "httpMethod": method,
        "path": path,  # full path, for the second stage
    }

    try:
        return handler(event, {})
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
