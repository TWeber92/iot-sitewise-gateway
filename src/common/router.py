import json

from src.handlers.get_asset import lambda_handler as get_asset
from src.handlers.get_child import lambda_handler as get_child
from src.handlers.get_hierarchy import lambda_handler as get_hierarchy
from src.handlers.get_property import lambda_handler as get_property
from src.handlers.admin_asset import lambda_handler as admin_asset
from src.common.auth import Auth

ROUTES = {
    "GET:/api/asset": get_asset,
    "GET:/api/child": get_child,
    "GET:/api/property": get_property,
    "GET:/api/hierarchy": get_hierarchy,
    "POST:/api/admin": admin_asset,
    "PUT:/api/admin": admin_asset,
}


def route(method: str, path: str, raw_body: str = None, headers: dict = None):
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

    if method in ["POST", "PUT", "DELETE"]:
        if not headers or not Auth.check_basic_auth(headers):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
            }
    parsed_body = json.loads(raw_body) if raw_body else {}
    event = {
        "body": parsed_body,
        "httpMethod": method,
        "path": path,
    }

    try:
        result = handler(event, {})
        return {"statusCode": result["statusCode"], "body": json.dumps(result["data"])}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": "Internal Server Error",
                    "message": str(e),
                }
            ),
        }
