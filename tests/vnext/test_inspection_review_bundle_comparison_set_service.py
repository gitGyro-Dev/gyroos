import pytest

from app.vnext.inspection_review_bundle_comparison_set import (
    ExperimentalReviewBundleComparisonReference,
    ExperimentalReviewBundleComparisonSetRequest,
    ExperimentalReviewBundleComparisonSetSettings,
)
from app.vnext.inspection_review_bundle_comparison_set_service import (
    ExperimentalReviewBundleComparisonSetDuplicateError,
    ExperimentalReviewBundleComparisonSetIdentityError,
    ExperimentalReviewBundleComparisonSetResourceLimitError,
    ExperimentalReviewBundleComparisonSetService,
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


def request(**overrides):
    values = {
        "comparison_set_id": "set-001",
        "comparison_references": (
            reference("comparison-001"),
            reference("comparison-002"),
        ),
        "warnings": ("caller_warning",),
        "source_refs": ("source-001",),
        "metadata": {"purpose": "inspection"},
    }
    values.update(overrides)
    return ExperimentalReviewBundleComparisonSetRequest(**values)


def test_service_creates_request_local_set_with_digest() -> None:
    result = ExperimentalReviewBundleComparisonSetService().create_set(request())

    assert result.comparison_set_created is True
    assert result.comparison_set.comparison_count == 2
    assert len(result.comparison_set.comparison_references_digest) == 64
    assert tuple(
        item.bundle_comparison_id for item in result.comparison_set.comparison_references
    ) == ("comparison-001", "comparison-002")


def test_service_preserves_request_order() -> None:
    result = ExperimentalReviewBundleComparisonSetService().create_set(
        request(
            comparison_references=(
                reference("comparison-002"),
                reference("comparison-001"),
            )
        )
    )

    assert tuple(
        item.bundle_comparison_id for item in result.comparison_set.comparison_references
    ) == ("comparison-002", "comparison-001")


def test_service_rejects_empty_reference_set() -> None:
    with pytest.raises(ExperimentalReviewBundleComparisonSetIdentityError):
        ExperimentalReviewBundleComparisonSetService().create_set(
            request(comparison_references=())
        )


def test_service_rejects_duplicate_comparison_ids() -> None:
    duplicate = reference("comparison-001")
    with pytest.raises(ExperimentalReviewBundleComparisonSetDuplicateError):
        ExperimentalReviewBundleComparisonSetService().create_set(
            request(comparison_references=(duplicate, duplicate))
        )


def test_service_enforces_comparison_count_limit() -> None:
    service = ExperimentalReviewBundleComparisonSetService(
        settings=ExperimentalReviewBundleComparisonSetSettings(max_comparison_count=1)
    )

    with pytest.raises(ExperimentalReviewBundleComparisonSetResourceLimitError):
        service.create_set(request())


def test_service_enforces_metadata_limit() -> None:
    service = ExperimentalReviewBundleComparisonSetService(
        settings=ExperimentalReviewBundleComparisonSetSettings(max_metadata_bytes=2)
    )

    with pytest.raises(ExperimentalReviewBundleComparisonSetResourceLimitError):
        service.create_set(request(metadata={"value": "too-large"}))


def test_result_does_not_define_runtime_authentication_or_risk_outputs() -> None:
    result = ExperimentalReviewBundleComparisonSetService().create_set(request())
    fields = type(result.comparison_set).model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "operator_response" not in fields
    assert "next_action" not in fields
    assert "runtime_state" not in fields
    assert "semantic_trend" not in fields
    assert "risk_level" not in fields
