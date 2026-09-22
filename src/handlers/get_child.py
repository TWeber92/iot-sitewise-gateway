import json

from src.service.child_service import ChildService
from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset


def lambda_handler(event, context):
    client = get_sitewise_client()
    event["body"] = json.loads(event["body"])
    service = ChildService(client)
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "GET:/api/child/assets": lambda: service.get_child_assets(event),
    }

    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return {"statusCode": 200, "body": json.dumps(handler())}
