import json
from unittest.mock import patch

from src.handlers.get_asset_property_historical_values import lambda_handler


def test_returns_historical_values_for_property(mock_client):
    # arrange
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetName": "Line 1",
        "assetProperties": [
            {"id": "p1", "name": "CycleTime"},
        ],
    }

    mock_client.get_paginator.return_value.paginate.return_value = [
        {
            "assetPropertyValueHistory": [
                {
                    "timestamp": {"timeInSeconds": 1677628800, "offsetInNanos": 0},
                    "value": {"doubleValue": 12.345},
                },
                {
                    "timestamp": {"timeInSeconds": 1677632400, "offsetInNanos": 0},
                    "value": {"doubleValue": 67.891},
                },
            ]
        }
    ]

    event = {
        "body": {
            "assetId": "asset-1",
            "startDate": "2023-03-01",
            "endDate": "2023-03-03",
            "qualities": ["GOOD"],
            "timeOrdering": "ASCENDING",
            "maxResults": 10,
            "propertyNames": ["CycleTime"],
        }
    }

    # act
    with patch(
        "src.handlers.get_asset_property_historical_values.get_sitewise_client",
        return_value=mock_client,
    ):
        response = lambda_handler(event, {})

    # assert
    assert response["statusCode"] == 200
    body = response["body"]
    assert len(body) == 1

    result = json.loads(body[0])
    assert result["propertyName"] == "CycleTime"
    assert result["propertyId"] == "p1"
    assert len(result["values"]) == 2
    assert result["values"][0]["value"] == 12.35
    assert result["values"][1]["value"] == 67.89
