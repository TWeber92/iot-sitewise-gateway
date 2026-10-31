from src.repository.asset_repository import AssetRepository
from src.service.asset_service import AssetService
from src.controller.asset_controller import AssetController


def test_returns_parent_children_grandchildren(mock_client):
    def describe_asset(assetId):
        assets = {
            "parent-id": {
                "assetId": "parent-id",
                "assetName": "Parent Line",
                "lineId": "line-1",
                "lineName": "Line 1",
                "lineStatus": {"state": "ACTIVE"},
                "assetHierarchies": [{"id": "hierarchy-1"}],
            },
            "child-1": {
                "assetId": "child-1",
                "assetName": "Child 1",
                "assetHierarchies": [
                    {"id": "gc-1", "name": "Grandchild 1"},
                    {"id": "gc-2", "name": "Grandchild 2"},
                ],
            },
        }
        return assets[assetId]

    mock_client.describe_asset.side_effect = describe_asset
    mock_client.list_associated_assets.return_value = {
        "assetSummaries": [{"id": "child-1", "name": "Child 1"}]
    }

    repo = AssetRepository(mock_client)
    service = AssetService(repo)
    controller = AssetController(service)

    event = {
        "body": {
            "assetId": "parent-id",
            "lineSuffixes": ["id", "name", "status"],
        }
    }

    # act
    response = controller.get_asset_hierarchy(event)

    # assert
    assert response["statusCode"] == 200
    body = response["data"]

    assert "parent" in body
    assert "children" in body

    parent = body["parent"]
    assert parent["lineId"] == "line-1"
    assert parent["lineName"] == "Line 1"
    assert parent["lineStatus"] == "ACTIVE"

    assert len(body["children"]) == 1
    child = body["children"][0]
    assert child["child"] == {"id": "child-1", "name": "Child 1"}
    assert len(child["grandchildren"]) == 2
    assert child["grandchildren"][0] == {"id": "gc-1", "name": "Grandchild 1"}
    assert child["grandchildren"][1] == {"id": "gc-2", "name": "Grandchild 2"}
