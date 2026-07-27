from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_sequence_comparison_register import (
    ExperimentalComparisonSequenceComparisonReference,
    ExperimentalComparisonSequenceComparisonRegisterDigestPolicy,
    ExperimentalComparisonSequenceComparisonRegisterRequest,
    ExperimentalComparisonSequenceComparisonRegisterSettings,
    digest_comparison_references,
)


def reference(identifier: str) -> ExperimentalComparisonSequenceComparisonReference:
    return ExperimentalComparisonSequenceComparisonReference(
        sequence_comparison_id=identifier,
        left_comparison_sequence_id=f"{identifier}-left",
        right_comparison_sequence_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_register_models_are_closed_and_frozen() -> None:
    request = ExperimentalComparisonSequenceComparisonRegisterRequest(
        comparison_register_id="register-001",
        comparison_references=(reference("comparison-001"),),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceComparisonRegisterRequest(
            comparison_register_id="register-001",
            comparison_references=(reference("comparison-001"),),
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        request.comparison_register_id = "changed"


def test_digest_is_deterministic() -> None:
    references = (reference("comparison-001"), reference("comparison-002"))
    policy = ExperimentalComparisonSequenceComparisonRegisterDigestPolicy()

    assert digest_comparison_references(references, policy) == digest_comparison_references(
        references, policy
    )


def test_digest_is_order_sensitive() -> None:
    first = reference("comparison-001")
    second = reference("comparison-002")
    policy = ExperimentalComparisonSequenceComparisonRegisterDigestPolicy()

    assert digest_comparison_references((first, second), policy) != digest_comparison_references(
        (second, first), policy
    )


def test_settings_are_bounded() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceComparisonRegisterSettings(max_comparison_count=0)

    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceComparisonRegisterSettings(max_identifier_length=0)


def test_reference_has_no_runtime_authentication_or_semantic_fields() -> None:
    fields = ExperimentalComparisonSequenceComparisonReference.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
