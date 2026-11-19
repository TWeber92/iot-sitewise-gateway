from src.repository.asset_repository import AssetRepository
from src.service.asset_service import AssetService
from src.controller.asset_controller import AssetController

from src.common.mock_sitewise_client import MockSiteWiseClient


def _point(ts, value, quality="GOOD"):
    return {
        "timestamp": {"timeInSeconds": ts, "offsetInNanos": 0},
        "value": {"doubleValue": value},
        "quality": quality,
    }


def _repo_args(**overrides):
    args = dict(
        asset_id="asset-1",
        property_id="p1",
        start_date=0,
        end_date=2_000_000_000,
        qualities=["GOOD"],
        time_ordering="ASCENDING",
        max_results=10,
    )
    args.update(overrides)
    return args


# ---------------------------------------------------------------
# 1. Original test, stubbed for the nextToken loop
# ---------------------------------------------------------------
def test_returns_historical_values_for_property(mock_client):
    # arrange
    mock_client.describe_asset.return_value = {
        "assetId": "asset-1",
        "assetName": "Line 1",
        "assetProperties": [{"id": "p1", "name": "CycleTime"}],
    }

    # Plain dict, no nextToken: a MagicMock here would loop forever.
    mock_client.get_asset_property_value_history.return_value = {
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


# ---------------------------------------------------------------
# 2. Repository follows nextToken across pages
# ---------------------------------------------------------------
def test_repository_follows_next_token(mock_client):
    mock_client.get_asset_property_value_history.side_effect = [
        {
            "assetPropertyValueHistory": [_point(1, 1.0), _point(2, 2.0)],
            "nextToken": "tok-2",
        },
        {"assetPropertyValueHistory": [_point(3, 3.0)]},  # no token: last page
    ]

    repo = AssetRepository(mock_client)
    values = repo.get_raw_historical_values(**_repo_args())

    assert [v["value"]["doubleValue"] for v in values] == [1.0, 2.0, 3.0]
    calls = mock_client.get_asset_property_value_history.call_args_list
    assert len(calls) == 2
    assert "nextToken" not in calls[0].kwargs
    assert calls[1].kwargs["nextToken"] == "tok-2"


# ---------------------------------------------------------------
# 3. Repository never returns more than max_results
# ---------------------------------------------------------------
def test_repository_respects_max_results(mock_client):
    mock_client.get_asset_property_value_history.side_effect = [
        {
            "assetPropertyValueHistory": [_point(1, 1.0), _point(2, 2.0)],
            "nextToken": "tok-2",
        },
        {
            "assetPropertyValueHistory": [_point(3, 3.0), _point(4, 4.0)],
            "nextToken": "tok-3",
        },
    ]

    repo = AssetRepository(mock_client)
    values = repo.get_raw_historical_values(**_repo_args(max_results=3))

    assert len(values) == 3


# ---------------------------------------------------------------
# 4. Repository + real MockSiteWiseClient: filtering and paging together
# ---------------------------------------------------------------
class FakeOort:
    """Stands in for the OORT client; serves one asset from memory."""

    def __init__(self, asset):
        self.asset = asset

    def get_json(self, key):
        return self.asset


def _seeded_asset():
    day = 86400
    t0 = 1735689600 + 12 * 3600  # 2025-01-01 12:00 UTC
    history = [
        _point(t0 + i * day, float(i), "BAD" if i % 5 == 4 else "GOOD")
        for i in range(10)  # 10 points, 2 BAD, 8 GOOD
    ]
    return {
        "id": "asset-1",
        "name": "Extruder A",
        "status": "ACTIVE",
        "properties": {"Temp": 200.0},
        "hierarchies": [],
        "children": [],
        "history": {"Temp": history},
        "aggregates": {},
    }


def test_repository_with_mock_client_filters_quality_and_pages():
    client = MockSiteWiseClient(FakeOort(_seeded_asset()))
    repo = AssetRepository(client)

    start = 1735689600  # 2025-01-01 00:00 UTC
    end = start + 30 * 86400

    all_good = repo.get_raw_historical_values(
        **_repo_args(
            property_id="Temp-id", start_date=start, end_date=end, max_results=100
        )
    )
    assert len(all_good) == 8  # 10 points minus 2 BAD
    assert all(v["quality"] == "GOOD" for v in all_good)

    # mock pages are 3 items, so 8 results proves the loop crossed pages
    capped = repo.get_raw_historical_values(
        **_repo_args(
            property_id="Temp-id", start_date=start, end_date=end, max_results=5
        )
    )
    assert len(capped) == 5
