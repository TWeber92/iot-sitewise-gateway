from src.repository.child_repository import ChildRepository
from src.service.child_service import ChildService
from src.controller.child_controller import ChildController


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

    repo = ChildRepository(mock_client)
    service = ChildService(repo)
    controller = ChildController(service)

    event = {
        "body": {"parent_asset_id": "parent-id", "childNames": ["ExtrusionLine_1"]}
    }

    # act
    response = controller.get_child_assets(event)

    # assert
    assert response["statusCode"] == 200
    assert response["data"] == {"ExtrusionLine_1": "child-1"}
