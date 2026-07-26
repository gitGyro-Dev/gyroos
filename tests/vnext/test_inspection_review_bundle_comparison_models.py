import pytest
from pydantic import ValidationError

from app.vnext.inspection_review_bundle_comparison import (
    ExperimentalReviewBundleComparisonRequest,
    ExperimentalReviewBundleComparisonSettings,
    ExperimentalReviewBundleReference,
)


def bundle_ref(bundle_id: str = "bundle-left") -> ExperimentalReviewBundleReference:
    return ExperimentalReviewBundleReference(
        review_bundle_id=bundle_id,
        comparison_ids=("comparison-001", "comparison-002"),
        bundle_digest="a" * 64,
    )


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalReviewBundleComparisonSettings(max_identifier_length=0)


def test_bundle_reference_rejects_invalid_digest_label() -> None:
    with pytest.raises(ValidationError):
        ExperimentalReviewBundleReference(
            review_bundle_id="bundle-left",
            comparison_ids=("comparison-001",),
            bundle_digest="not-a-digest",
        )


def test_comparison_request_is_closed_and_frozen() -> None:
    request = ExperimentalReviewBundleComparisonRequest(
        bundle_comparison_id="bundle-comparison-001",
        left_bundle=bundle_ref("bundle-left"),
        right_bundle=bundle_ref("bundle-right"),
    )

    with pytest.raises(ValidationError):
        ExperimentalReviewBundleComparisonRequest(
            **request.model_dump(mode="python"),
            auth_state="AUTH_STABLE",
        )

    with pytest.raises(ValidationError):
        request.bundle_comparison_id = "changed"


def test_models_do_not_define_runtime_authentication_or_risk_fields() -> None:
    fields = ExperimentalReviewBundleComparisonRequest.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
