import json
from src.service.asset_service import AssetService
from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset


def lambda_handler(event, context):
    client = get_sitewise_client()
    event["body"] = json.loads(event["body"])
    service = AssetService(client)
    method = event["httpMethod"]
    path = event["path"]

    ROUTES = {
        "GET:/api/asset/hierarchy": lambda: service.get_asset_hierarchy(event),
        "GET:/api/asset/metric/lat-val": lambda: service.get_asset_metric_latest_value(
            event
        ),
        "GET:/api/asset/prop/hist/val": lambda: service.get_asset_property_historical_values(
            event
        ),
    }

    handler = ROUTES.get(f"{method}:{path}")
    if handler is None:
        raise ValueError(f"No handler for {method}:{path}")

    return {"statusCode": 200, "body": json.dumps(handler())}
