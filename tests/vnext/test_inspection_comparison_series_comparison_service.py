import pytest

from app.vnext.inspection_comparison_series_comparison import (
    ExperimentalComparisonSeriesComparisonRequest,
    ExperimentalComparisonSeriesComparisonSettings,
    ExperimentalComparisonSeriesReference,
)
from app.vnext.inspection_comparison_series_comparison_service import (
    ExperimentalComparisonSeriesComparisonDuplicateError,
    ExperimentalComparisonSeriesComparisonIdentityError,
    ExperimentalComparisonSeriesComparisonResourceLimitError,
    ExperimentalComparisonSeriesComparisonService,
)


def ref(series_id: str, ids: tuple[str, ...], digest: str | None = None):
    return ExperimentalComparisonSeriesReference(
        comparison_series_id=series_id,
        set_comparison_ids=ids,
        series_digest=digest,
    )


def request(left, right, metadata=None):
    return ExperimentalComparisonSeriesComparisonRequest(
        series_comparison_id="series-comparison-001",
        left_series=left,
        right_series=right,
        comparison_metadata=metadata or {},
    )


def test_compare_computes_deterministic_membership_difference() -> None:
    service = ExperimentalComparisonSeriesComparisonService()
    result = service.compare(
        request(
            ref("series-left", ("set-cmp-001", "set-cmp-002"), "a" * 64),
            ref("series-right", ("set-cmp-002", "set-cmp-003"), "b" * 64),
        )
    )
    report = result.report
    assert report.added_set_comparison_ids == ("set-cmp-003",)
    assert report.removed_set_comparison_ids == ("set-cmp-001",)
    assert report.retained_set_comparison_ids == ("set-cmp-002",)
    assert report.digest_changed is True


def test_digest_changed_false_and_none() -> None:
    service = ExperimentalComparisonSeriesComparisonService()
    same = service.compare(
        request(
            ref("series-left", (), "a" * 64),
            ref("series-right", (), "a" * 64),
        )
    )
    unknown = service.compare(
        request(ref("series-left", ()), ref("series-right", (), "a" * 64))
    )
    assert same.report.digest_changed is False
    assert unknown.report.digest_changed is None


def test_rejects_same_series_identity() -> None:
    service = ExperimentalComparisonSeriesComparisonService()
    with pytest.raises(ExperimentalComparisonSeriesComparisonIdentityError):
        service.compare(request(ref("same", ()), ref("same", ())))


def test_rejects_duplicate_ids_within_side() -> None:
    service = ExperimentalComparisonSeriesComparisonService()
    with pytest.raises(ExperimentalComparisonSeriesComparisonDuplicateError):
        service.compare(
            request(
                ref("left", ("set-cmp-001", "set-cmp-001")),
                ref("right", ()),
            )
        )


def test_enforces_reference_count_and_metadata_limits() -> None:
    settings = ExperimentalComparisonSeriesComparisonSettings(
        max_reference_count_per_side=1,
        max_metadata_bytes=4,
    )
    service = ExperimentalComparisonSeriesComparisonService(settings)
    with pytest.raises(ExperimentalComparisonSeriesComparisonResourceLimitError):
        service.compare(
            request(ref("left", ("a", "b")), ref("right", ()))
        )
    with pytest.raises(ExperimentalComparisonSeriesComparisonResourceLimitError):
        service.compare(
            request(ref("left", ()), ref("right", ()), {"long": "value"})
        )


def test_report_has_no_runtime_authentication_or_semantic_outputs() -> None:
    service = ExperimentalComparisonSeriesComparisonService()
    report = service.compare(
        request(ref("left", ()), ref("right", ()))
    ).report
    fields = report.__class__.model_fields
    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
