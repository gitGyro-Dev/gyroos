import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_register_comparison import (
    ExperimentalComparisonRegisterComparisonReport,
    ExperimentalComparisonRegisterComparisonRequest,
    ExperimentalComparisonRegisterComparisonResult,
    ExperimentalComparisonRegisterComparisonSettings,
    ExperimentalComparisonRegisterReference,
)


def reference(register_id: str, ids: tuple[str, ...], digest: str | None = None):
    return ExperimentalComparisonRegisterReference(
        comparison_register_id=register_id,
        sequence_comparison_ids=ids,
        register_digest=digest,
    )


def test_models_are_closed_and_frozen() -> None:
    request = ExperimentalComparisonRegisterComparisonRequest(
        register_comparison_id="register-comparison-001",
        left_register=reference("register-left", ("sequence-cmp-001",)),
        right_register=reference("register-right", ("sequence-cmp-002",)),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonRequest(
            **request.model_dump(),
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        request.register_comparison_id = "changed"


def test_digest_label_requires_lowercase_sha256_hex() -> None:
    valid = reference("register-left", ("sequence-cmp-001",), "a" * 64)
    assert valid.register_digest == "a" * 64

    for invalid in ("A" * 64, "g" * 64, "a" * 63, ""):
        with pytest.raises(ValidationError):
            reference("register-left", ("sequence-cmp-001",), invalid)


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonRegisterComparisonSettings()
    assert settings.max_sequence_comparison_references_per_side == 128

    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonSettings(
            max_sequence_comparison_references_per_side=0
        )


def test_report_and_result_have_no_runtime_authentication_or_semantic_fields() -> None:
    report_fields = ExperimentalComparisonRegisterComparisonReport.model_fields
    result_fields = ExperimentalComparisonRegisterComparisonResult.model_fields

    forbidden = {
        "auth_state",
        "risk_level",
        "semantic_trend",
        "operator_response",
        "runtime_state",
        "difference_object",
        "boundary_evaluation",
        "next_action",
    }

    assert forbidden.isdisjoint(report_fields)
    assert forbidden.isdisjoint(result_fields)
