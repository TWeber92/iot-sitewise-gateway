from src.repository.asset_repository import AssetRepository
from src.service.asset_service import AssetService
from src.controller.asset_controller import AssetController


def test_returns_historical_values_for_property(mock_client):
    # arrange
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetName": "Line 1",
        "assetProperties": [{"id": "p1", "name": "CycleTime"}],
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

    repo = AssetRepository(mock_client)
    service = AssetService(repo)
    controller = AssetController(service)

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
    response = controller.get_asset_property_historical_values(event)

    # assert
    assert response["statusCode"] == 200
    result = response["data"]
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["propertyName"] == "CycleTime"
    assert result[0]["propertyId"] == "p1"
    assert len(result[0]["values"]) == 2
    assert result[0]["values"][0]["value"] == 12.35
    assert result[0]["values"][1]["value"] == 67.89
