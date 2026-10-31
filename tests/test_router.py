import json
from unittest.mock import patch, MagicMock
from src.common.router import route

# Note: Assuming the Logger is setup somewhere globally in tests, or we patch it.
# If you get errors about Logger not being configured, you can add:
# from src.common.logger import Logger
# Logger.setup_default_logger()


def test_unknown_route_returns_404():
    result = route("GET", "/api/nope")
    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "No route for GET /api/nope" in body["error"]


def test_routes_get_child_to_handler():
    fake_controller_response = {"statusCode": 200, "data": {"fake": "response"}}

    with patch.dict(
        "src.common.router.ROUTES",
        {"GET:/api/child": MagicMock(return_value=fake_controller_response)},
    ):
        result = route("GET", "/api/child/x", json.dumps({"parent_asset_id": "x"}))

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"fake": "response"}


def test_passes_body_through_as_string():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": fake_handler}):
        raw = json.dumps({"parent_asset_id": "abc", "childNames": ["X"]})
        route("GET", "/api/child/x", raw)

    assert captured_event["body"] == {"parent_asset_id": "abc", "childNames": ["X"]}


def test_empty_body_passes_as_none():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": fake_handler}):
        route("GET", "/api/child/x")

    assert captured_event["body"] == {}


def test_handler_exception_returns_500():
    def broken_handler(event, context):
        raise ValueError("boom")

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": broken_handler}):
        result = route("GET", "/api/child/x", json.dumps({}))

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "boom" in body["message"]
