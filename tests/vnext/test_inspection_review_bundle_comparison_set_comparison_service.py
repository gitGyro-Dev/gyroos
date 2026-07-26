import pytest

from app.vnext.inspection_review_bundle_comparison_set_comparison import (
    ExperimentalComparisonSetComparisonRequest,
    ExperimentalComparisonSetComparisonSettings,
    ExperimentalComparisonSetReference,
)
from app.vnext.inspection_review_bundle_comparison_set_comparison_service import (
    ExperimentalComparisonSetComparisonDuplicateError,
    ExperimentalComparisonSetComparisonIdentityError,
    ExperimentalComparisonSetComparisonResourceLimitError,
    ExperimentalComparisonSetComparisonService,
)


def reference(
    set_id: str,
    ids: tuple[str, ...],
    digest: str | None,
) -> ExperimentalComparisonSetReference:
    return ExperimentalComparisonSetReference(
        comparison_set_id=set_id,
        bundle_comparison_ids=ids,
        set_digest=digest,
    )


def request(**overrides) -> ExperimentalComparisonSetComparisonRequest:
    values = {
        "set_comparison_id": "set-comparison-001",
        "left_set": reference(
            "set-left",
            ("bundle-comparison-001", "bundle-comparison-002"),
            "a" * 64,
        ),
        "right_set": reference(
            "set-right",
            ("bundle-comparison-002", "bundle-comparison-003"),
            "b" * 64,
        ),
        "warnings": (),
        "comparison_metadata": {"purpose": "inspection"},
    }
    values.update(overrides)
    return ExperimentalComparisonSetComparisonRequest(**values)


def test_service_computes_deterministic_membership_difference() -> None:
    result = ExperimentalComparisonSetComparisonService().compare(request())

    assert result.comparison_report_created is True
    assert result.report.added_bundle_comparison_ids == ("bundle-comparison-003",)
    assert result.report.removed_bundle_comparison_ids == ("bundle-comparison-001",)
    assert result.report.retained_bundle_comparison_ids == ("bundle-comparison-002",)
    assert result.report.digest_changed is True


def test_service_preserves_side_based_ordering() -> None:
    result = ExperimentalComparisonSetComparisonService().compare(
        request(
            left_set=reference("set-left", ("c", "a", "b"), "a" * 64),
            right_set=reference("set-right", ("b", "d", "a", "e"), "a" * 64),
        )
    )

    assert result.report.added_bundle_comparison_ids == ("d", "e")
    assert result.report.removed_bundle_comparison_ids == ("c",)
    assert result.report.retained_bundle_comparison_ids == ("a", "b")
    assert result.report.digest_changed is False


def test_service_rejects_same_set_on_both_sides() -> None:
    with pytest.raises(ExperimentalComparisonSetComparisonIdentityError):
        ExperimentalComparisonSetComparisonService().compare(
            request(
                right_set=reference(
                    "set-left",
                    ("bundle-comparison-003",),
                    "b" * 64,
                )
            )
        )


def test_service_rejects_duplicate_reference_within_side() -> None:
    with pytest.raises(ExperimentalComparisonSetComparisonDuplicateError):
        ExperimentalComparisonSetComparisonService().compare(
            request(
                left_set=reference(
                    "set-left",
                    ("bundle-comparison-001", "bundle-comparison-001"),
                    "a" * 64,
                )
            )
        )


def test_service_enforces_reference_count_limit() -> None:
    service = ExperimentalComparisonSetComparisonService(
        settings=ExperimentalComparisonSetComparisonSettings(
            max_bundle_comparison_count_per_side=1
        )
    )

    with pytest.raises(ExperimentalComparisonSetComparisonResourceLimitError):
        service.compare(request())


def test_service_enforces_metadata_byte_limit() -> None:
    service = ExperimentalComparisonSetComparisonService(
        settings=ExperimentalComparisonSetComparisonSettings(max_metadata_bytes=2)
    )

    with pytest.raises(ExperimentalComparisonSetComparisonResourceLimitError):
        service.compare(request())


def test_digest_changed_is_none_when_one_digest_is_absent() -> None:
    result = ExperimentalComparisonSetComparisonService().compare(
        request(
            right_set=reference(
                "set-right",
                ("bundle-comparison-002",),
                None,
            )
        )
    )

    assert result.report.digest_changed is None


def test_report_does_not_define_runtime_authentication_or_semantic_outputs() -> None:
    report = ExperimentalComparisonSetComparisonService().compare(request()).report
    fields = type(report).model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
