import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_series_comparison_collection import (
    ExperimentalComparisonSeriesComparisonCollectionDigestPolicy,
    ExperimentalComparisonSeriesComparisonCollectionManifest,
    ExperimentalComparisonSeriesComparisonCollectionRequest,
    ExperimentalComparisonSeriesComparisonCollectionResult,
    ExperimentalComparisonSeriesComparisonCollectionSettings,
    ExperimentalComparisonSeriesComparisonReference,
    digest_comparison_references,
)


def reference(
    series_comparison_id: str,
) -> ExperimentalComparisonSeriesComparisonReference:
    return ExperimentalComparisonSeriesComparisonReference(
        series_comparison_id=series_comparison_id,
        left_comparison_series_id=f"{series_comparison_id}-left",
        right_comparison_series_id=f"{series_comparison_id}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_models_are_closed_and_frozen() -> None:
    item = reference("series-comparison-001")

    with pytest.raises(ValidationError):
        ExperimentalComparisonSeriesComparisonReference(
            **item.model_dump(),
            unexpected="value",
        )

    with pytest.raises(ValidationError):
        item.series_comparison_id = "changed"  # type: ignore[misc]


def test_request_rejects_empty_reference_set() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonSeriesComparisonCollectionRequest(
            comparison_collection_id="collection-001",
            comparison_references=(),
        )


def test_digest_is_deterministic_and_order_sensitive() -> None:
    policy = ExperimentalComparisonSeriesComparisonCollectionDigestPolicy()
    first = reference("series-comparison-001")
    second = reference("series-comparison-002")

    digest_a = digest_comparison_references((first, second), policy)
    digest_b = digest_comparison_references((first, second), policy)
    reversed_digest = digest_comparison_references((second, first), policy)

    assert digest_a == digest_b
    assert len(digest_a) == 64
    assert digest_a != reversed_digest


def test_settings_bounds_are_enforced() -> None:
    settings = ExperimentalComparisonSeriesComparisonCollectionSettings()
    assert settings.max_comparison_count == 100
    assert settings.max_metadata_bytes == 16384

    with pytest.raises(ValidationError):
        ExperimentalComparisonSeriesComparisonCollectionSettings(
            max_comparison_count=0
        )


def test_result_models_expose_no_runtime_authentication_or_semantic_fields() -> None:
    forbidden = {
        "auth_state",
        "risk_level",
        "semantic_trend",
        "operator_response",
        "runtime_state",
        "difference_object",
        "boundary_evaluation",
    }

    assert forbidden.isdisjoint(
        ExperimentalComparisonSeriesComparisonCollectionManifest.model_fields
    )
    assert forbidden.isdisjoint(
        ExperimentalComparisonSeriesComparisonCollectionResult.model_fields
    )
