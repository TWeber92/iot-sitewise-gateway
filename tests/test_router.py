import json
from unittest.mock import patch, MagicMock

from src.common.router import route


def test_unknown_route_returns_404():
    result = route("GET", "/api/nope")
    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "No route for GET /api/nope" in body["error"]


def test_routes_get_child_to_handler():
    fake_response = {"statusCode": 200, "body": json.dumps({"fake": "response"})}

    with patch.dict(
        "src.common.router.ROUTES",
        {"GET:/api/child": MagicMock(return_value=fake_response)},
    ):
        result = route("GET", "/api/child/x", json.dumps({"parent_asset_id": "x"}))

    assert result == fake_response


def test_passes_body_through_as_string():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {"statusCode": 200, "body": "{}"}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": fake_handler}):
        raw = json.dumps({"parent_asset_id": "abc", "childNames": ["X"]})
        route("GET", "/api/child/x", raw)

    assert captured_event["body"] == raw  # still a string — router doesn't parse


def test_empty_body_passes_as_none():
    captured_event = {}

    def fake_handler(event, context):
        captured_event.update(event)
        return {"statusCode": 200, "body": "{}"}

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": fake_handler}):
        route("GET", "/api/child/x")

    assert captured_event["body"] is None  # no body → None, matching API Gateway


def test_handler_exception_returns_500():
    def broken_handler(event, context):
        raise ValueError("boom")

    with patch.dict("src.common.router.ROUTES", {"GET:/api/child": broken_handler}):
        result = route("GET", "/api/child/x", json.dumps({}))

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "boom" in body["error"]
