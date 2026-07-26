import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_series_comparison import (
    ExperimentalComparisonSeriesComparisonRequest,
    ExperimentalComparisonSeriesComparisonSettings,
    ExperimentalComparisonSeriesReference,
)


def series_ref(series_id: str, digest: str | None = None):
    return ExperimentalComparisonSeriesReference(
        comparison_series_id=series_id,
        set_comparison_ids=("set-comparison-001", "set-comparison-002"),
        series_digest=digest,
    )


def test_models_are_closed_and_frozen() -> None:
    reference = series_ref("series-001", "a" * 64)
    with pytest.raises(ValidationError):
        reference.comparison_series_id = "changed"
    with pytest.raises(ValidationError):
        ExperimentalComparisonSeriesReference(
            comparison_series_id="series-001",
            unexpected="value",
        )


def test_digest_label_validation() -> None:
    assert series_ref("series-001", "A" * 64).series_digest == "a" * 64
    with pytest.raises(ValidationError):
        series_ref("series-001", "not-a-digest")


def test_request_contains_only_reference_level_inputs() -> None:
    request = ExperimentalComparisonSeriesComparisonRequest(
        series_comparison_id="series-comparison-001",
        left_series=series_ref("series-left"),
        right_series=series_ref("series-right"),
    )
    fields = request.__class__.model_fields
    assert "runtime_state" not in fields
    assert "operator_response" not in fields
    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "difference_object" not in fields


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonSeriesComparisonSettings()
    assert settings.max_reference_count_per_side == 256
    with pytest.raises(ValidationError):
        ExperimentalComparisonSeriesComparisonSettings(max_reference_count_per_side=0)
