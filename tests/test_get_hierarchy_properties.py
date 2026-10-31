from src.repository.hierarchy_repository import HierarchyRepository
from src.service.hierarchy_service import HierarchyService
from src.controller.hierarchy_controller import HierarchyController


def test_builds_parent_only(mock_client):
    # arrange
    mock_client.describe_asset.return_value = {
        "assetId": "parent-id",
        "assetName": "Parent Line",
        "assetProperties": [{"id": "p1", "name": "CycleTime"}],
        "assetHierarchies": [{"id": "hierarchy-1"}],
    }

    mock_client.get_asset_property_value.return_value = {
        "propertyValue": {"value": {"doubleValue": 12.345}}
    }

    # build the real controller with the mock client
    repo = HierarchyRepository(mock_client)
    service = HierarchyService(repo)
    controller = HierarchyController(service)

    event = {
        "body": {
            "parentAssetId": "parent-id",
            "hierarchy": "PARENT",
            "propertyNames": ["CycleTime"],
        }
    }

    # act
    response = controller.get_hierarchy_properties(event)

    # assert
    assert response["statusCode"] == 200
    body = response["data"]
    assert body["id"] == "parent-id"
    assert body["name"] == "Parent Line"
    assert body["properties"] == [{"propertyName": "CycleTime", "latestValue": 12.35}]
    assert body["children"] == []


def test_builds_parent_with_children(mock_client):
    # arrange
    def describe_asset(assetId):
        assets = {
            "parent-id": {
                "assetId": "parent-id",
                "assetName": "Parent Line",
                "assetProperties": [{"id": "p1", "name": "CycleTime"}],
                "assetHierarchies": [{"id": "hierarchy-1"}],
            },
            "child-1": {
                "assetId": "child-1",
                "assetName": "Child 1",
                "assetProperties": [{"id": "p2", "name": "CycleTime"}],
                "assetHierarchies": [],
            },
        }
        return assets[assetId]

    mock_client.describe_asset.side_effect = describe_asset
    mock_client.get_asset_property_value.return_value = {
        "propertyValue": {"value": {"doubleValue": 99.0}}
    }
    mock_client.list_associated_assets.return_value = {
        "assetSummaries": [{"id": "child-1", "name": "Child 1"}]
    }

    repo = HierarchyRepository(mock_client)
    service = HierarchyService(repo)
    controller = HierarchyController(service)

    event = {
        "body": {
            "parentAssetId": "parent-id",
            "hierarchy": "CHILD1",
            "propertyNames": ["CycleTime"],
        }
    }

    # act
    response = controller.get_hierarchy_properties(event)

    # assert
    assert response["statusCode"] == 200
    body = response["data"]
    assert body["id"] == "parent-id"
    assert len(body["children"]) == 1
    child = body["children"][0]
    assert child["id"] == "child-1"
    assert child["name"] == "Child 1"
    assert child["properties"] == [{"propertyName": "CycleTime", "latestValue": 99.0}]
    assert child["children"] == []
