import json
from unittest.mock import patch

from src.handlers.get_property import lambda_handler


def test_returns_aggregates_for_matching_properties(mock_client):
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetProperties": [
            {"id": "p1", "name": "Runtime"},
            {"id": "p2", "name": "Downtime"},
            {"id": "p3", "name": "Temperature"},
        ],
    }

    # every property returns a numeric value (no stringValue)
    mock_client.get_asset_property_value.return_value = {
        "propertyValue": {"value": {"doubleValue": 100.0}}
    }

    def get_aggregates(
        assetId, propertyId, aggregateTypes, resolution, startDate, endDate, maxResults
    ):
        return {"aggregatedValues": [{"value": {aggregateTypes[0]: 42.5}}]}

    mock_client.get_asset_property_aggregates.side_effect = get_aggregates

    event = {
        "httpMethod": "GET",
        "path": "/api/property/agg",
        "body": """{
            "assetId": "asset-1",
            "startTime": "2023-03-01",
            "endTime": "2023-03-03",
            "interval": "1m",
            "aggregateTypes": ["SUM"],
            "propertiesNeeded": ["Runtime", "Downtime"]
        }""",
    }

    with patch(
        "src.handlers.get_property.get_sitewise_client",
        return_value=mock_client,
    ):
        response = lambda_handler(event, {})

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body == {
        "Runtime": {"SUM": 42.5},
        "Downtime": {"SUM": 42.5},
    }
