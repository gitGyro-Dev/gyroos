import pytest

from app.vnext.inspection_comparison_set_comparison_series import (
    ExperimentalComparisonSetComparisonReference,
    ExperimentalComparisonSetComparisonSeriesRequest,
    ExperimentalComparisonSetComparisonSeriesSettings,
)
from app.vnext.inspection_comparison_set_comparison_series_service import (
    ExperimentalComparisonSetComparisonSeriesDuplicateError,
    ExperimentalComparisonSetComparisonSeriesIdentityError,
    ExperimentalComparisonSetComparisonSeriesResourceLimitError,
    ExperimentalComparisonSetComparisonSeriesService,
)


def reference(identifier: str) -> ExperimentalComparisonSetComparisonReference:
    return ExperimentalComparisonSetComparisonReference(
        set_comparison_id=identifier,
        left_comparison_set_id=f"{identifier}-left",
        right_comparison_set_id=f"{identifier}-right",
        added_count=1,
        removed_count=0,
        retained_count=2,
        digest_changed=False,
    )


def request(*identifiers: str, metadata: dict | None = None):
    return ExperimentalComparisonSetComparisonSeriesRequest(
        comparison_series_id="series-001",
        set_comparison_references=tuple(reference(value) for value in identifiers),
        warnings=(),
        source_refs=(),
        series_metadata=metadata or {},
    )


def test_create_series_preserves_order_and_creates_digest() -> None:
    result = ExperimentalComparisonSetComparisonSeriesService().create_series(
        request("comparison-001", "comparison-002")
    )

    assert result.comparison_series_created is True
    assert result.manifest.reference_count == 2
    assert [
        item.set_comparison_id for item in result.manifest.set_comparison_references
    ] == ["comparison-001", "comparison-002"]
    assert len(result.manifest.series_digest) == 64


def test_rejects_empty_reference_set() -> None:
    with pytest.raises(ExperimentalComparisonSetComparisonSeriesIdentityError):
        ExperimentalComparisonSetComparisonSeriesService().create_series(request())


def test_rejects_duplicate_set_comparison_id() -> None:
    with pytest.raises(ExperimentalComparisonSetComparisonSeriesDuplicateError):
        ExperimentalComparisonSetComparisonSeriesService().create_series(
            request("comparison-001", "comparison-001")
        )


def test_rejects_reference_count_over_limit() -> None:
    service = ExperimentalComparisonSetComparisonSeriesService(
        settings=ExperimentalComparisonSetComparisonSeriesSettings(max_references=1)
    )

    with pytest.raises(ExperimentalComparisonSetComparisonSeriesResourceLimitError):
        service.create_series(request("comparison-001", "comparison-002"))


def test_rejects_metadata_over_limit() -> None:
    service = ExperimentalComparisonSetComparisonSeriesService(
        settings=ExperimentalComparisonSetComparisonSeriesSettings(max_metadata_bytes=2)
    )

    with pytest.raises(ExperimentalComparisonSetComparisonSeriesResourceLimitError):
        service.create_series(request("comparison-001", metadata={"x": "value"}))


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    result = ExperimentalComparisonSetComparisonSeriesService().create_series(
        request("comparison-001")
    )
    fields = result.manifest.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
