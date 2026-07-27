from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_sequence_comparison,
    router as experimental_router,
)
from app.vnext.inspection_comparison_sequence_comparison import (
    ExperimentalComparisonSequenceComparisonRequest,
)


PATH = "/vnext/experimental/inspection-comparison-sequence-comparisons"


def payload() -> dict:
    return {
        "sequence_comparison_id": "sequence-comparison-001",
        "left_sequence": {
            "comparison_sequence_id": "sequence-left",
            "collection_comparison_ids": ["collection-cmp-001", "collection-cmp-002"],
            "sequence_digest": "a" * 64,
        },
        "right_sequence": {
            "comparison_sequence_id": "sequence-right",
            "collection_comparison_ids": ["collection-cmp-002", "collection-cmp-003"],
            "sequence_digest": "b" * 64,
        },
        "warnings": [],
        "comparison_metadata": {"purpose": "inspection"},
    }


def test_create_comparison_returns_request_local_report() -> None:
    request = ExperimentalComparisonSequenceComparisonRequest(**payload())
    result = create_experimental_inspection_comparison_sequence_comparison(request)

    assert result.comparison_sequence_comparison_created is True
    assert result.report.added_collection_comparison_ids == ("collection-cmp-003",)
    assert result.report.removed_collection_comparison_ids == ("collection-cmp-001",)
    assert result.report.retained_collection_comparison_ids == ("collection-cmp-002",)
    assert result.report.digest_changed is True


def test_create_comparison_rejects_same_sequence() -> None:
    request_body = payload()
    request_body["right_sequence"]["comparison_sequence_id"] = "sequence-left"
    request = ExperimentalComparisonSequenceComparisonRequest(**request_body)

    response = create_experimental_inspection_comparison_sequence_comparison(request)

    assert response.status_code == 422
    assert b"GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_INVALID" in response.body


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonSequenceComparisonRequest(**payload())
    report = create_experimental_inspection_comparison_sequence_comparison(request).report
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
    assert f"{PATH}/{{sequence_comparison_id}}" not in registered_methods_by_path
