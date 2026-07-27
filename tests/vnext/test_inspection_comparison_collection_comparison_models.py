from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_collection_comparison import (
    ExperimentalComparisonCollectionComparisonRequest,
    ExperimentalComparisonCollectionComparisonSettings,
    ExperimentalComparisonCollectionReference,
)


def reference(**overrides):
    data = {
        "comparison_collection_id": "collection-left",
        "series_comparison_ids": ("series-cmp-001", "series-cmp-002"),
        "collection_digest": "a" * 64,
    }
    data.update(overrides)
    return ExperimentalComparisonCollectionReference(**data)


def test_reference_model_is_closed_and_frozen() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonCollectionReference(
            comparison_collection_id="collection-left",
            series_comparison_ids=("series-cmp-001",),
            unexpected=True,
        )

    item = reference()
    with pytest.raises(ValidationError):
        item.comparison_collection_id = "changed"


def test_digest_label_is_normalized_and_validated() -> None:
    assert reference(collection_digest="A" * 64).collection_digest == "a" * 64

    with pytest.raises(ValidationError):
        reference(collection_digest="not-a-digest")


def test_request_has_only_reference_comparison_fields() -> None:
    request = ExperimentalComparisonCollectionComparisonRequest(
        collection_comparison_id="collection-comparison-001",
        left_collection=reference(),
        right_collection=reference(
            comparison_collection_id="collection-right",
            collection_digest="b" * 64,
        ),
    )

    fields = request.__class__.model_fields
    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields


def test_settings_bounds_are_closed() -> None:
    settings = ExperimentalComparisonCollectionComparisonSettings()
    assert settings.max_reference_count == 100
    assert settings.max_identifier_length == 256
    assert settings.max_warning_count == 50
    assert settings.max_metadata_bytes == 16384

    with pytest.raises(ValidationError):
        ExperimentalComparisonCollectionComparisonSettings(max_reference_count=0)
