from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_set_comparison_series import (
    ExperimentalComparisonSetComparisonReference,
    ExperimentalComparisonSetComparisonSeriesDigestPolicy,
    ExperimentalComparisonSetComparisonSeriesRequest,
    ExperimentalComparisonSetComparisonSeriesSettings,
    compute_series_digest,
)


def reference(identifier: str) -> ExperimentalComparisonSetComparisonReference:
    return ExperimentalComparisonSetComparisonReference(
        set_comparison_id=identifier,
        left_comparison_set_id=f"{identifier}-left",
        right_comparison_set_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_models_are_closed_and_frozen() -> None:
    request = ExperimentalComparisonSetComparisonSeriesRequest(
        comparison_series_id="series-001",
        set_comparison_references=(reference("comparison-001"),),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonSetComparisonSeriesRequest(
            comparison_series_id="series-001",
            set_comparison_references=(reference("comparison-001"),),
            unsupported=True,
        )

    with pytest.raises(ValidationError):
        request.comparison_series_id = "series-002"


def test_digest_is_deterministic_and_order_sensitive() -> None:
    first = reference("comparison-001")
    second = reference("comparison-002")

    digest_a = compute_series_digest((first, second))
    digest_b = compute_series_digest((first, second))
    digest_reversed = compute_series_digest((second, first))

    assert digest_a == digest_b
    assert len(digest_a) == 64
    assert digest_a != digest_reversed


def test_digest_policy_is_fixed() -> None:
    policy = ExperimentalComparisonSetComparisonSeriesDigestPolicy()

    assert policy.algorithm == "SHA-256"
    assert policy.canonicalization == "JSON_SORTED_KEYS_UTF8_COMPACT_V1"


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonSetComparisonSeriesSettings()
    assert settings.max_references == 100

    with pytest.raises(ValidationError):
        ExperimentalComparisonSetComparisonSeriesSettings(max_references=0)


def test_reference_contains_no_runtime_authentication_or_semantic_fields() -> None:
    fields = ExperimentalComparisonSetComparisonReference.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
