import pytest

from app.vnext.inspection_comparison_series_comparison_collection import (
    ExperimentalComparisonSeriesComparisonCollectionRequest,
    ExperimentalComparisonSeriesComparisonCollectionSettings,
    ExperimentalComparisonSeriesComparisonReference,
)
from app.vnext.inspection_comparison_series_comparison_collection_service import (
    ExperimentalComparisonSeriesComparisonCollectionDuplicateError,
    ExperimentalComparisonSeriesComparisonCollectionResourceLimitError,
    ExperimentalComparisonSeriesComparisonCollectionService,
)


def reference(series_comparison_id: str) -> ExperimentalComparisonSeriesComparisonReference:
    return ExperimentalComparisonSeriesComparisonReference(
        series_comparison_id=series_comparison_id,
        left_comparison_series_id=f"{series_comparison_id}-left",
        right_comparison_series_id=f"{series_comparison_id}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_create_collection_preserves_order_and_creates_digest() -> None:
    request = ExperimentalComparisonSeriesComparisonCollectionRequest(
        comparison_collection_id="collection-001",
        comparison_references=(
            reference("series-comparison-001"),
            reference("series-comparison-002"),
        ),
        source_refs=("source-001",),
        collection_metadata={"purpose": "inspection"},
    )

    result = ExperimentalComparisonSeriesComparisonCollectionService().create_collection(
        request
    )

    assert result.comparison_collection_created is True
    assert result.manifest.comparison_count == 2
    assert [
        item.series_comparison_id for item in result.manifest.comparison_references
    ] == ["series-comparison-001", "series-comparison-002"]
    assert len(result.manifest.comparison_references_digest) == 64


def test_duplicate_series_comparison_id_is_rejected() -> None:
    request = ExperimentalComparisonSeriesComparisonCollectionRequest(
        comparison_collection_id="collection-001",
        comparison_references=(
            reference("series-comparison-001"),
            reference("series-comparison-001"),
        ),
    )

    with pytest.raises(ExperimentalComparisonSeriesComparisonCollectionDuplicateError):
        ExperimentalComparisonSeriesComparisonCollectionService().create_collection(
            request
        )


def test_comparison_count_limit_is_enforced() -> None:
    service = ExperimentalComparisonSeriesComparisonCollectionService(
        ExperimentalComparisonSeriesComparisonCollectionSettings(max_comparison_count=1)
    )
    request = ExperimentalComparisonSeriesComparisonCollectionRequest(
        comparison_collection_id="collection-001",
        comparison_references=(
            reference("series-comparison-001"),
            reference("series-comparison-002"),
        ),
    )

    with pytest.raises(
        ExperimentalComparisonSeriesComparisonCollectionResourceLimitError
    ):
        service.create_collection(request)


def test_metadata_byte_limit_is_enforced() -> None:
    service = ExperimentalComparisonSeriesComparisonCollectionService(
        ExperimentalComparisonSeriesComparisonCollectionSettings(max_metadata_bytes=8)
    )
    request = ExperimentalComparisonSeriesComparisonCollectionRequest(
        comparison_collection_id="collection-001",
        comparison_references=(reference("series-comparison-001"),),
        collection_metadata={"value": "too-large"},
    )

    with pytest.raises(
        ExperimentalComparisonSeriesComparisonCollectionResourceLimitError
    ):
        service.create_collection(request)


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonSeriesComparisonCollectionRequest(
        comparison_collection_id="collection-001",
        comparison_references=(reference("series-comparison-001"),),
    )
    result = ExperimentalComparisonSeriesComparisonCollectionService().create_collection(
        request
    )
    fields = result.manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
