from fastapi.testclient import TestClient

from app.main import app
from app.vnext.experimental_api_routes import router as experimental_router
from app.vnext.inspection_comparison_collection_comparison import (
    ExperimentalComparisonCollectionComparisonRequest,
)
from app.vnext.inspection_comparison_collection_comparison_service import (
    ExperimentalComparisonCollectionComparisonService,
)


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}
PATH = "/vnext/experimental/inspection-comparison-collection-comparisons"


def payload() -> dict:
    return {
        "collection_comparison_id": "collection-comparison-001",
        "left_collection": {
            "comparison_collection_id": "collection-left",
            "series_comparison_ids": ["series-cmp-001", "series-cmp-002"],
            "collection_digest": "a" * 64,
        },
        "right_collection": {
            "comparison_collection_id": "collection-right",
            "series_comparison_ids": ["series-cmp-002", "series-cmp-003"],
            "collection_digest": "b" * 64,
        },
        "warnings": [],
        "comparison_metadata": {"purpose": "inspection"},
    }


def test_create_comparison_returns_request_local_report(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_collection_comparison_created"] is True
    assert body["report"]["added_series_comparison_ids"] == ["series-cmp-003"]
    assert body["report"]["removed_series_comparison_ids"] == ["series-cmp-001"]
    assert body["report"]["retained_series_comparison_ids"] == ["series-cmp-002"]
    assert body["report"]["digest_changed"] is True


def test_create_comparison_rejects_same_collection(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    request_body = payload()
    request_body["right_collection"]["comparison_collection_id"] = "collection-left"

    response = client.post(PATH, headers=HEADERS, json=request_body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonCollectionComparisonRequest(**payload())
    report = ExperimentalComparisonCollectionComparisonService().compare(request).report
    fields = report.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields


def test_comparison_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{collection_comparison_id}}" not in registered_methods_by_path
