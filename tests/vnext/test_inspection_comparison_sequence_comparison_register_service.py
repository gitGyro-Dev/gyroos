from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_sequence_comparison_register import (
    ExperimentalComparisonSequenceComparisonReference,
    ExperimentalComparisonSequenceComparisonRegisterRequest,
    ExperimentalComparisonSequenceComparisonRegisterSettings,
)
from app.vnext.inspection_comparison_sequence_comparison_register_service import (
    ExperimentalComparisonSequenceComparisonRegisterDuplicateError,
    ExperimentalComparisonSequenceComparisonRegisterResourceLimitError,
    ExperimentalComparisonSequenceComparisonRegisterService,
)


def reference(identifier: str) -> ExperimentalComparisonSequenceComparisonReference:
    return ExperimentalComparisonSequenceComparisonReference(
        sequence_comparison_id=identifier,
        left_comparison_sequence_id=f"{identifier}-left",
        right_comparison_sequence_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=False,
    )


def request_with(*identifiers: str) -> ExperimentalComparisonSequenceComparisonRegisterRequest:
    return ExperimentalComparisonSequenceComparisonRegisterRequest(
        comparison_register_id="register-001",
        comparison_references=tuple(reference(identifier) for identifier in identifiers),
        source_refs=("source-001",),
        register_metadata={"purpose": "inspection"},
    )


def test_service_creates_request_local_register_in_request_order() -> None:
    result = ExperimentalComparisonSequenceComparisonRegisterService().create_register(
        request_with("comparison-002", "comparison-001")
    )

    assert result.comparison_register_created is True
    assert result.manifest.comparison_register_id == "register-001"
    assert [
        item.sequence_comparison_id for item in result.manifest.comparison_references
    ] == ["comparison-002", "comparison-001"]
    assert result.manifest.comparison_count == 2
    assert len(result.manifest.comparison_references_digest) == 64


def test_service_rejects_duplicate_sequence_comparison_id() -> None:
    with pytest.raises(ExperimentalComparisonSequenceComparisonRegisterDuplicateError):
        ExperimentalComparisonSequenceComparisonRegisterService().create_register(
            request_with("comparison-001", "comparison-001")
        )


def test_service_enforces_reference_limit() -> None:
    service = ExperimentalComparisonSequenceComparisonRegisterService(
        ExperimentalComparisonSequenceComparisonRegisterSettings(max_comparison_count=1)
    )

    with pytest.raises(
        ExperimentalComparisonSequenceComparisonRegisterResourceLimitError
    ):
        service.create_register(request_with("comparison-001", "comparison-002"))


def test_service_enforces_metadata_limit() -> None:
    service = ExperimentalComparisonSequenceComparisonRegisterService(
        ExperimentalComparisonSequenceComparisonRegisterSettings(max_metadata_bytes=2)
    )

    with pytest.raises(
        ExperimentalComparisonSequenceComparisonRegisterResourceLimitError
    ):
        service.create_register(request_with("comparison-001"))


def test_request_requires_non_empty_reference_set() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceComparisonRegisterRequest(
            comparison_register_id="register-001",
            comparison_references=(),
        )


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    manifest = ExperimentalComparisonSequenceComparisonRegisterService().create_register(
        request_with("comparison-001")
    ).manifest
    fields = manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
