import json

from src.service.property_service import PropertyService
from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset


def lambda_handler(event, context):
    client = get_sitewise_client()
    event["body"] = json.loads(event["body"])
    service = PropertyService(client)
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "GET:/api/property/agg": lambda: service.get_property_aggregates(event),
    }
    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return {"statusCode": 200, "body": json.dumps(handler())}
