from src.repository.asset_repository import AssetRepository
from src.service.asset_service import AssetService
from src.controller.asset_controller import AssetController


def test_filters_properties_by_suffix(mock_client):
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetProperties": [
            {"id": "p1", "name": "CycleTime"},
            {"id": "p2", "name": "Throughput"},
            {"id": "p3", "name": "Temperature"},
        ],
    }

    mock_client.get_asset_property_value.return_value = {
        "propertyValue": {"value": {"doubleValue": 12.345}}
    }

    repo = AssetRepository(mock_client)
    service = AssetService(repo)
    controller = AssetController(service)

    event = {
        "body": {
            "assetId": "asset-1",
            "allowed_suffixes": "CycleTime,Throughput",
        }
    }

    # act
    response = controller.get_asset_metric_latest_value(event)

    # assert
    assert response["statusCode"] == 200
    assert response["data"] == {"CycleTime": 12.35, "Throughput": 12.35}
