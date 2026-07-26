import pytest

from app.vnext.inspection_review_bundle_comparison import (
    ExperimentalReviewBundleComparisonRequest,
    ExperimentalReviewBundleComparisonSettings,
    ExperimentalReviewBundleReference,
)
from app.vnext.inspection_review_bundle_comparison_service import (
    ExperimentalReviewBundleComparisonDuplicateError,
    ExperimentalReviewBundleComparisonIdentityError,
    ExperimentalReviewBundleComparisonResourceLimitError,
    ExperimentalReviewBundleComparisonService,
)


def ref(bundle_id: str, comparison_ids: tuple[str, ...], digest: str | None = None):
    return ExperimentalReviewBundleReference(
        review_bundle_id=bundle_id,
        comparison_ids=comparison_ids,
        bundle_digest=digest,
    )


def request(**overrides):
    values = {
        "bundle_comparison_id": "bundle-comparison-001",
        "left_bundle": ref(
            "bundle-left",
            ("comparison-001", "comparison-002", "comparison-003"),
            "a" * 64,
        ),
        "right_bundle": ref(
            "bundle-right",
            ("comparison-002", "comparison-004", "comparison-003"),
            "b" * 64,
        ),
        "warnings": ("caller_warning",),
        "metadata": {"purpose": "inspection"},
    }
    values.update(overrides)
    return ExperimentalReviewBundleComparisonRequest(**values)


def test_service_creates_reference_level_comparison() -> None:
    result = ExperimentalReviewBundleComparisonService().compare(request())

    assert result.review_bundle_comparison_created is True
    assert result.report.added_comparison_ids == ("comparison-004",)
    assert result.report.removed_comparison_ids == ("comparison-001",)
    assert result.report.retained_comparison_ids == (
        "comparison-002",
        "comparison-003",
    )
    assert result.report.digest_changed is True


def test_service_preserves_side_based_ordering() -> None:
    result = ExperimentalReviewBundleComparisonService().compare(
        request(
            left_bundle=ref(
                "bundle-left",
                ("comparison-b", "comparison-a", "comparison-c"),
                "a" * 64,
            ),
            right_bundle=ref(
                "bundle-right",
                ("comparison-d", "comparison-c", "comparison-a"),
                "a" * 64,
            ),
        )
    )

    assert result.report.added_comparison_ids == ("comparison-d",)
    assert result.report.removed_comparison_ids == ("comparison-b",)
    assert result.report.retained_comparison_ids == (
        "comparison-a",
        "comparison-c",
    )
    assert result.report.digest_changed is False


def test_service_rejects_same_bundle_on_both_sides() -> None:
    same = ref("bundle-same", ("comparison-001",), "a" * 64)

    with pytest.raises(ExperimentalReviewBundleComparisonIdentityError):
        ExperimentalReviewBundleComparisonService().compare(
            request(left_bundle=same, right_bundle=same)
        )


def test_service_rejects_duplicate_comparison_ids_within_side() -> None:
    with pytest.raises(ExperimentalReviewBundleComparisonDuplicateError):
        ExperimentalReviewBundleComparisonService().compare(
            request(
                left_bundle=ref(
                    "bundle-left",
                    ("comparison-001", "comparison-001"),
                    "a" * 64,
                )
            )
        )


def test_service_enforces_comparison_reference_limit() -> None:
    service = ExperimentalReviewBundleComparisonService(
        ExperimentalReviewBundleComparisonSettings(max_comparison_reference_count=1)
    )

    with pytest.raises(ExperimentalReviewBundleComparisonResourceLimitError):
        service.compare(request())


def test_service_enforces_metadata_byte_limit() -> None:
    service = ExperimentalReviewBundleComparisonService(
        ExperimentalReviewBundleComparisonSettings(max_metadata_bytes=2)
    )

    with pytest.raises(ExperimentalReviewBundleComparisonResourceLimitError):
        service.compare(request(metadata={"x": "too-large"}))


def test_digest_changed_is_none_when_one_digest_is_missing() -> None:
    result = ExperimentalReviewBundleComparisonService().compare(
        request(
            left_bundle=ref("bundle-left", ("comparison-001",), None),
            right_bundle=ref("bundle-right", ("comparison-001",), "a" * 64),
        )
    )

    assert result.report.digest_changed is None


def test_report_does_not_define_runtime_authentication_semantic_or_risk_outputs() -> None:
    report = ExperimentalReviewBundleComparisonService().compare(request()).report
    fields = type(report).model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "difference_object" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
