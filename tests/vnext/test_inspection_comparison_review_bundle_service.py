import pytest

from app.vnext.inspection_comparison_review_bundle import (
    ExperimentalComparisonReportReference,
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleSettings,
)
from app.vnext.inspection_comparison_review_bundle_service import (
    ExperimentalComparisonReviewBundleDuplicateError,
    ExperimentalComparisonReviewBundleIdentityError,
    ExperimentalComparisonReviewBundleResourceLimitError,
    ExperimentalComparisonReviewBundleService,
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


def request(**overrides) -> ExperimentalComparisonReviewBundleRequest:
    values = {
        "review_bundle_id": "bundle-001",
        "comparison_references": (reference("a"), reference("b")),
        "warnings": ("caller_warning",),
        "source_refs": ("comparison-a",),
        "metadata": {"purpose": "inspection-review"},
    }
    values.update(overrides)
    return ExperimentalComparisonReviewBundleRequest(**values)


def test_service_creates_request_local_bundle_with_ordered_digest() -> None:
    result = ExperimentalComparisonReviewBundleService().create_bundle(request())

    assert result.review_bundle_created is True
    assert [
        item.comparison_id for item in result.bundle.comparison_references
    ] == ["a", "b"]
    assert len(result.bundle.ordered_reference_digest) == 64
    assert result.bundle.warnings == ("caller_warning",)


def test_service_rejects_empty_reference_set() -> None:
    with pytest.raises(ExperimentalComparisonReviewBundleIdentityError):
        ExperimentalComparisonReviewBundleService().create_bundle(
            request(comparison_references=())
        )


def test_service_rejects_duplicate_comparison_ids() -> None:
    with pytest.raises(ExperimentalComparisonReviewBundleDuplicateError):
        ExperimentalComparisonReviewBundleService().create_bundle(
            request(comparison_references=(reference("a"), reference("a")))
        )


def test_service_enforces_comparison_count_limit() -> None:
    service = ExperimentalComparisonReviewBundleService(
        settings=ExperimentalComparisonReviewBundleSettings(max_comparison_count=1)
    )

    with pytest.raises(ExperimentalComparisonReviewBundleResourceLimitError):
        service.create_bundle(request())


def test_service_enforces_metadata_byte_limit() -> None:
    service = ExperimentalComparisonReviewBundleService(
        settings=ExperimentalComparisonReviewBundleSettings(max_metadata_bytes=8)
    )

    with pytest.raises(ExperimentalComparisonReviewBundleResourceLimitError):
        service.create_bundle(request(metadata={"large": "0123456789"}))


def test_bundle_does_not_define_runtime_authentication_or_semantic_outputs() -> None:
    bundle = ExperimentalComparisonReviewBundleService().create_bundle(request()).bundle
    fields = type(bundle).model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
