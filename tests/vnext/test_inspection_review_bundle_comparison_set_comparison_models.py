import pytest
from pydantic import ValidationError

from app.vnext.inspection_review_bundle_comparison_set_comparison import (
    ExperimentalComparisonSetComparisonReport,
    ExperimentalComparisonSetComparisonRequest,
    ExperimentalComparisonSetComparisonResult,
    ExperimentalComparisonSetComparisonSettings,
    ExperimentalComparisonSetReference,
    utc_now,
)


def reference(set_id: str = "set-001", digest: str | None = "a" * 64):
    return ExperimentalComparisonSetReference(
        comparison_set_id=set_id,
        bundle_comparison_ids=("bundle-comparison-001",),
        set_digest=digest,
    )


def test_models_are_closed_and_frozen() -> None:
    request = ExperimentalComparisonSetComparisonRequest(
        set_comparison_id="set-comparison-001",
        left_set=reference(),
        right_set=reference("set-002", "b" * 64),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonSetComparisonRequest(
            set_comparison_id="set-comparison-001",
            left_set=reference(),
            right_set=reference("set-002", "b" * 64),
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        request.set_comparison_id = "changed"


def test_digest_label_is_normalized_and_validated() -> None:
    assert reference(digest="A" * 64).set_digest == "a" * 64

    with pytest.raises(ValidationError):
        reference(digest="not-a-digest")


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonSetComparisonSettings()
    assert settings.max_bundle_comparison_count_per_side == 256

    with pytest.raises(ValidationError):
        ExperimentalComparisonSetComparisonSettings(max_bundle_comparison_count_per_side=0)


def test_result_defines_reference_difference_only() -> None:
    report = ExperimentalComparisonSetComparisonReport(
        set_comparison_id="set-comparison-001",
        left_comparison_set_id="set-001",
        right_comparison_set_id="set-002",
        added_bundle_comparison_ids=("bundle-comparison-002",),
        removed_bundle_comparison_ids=(),
        retained_bundle_comparison_ids=("bundle-comparison-001",),
        left_set_digest="a" * 64,
        right_set_digest="b" * 64,
        digest_changed=True,
        created_at=utc_now(),
        warnings=(),
        comparison_metadata={},
    )
    result = ExperimentalComparisonSetComparisonResult(
        comparison_report_created=True,
        report=report,
    )
    fields = type(result.report).model_fields

    assert "semantic_trend" not in fields
    assert "risk_level" not in fields
    assert "auth_state" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
