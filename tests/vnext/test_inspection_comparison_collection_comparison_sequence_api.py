import json

from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_collection_comparison_sequence,
    router as experimental_router,
)
from app.vnext.inspection_comparison_collection_comparison_sequence import (
    ExperimentalComparisonCollectionComparisonSequenceRequest,
)


PATH = "/vnext/experimental/inspection-comparison-collection-comparison-sequences"


def payload() -> dict:
    return {
        "comparison_sequence_id": "sequence-001",
        "comparison_references": [
            {
                "collection_comparison_id": "comparison-001",
                "left_comparison_collection_id": "collection-left-001",
                "right_comparison_collection_id": "collection-right-001",
                "added_count": 1,
                "removed_count": 2,
                "retained_count": 3,
                "digest_changed": True,
            },
            {
                "collection_comparison_id": "comparison-002",
                "left_comparison_collection_id": "collection-left-002",
                "right_comparison_collection_id": "collection-right-002",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 4,
                "digest_changed": False,
            },
        ],
        "warnings": [],
        "source_refs": ["source-001"],
        "sequence_metadata": {"purpose": "inspection"},
    }


def test_create_sequence_returns_request_local_manifest() -> None:
    request = ExperimentalComparisonCollectionComparisonSequenceRequest(**payload())
    result = create_experimental_inspection_comparison_collection_comparison_sequence(
        request
    )

    assert result.comparison_sequence_created is True
    assert result.manifest.comparison_sequence_id == "sequence-001"
    assert result.manifest.comparison_count == 2
    assert len(result.manifest.comparison_references_digest) == 64


def test_create_sequence_rejects_duplicate_reference() -> None:
    request_body = payload()
    request_body["comparison_references"][1]["collection_comparison_id"] = (
        "comparison-001"
    )
    request = ExperimentalComparisonCollectionComparisonSequenceRequest(**request_body)

    response = create_experimental_inspection_comparison_collection_comparison_sequence(
        request
    )

    assert response.status_code == 422
    body = json.loads(response.body)
    assert body["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_"
        "COMPARISON_SEQUENCE_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonCollectionComparisonSequenceRequest(**payload())
    manifest = (
        create_experimental_inspection_comparison_collection_comparison_sequence(request)
        .manifest
    )
    fields = manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields


def test_sequence_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{comparison_sequence_id}}" not in registered_methods_by_path
