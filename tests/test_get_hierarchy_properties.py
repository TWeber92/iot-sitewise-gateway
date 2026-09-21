import json
from unittest.mock import patch

from src.handlers.get_hierarchy_properties import lambda_handler


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

    event = {
        "body": {
            "parentAssetId": "parent-id",
            "hierarchy": "PARENT",
            "propertyNames": ["CycleTime"],
        }
    }

    # act
    with patch(
        "src.handlers.get_hierarchy_properties.get_sitewise_client",
        return_value=mock_client,
    ):
        response = lambda_handler(event, {})

    # assert
    body = json.loads(response)
    assert body["parent"]["id"] == "parent-id"
    assert body["parent"]["name"] == "Parent Line"
    assert body["parent"]["properties"] == [
        {"propertyName": "CycleTime", "latestValue": 12.35}
    ]
    assert body["parent"]["children"] == []


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

    event = {
        "body": {
            "parentAssetId": "parent-id",
            "hierarchy": "CHILD1",
            "propertyNames": ["CycleTime"],
        }
    }

    # act
    with patch(
        "src.handlers.get_hierarchy_properties.get_sitewise_client",
        return_value=mock_client,
    ):
        response = lambda_handler(event, {})

    # assert
    body = json.loads(response)
    assert body["parent"]["id"] == "parent-id"
    assert len(body["parent"]["children"]) == 1
    child = body["parent"]["children"][0]
    assert child["id"] == "child-1"
    assert child["name"] == "Child 1"
    assert child["properties"] == [{"propertyName": "CycleTime", "latestValue": 99.0}]
    assert child["children"] == []
