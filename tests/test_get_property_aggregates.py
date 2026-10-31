import json
from src.repository.property_repository import PropertyRepository
from src.service.property_service import PropertyService
from src.controller.property_controller import PropertyController


def test_returns_aggregates_for_matching_properties(mock_client):
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetProperties": [
            {"id": "p1", "name": "Runtime"},
            {"id": "p2", "name": "Downtime"},
            {"id": "p3", "name": "Temperature"},
        ],
    }

    mock_client.get_asset_property_value.return_value = {
        "propertyValue": {"value": {"doubleValue": 100.0}}
    }

    def get_aggregates(
        assetId, propertyId, aggregateTypes, resolution, startDate, endDate, maxResults
    ):
        return {"aggregatedValues": [{"value": {aggregateTypes[0]: 42.5}}]}

    mock_client.get_asset_property_aggregates.side_effect = get_aggregates

    repo = PropertyRepository(mock_client)
    service = PropertyService(repo)
    controller = PropertyController(service)

    event = {
        "body": {
            "assetId": "asset-1",
            "startTime": "2023-03-01",
            "endTime": "2023-03-03",
            "interval": "1m",
            "aggregateTypes": ["SUM"],
            "propertiesNeeded": ["Runtime", "Downtime"],
        }
    }

    # 4. Act
    response = controller.get_property_aggregates(event)

    # 5. Assert
    assert response["statusCode"] == 200
    assert response["data"] == {
        "Runtime": {"SUM": 42.5},
        "Downtime": {"SUM": 42.5},
    }
