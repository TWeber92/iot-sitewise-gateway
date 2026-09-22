import json
from unittest.mock import patch

from src.handlers.get_child import lambda_handler


def test_returns_matching_children(mock_client):
    # arrange
    mock_client.describe_asset.side_effect = [
        # first call: parent asset
        {
            "assetId": "parent-id",
            "assetName": "Parent Line",
            "assetHierarchies": [{"id": "hierarchy-1"}],
        },
        # second call: child 1
        {"assetId": "child-1", "assetName": "ExtrusionLine_1"},
        # third call: child 2
        {"assetId": "child-2", "assetName": "ExtrusionLine_2"},
    ]

    mock_client.list_associated_assets.return_value = {
        "assetSummaries": [
            {"id": "child-1", "name": "ExtrusionLine_1"},
            {"id": "child-2", "name": "ExtrusionLine_2"},
        ]
    }

    event = {
        "httpMethod": "GET",
        "path": "/api/child/assets",
        "body": '{"parent_asset_id": "parent-id","childNames": ["ExtrusionLine_1"]}',
    }

    # act
    with patch("src.handlers.get_child.get_sitewise_client", return_value=mock_client):
        response = lambda_handler(event, {})

    # assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body) == 1
    assert body == {"ExtrusionLine_1": "child-1"}
