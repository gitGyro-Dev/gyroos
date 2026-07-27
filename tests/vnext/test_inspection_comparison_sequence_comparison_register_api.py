import json

from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_sequence_comparison_register,
    router as experimental_router,
)
from app.vnext.inspection_comparison_sequence_comparison_register import (
    ExperimentalComparisonSequenceComparisonRegisterRequest,
)


PATH = "/vnext/experimental/inspection-comparison-sequence-comparison-registers"


def payload() -> dict:
    return {
        "comparison_register_id": "register-001",
        "comparison_references": [
            {
                "sequence_comparison_id": "sequence-comparison-001",
                "left_comparison_sequence_id": "sequence-left-001",
                "right_comparison_sequence_id": "sequence-right-001",
                "added_count": 1,
                "removed_count": 2,
                "retained_count": 3,
                "digest_changed": True,
            },
            {
                "sequence_comparison_id": "sequence-comparison-002",
                "left_comparison_sequence_id": "sequence-left-002",
                "right_comparison_sequence_id": "sequence-right-002",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 4,
                "digest_changed": False,
            },
        ],
        "warnings": [],
        "source_refs": ["source-001"],
        "register_metadata": {"purpose": "inspection"},
    }


def test_create_register_returns_request_local_manifest() -> None:
    request = ExperimentalComparisonSequenceComparisonRegisterRequest(**payload())
    result = create_experimental_inspection_comparison_sequence_comparison_register(request)

    assert result.comparison_register_created is True
    assert result.manifest.comparison_register_id == "register-001"
    assert result.manifest.comparison_count == 2
    assert len(result.manifest.comparison_references_digest) == 64


def test_create_register_rejects_duplicate_reference() -> None:
    request_body = payload()
    request_body["comparison_references"][1]["sequence_comparison_id"] = (
        "sequence-comparison-001"
    )
    request = ExperimentalComparisonSequenceComparisonRegisterRequest(**request_body)

    response = create_experimental_inspection_comparison_sequence_comparison_register(
        request
    )

    assert response.status_code == 422
    body = json.loads(response.body)
    assert body["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_REGISTER_INVALID"
    )


def test_register_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{comparison_register_id}}" not in registered_methods_by_path


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonSequenceComparisonRegisterRequest(**payload())
    manifest = create_experimental_inspection_comparison_sequence_comparison_register(
        request
    ).manifest
    fields = manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
