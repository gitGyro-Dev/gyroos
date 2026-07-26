from fastapi.testclient import TestClient

from app.main import app
from app.vnext.experimental_api_routes import router as experimental_router


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}
PATH = "/vnext/experimental/inspection-comparison-series-comparisons"
ROUTER_PATH = "/vnext/experimental/inspection-comparison-series-comparisons"


def payload() -> dict:
    return {
        "series_comparison_id": "series-comparison-001",
        "left_series": {
            "comparison_series_id": "series-left",
            "set_comparison_ids": ["set-cmp-001", "set-cmp-002"],
            "series_digest": "a" * 64,
        },
        "right_series": {
            "comparison_series_id": "series-right",
            "set_comparison_ids": ["set-cmp-002", "set-cmp-003"],
            "series_digest": "b" * 64,
        },
        "warnings": [],
        "comparison_metadata": {"purpose": "inspection"},
    }


def test_create_comparison_returns_request_local_report(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_series_comparison_created"] is True
    assert body["report"]["added_set_comparison_ids"] == ["set-cmp-003"]
    assert body["report"]["removed_set_comparison_ids"] == ["set-cmp-001"]
    assert body["report"]["retained_set_comparison_ids"] == ["set-cmp-002"]
    assert body["report"]["digest_changed"] is True


def test_create_comparison_rejects_same_series(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    request_body = payload()
    request_body["right_series"]["comparison_series_id"] = "series-left"

    response = client.post(PATH, headers=HEADERS, json=request_body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())
    report = response.json()["report"]

    assert "auth_state" not in report
    assert "risk_level" not in report
    assert "semantic_trend" not in report
    assert "operator_response" not in report
    assert "runtime_state" not in report
    assert "difference_object" not in report


def test_comparison_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[ROUTER_PATH] == {"POST"}
    assert f"{ROUTER_PATH}/{{series_comparison_id}}" not in registered_methods_by_path
