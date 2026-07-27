from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_sequence_comparison import (
    ExperimentalComparisonSequenceComparisonRequest,
    ExperimentalComparisonSequenceComparisonSettings,
    ExperimentalComparisonSequenceReference,
)


def reference() -> ExperimentalComparisonSequenceReference:
    return ExperimentalComparisonSequenceReference(
        comparison_sequence_id="sequence-001",
        collection_comparison_ids=("collection-cmp-001", "collection-cmp-002"),
        sequence_digest="a" * 64,
    )


def test_models_are_closed_and_frozen() -> None:
    item = reference()

    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceReference(
            comparison_sequence_id="sequence-001",
            unknown_field="not-approved",
        )

    with pytest.raises(ValidationError):
        item.comparison_sequence_id = "changed"


def test_digest_label_is_normalized_and_validated() -> None:
    item = ExperimentalComparisonSequenceReference(
        comparison_sequence_id="sequence-001",
        sequence_digest="A" * 64,
    )
    assert item.sequence_digest == "a" * 64

    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceReference(
            comparison_sequence_id="sequence-001",
            sequence_digest="not-a-digest",
        )


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonSequenceComparisonSettings()
    assert settings.max_reference_count == 100
    assert settings.max_identifier_length == 256
    assert settings.max_warning_count == 50
    assert settings.max_metadata_bytes == 16384

    with pytest.raises(ValidationError):
        ExperimentalComparisonSequenceComparisonSettings(max_reference_count=0)


def test_request_has_no_runtime_authentication_or_semantic_fields() -> None:
    request = ExperimentalComparisonSequenceComparisonRequest(
        sequence_comparison_id="sequence-comparison-001",
        left_sequence=reference(),
        right_sequence=ExperimentalComparisonSequenceReference(
            comparison_sequence_id="sequence-002"
        ),
    )
    fields = request.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
