import pytest
from pydantic import ValidationError

from app.vnext.inspection_review_bundle_comparison_set import (
    ExperimentalReviewBundleComparisonReference,
    ExperimentalReviewBundleComparisonSetDigestPolicy,
    ExperimentalReviewBundleComparisonSetRequest,
    ExperimentalReviewBundleComparisonSetSettings,
    canonical_comparison_references_json,
    digest_comparison_references,
)


def reference(identifier: str):
    return ExperimentalReviewBundleComparisonReference(
        bundle_comparison_id=identifier,
        left_review_bundle_id=f"{identifier}-left",
        right_review_bundle_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_models_are_closed_and_frozen() -> None:
    value = reference("comparison-001")

    with pytest.raises(ValidationError):
        ExperimentalReviewBundleComparisonReference(
            bundle_comparison_id="comparison-001",
            left_review_bundle_id="left",
            right_review_bundle_id="right",
            added_count=0,
            removed_count=0,
            retained_count=0,
            unexpected="value",
        )

    with pytest.raises(ValidationError):
        value.bundle_comparison_id = "changed"


def test_settings_are_bounded() -> None:
    with pytest.raises(ValidationError):
        ExperimentalReviewBundleComparisonSetSettings(max_comparison_count=0)

    with pytest.raises(ValidationError):
        ExperimentalReviewBundleComparisonSetSettings(max_metadata_bytes=1048577)


def test_digest_is_deterministic() -> None:
    references = (reference("comparison-001"), reference("comparison-002"))
    policy = ExperimentalReviewBundleComparisonSetDigestPolicy()

    assert digest_comparison_references(references, policy) == digest_comparison_references(
        references, policy
    )
    assert len(digest_comparison_references(references, policy)) == 64


def test_digest_is_order_sensitive() -> None:
    first = reference("comparison-001")
    second = reference("comparison-002")
    policy = ExperimentalReviewBundleComparisonSetDigestPolicy()

    assert digest_comparison_references((first, second), policy) != digest_comparison_references(
        (second, first), policy
    )


def test_canonical_json_rejects_non_finite_values() -> None:
    request = ExperimentalReviewBundleComparisonSetRequest(
        comparison_set_id="set-001",
        comparison_references=(reference("comparison-001"),),
        metadata={"value": float("nan")},
    )

    assert canonical_comparison_references_json(request.comparison_references)


def test_request_does_not_define_runtime_or_authentication_fields() -> None:
    fields = ExperimentalReviewBundleComparisonSetRequest.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "operator_response" not in fields
    assert "next_action" not in fields
    assert "runtime_state" not in fields
    assert "semantic_trend" not in fields
    assert "risk_level" not in fields
