import json
from unittest.mock import patch

from src.handlers.get_asset_hierarchy import lambda_handler


def test_returns_parent_children_grandchildren(mock_client):
    # arrange
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

    event = {
        "assetId": "parent-id",
        "lineSuffixes": ["id", "name", "status"],
    }

    # act
    with patch(
        "src.handlers.get_asset_hierarchy.get_sitewise_client", return_value=mock_client
    ):
        response = lambda_handler(event, {})

    # assert
    body = json.loads(response)
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
