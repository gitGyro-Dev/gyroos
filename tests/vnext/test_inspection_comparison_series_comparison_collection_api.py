from fastapi.testclient import TestClient

from app.main import app
from app.vnext.experimental_api_routes import router as experimental_router
from app.vnext.inspection_comparison_series_comparison_collection import (
    ExperimentalComparisonSeriesComparisonCollectionRequest,
)
from app.vnext.inspection_comparison_series_comparison_collection_service import (
    ExperimentalComparisonSeriesComparisonCollectionService,
)


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}
PATH = "/vnext/experimental/inspection-comparison-series-comparison-collections"


def payload() -> dict:
    return {
        "comparison_collection_id": "collection-001",
        "comparison_references": [
            {
                "series_comparison_id": "series-comparison-001",
                "left_comparison_series_id": "series-left-001",
                "right_comparison_series_id": "series-right-001",
                "added_count": 1,
                "removed_count": 2,
                "retained_count": 3,
                "digest_changed": True,
            },
            {
                "series_comparison_id": "series-comparison-002",
                "left_comparison_series_id": "series-left-002",
                "right_comparison_series_id": "series-right-002",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 4,
                "digest_changed": False,
            },
        ],
        "warnings": [],
        "source_refs": ["source-001"],
        "collection_metadata": {"purpose": "inspection"},
    }


def test_create_collection_returns_request_local_manifest(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_collection_created"] is True
    assert body["manifest"]["comparison_collection_id"] == "collection-001"
    assert body["manifest"]["comparison_count"] == 2
    assert len(body["manifest"]["comparison_references_digest"]) == 64


def test_create_collection_rejects_duplicate_reference(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    request_body = payload()
    request_body["comparison_references"][1]["series_comparison_id"] = (
        "series-comparison-001"
    )

    response = client.post(PATH, headers=HEADERS, json=request_body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_COLLECTION_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonSeriesComparisonCollectionRequest.model_validate(payload())
    result = ExperimentalComparisonSeriesComparisonCollectionService().create_collection(request)
    manifest = result.manifest.model_dump(mode="json")

    assert "auth_state" not in manifest
    assert "risk_level" not in manifest
    assert "semantic_trend" not in manifest
    assert "operator_response" not in manifest
    assert "runtime_state" not in manifest
    assert "difference_object" not in manifest


def test_collection_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{comparison_collection_id}}" not in registered_methods_by_path
