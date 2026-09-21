import json
from unittest.mock import patch, MagicMock

from src.common.router import route


def test_unknown_route_returns_404():
    result = route("GET", "/api/nope")
    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "No route for GET /api/nope" in body["error"]


def test_routes_get_children_to_handler():
    fake_response = {"statusCode": 200, "body": json.dumps({"fake": "response"})}

    with patch("src.common.router.ROUTES") as mock_routes:
        mock_routes.get.return_value = MagicMock(return_value=fake_response)
        result = route("GET", "/api/children", json.dumps({"parent_asset_id": "x"}))

    assert result == fake_response


def test_parses_json_body_before_dispatch():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {"statusCode": 200, "body": "{}"}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/children": fake_handler}):
        route(
            "GET",
            "/api/children",
            json.dumps({"parent_asset_id": "abc", "childNames": ["X"]}),
        )

    assert captured_event["body"] == {"parent_asset_id": "abc", "childNames": ["X"]}


def test_empty_body_becomes_empty_dict():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {"statusCode": 200, "body": "{}"}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/children": fake_handler}):
        route("GET", "/api/children")

    assert captured_event["body"] == {}


def test_handler_exception_returns_500():
    def broken_handler(event, context):
        raise ValueError("boom")

    with patch.dict("src.common.router.ROUTES", {"GET:/api/children": broken_handler}):
        result = route("GET", "/api/children", json.dumps({}))

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "boom" in body["error"]
