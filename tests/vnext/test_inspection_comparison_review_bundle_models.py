import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_review_bundle import (
    ExperimentalComparisonReportReference,
    ExperimentalComparisonReviewBundleDigestPolicy,
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleSettings,
)


def reference(comparison_id: str) -> ExperimentalComparisonReportReference:
    return ExperimentalComparisonReportReference(
        comparison_id=comparison_id,
        left_manifest_id=f"left-{comparison_id}",
        right_manifest_id=f"right-{comparison_id}",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalComparisonReviewBundleSettings(max_comparison_count=0)


def test_digest_is_deterministic_and_order_sensitive() -> None:
    policy = ExperimentalComparisonReviewBundleDigestPolicy()
    first = [reference("a").model_dump(mode="json"), reference("b").model_dump(mode="json")]
    same = [reference("a").model_dump(mode="json"), reference("b").model_dump(mode="json")]
    reversed_order = list(reversed(first))

    assert policy.digest(first) == policy.digest(same)
    assert policy.digest(first) != policy.digest(reversed_order)


def test_digest_policy_rejects_unsupported_canonicalization() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonReviewBundleDigestPolicy(canonicalization="UNSUPPORTED")


def test_request_is_closed_and_frozen() -> None:
    request = ExperimentalComparisonReviewBundleRequest(
        review_bundle_id="bundle-001",
        comparison_references=(reference("a"),),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonReviewBundleRequest(
            **request.model_dump(mode="python"),
            risk_level="HIGH",
        )

    with pytest.raises(ValidationError):
        request.review_bundle_id = "changed"


def test_models_do_not_define_runtime_authentication_or_semantic_outputs() -> None:
    fields = ExperimentalComparisonReviewBundleRequest.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
