import json
from unittest.mock import patch

from src.handlers.get_asset_metric_latest_value import lambda_handler


def test_filters_properties_by_suffix(mock_client):
    # arrange
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetProperties": [
            {"id": "p1", "name": "CycleTime"},
            {"id": "p2", "name": "Throughput"},
            {"id": "p3", "name": "Temperature"},
        ],
    }

    def get_value(assetId, propertyId):
        return {"propertyValue": {"value": {"doubleValue": 12.345}}}

    mock_client.get_asset_property_value.side_effect = get_value

    event = {
        "assetId": "asset-1",
        "allowed_suffixes": "CycleTime,Throughput",
    }

    # act
    with patch(
        "src.handlers.get_asset_metric_latest_value.get_sitewise_client",
        return_value=mock_client,
    ):
        response = lambda_handler(event, {})

    # assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body == {"CycleTime": 12.35, "Throughput": 12.35}
