from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_collection_comparison_sequence import (
    ExperimentalComparisonCollectionComparisonReference,
    ExperimentalComparisonCollectionComparisonSequenceDigestPolicy,
    ExperimentalComparisonCollectionComparisonSequenceManifest,
    ExperimentalComparisonCollectionComparisonSequenceRequest,
    ExperimentalComparisonCollectionComparisonSequenceResult,
    ExperimentalComparisonCollectionComparisonSequenceSettings,
    digest_comparison_references,
)


def reference(identifier: str) -> ExperimentalComparisonCollectionComparisonReference:
    return ExperimentalComparisonCollectionComparisonReference(
        collection_comparison_id=identifier,
        left_comparison_collection_id=f"{identifier}-left",
        right_comparison_collection_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_models_are_closed_and_frozen() -> None:
    request = ExperimentalComparisonCollectionComparisonSequenceRequest(
        comparison_sequence_id="sequence-001",
        comparison_references=(reference("comparison-001"),),
    )

    with pytest.raises(ValidationError):
        ExperimentalComparisonCollectionComparisonSequenceRequest(
            comparison_sequence_id="sequence-001",
            comparison_references=(reference("comparison-001"),),
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        request.comparison_sequence_id = "sequence-002"


def test_digest_is_deterministic_and_order_sensitive() -> None:
    first = reference("comparison-001")
    second = reference("comparison-002")
    policy = ExperimentalComparisonCollectionComparisonSequenceDigestPolicy()

    digest_a = digest_comparison_references((first, second), policy)
    digest_b = digest_comparison_references((first, second), policy)
    digest_reversed = digest_comparison_references((second, first), policy)

    assert digest_a == digest_b
    assert len(digest_a) == 64
    assert digest_a != digest_reversed


def test_settings_are_bounded() -> None:
    settings = ExperimentalComparisonCollectionComparisonSequenceSettings()

    assert settings.max_comparison_count == 100
    assert settings.max_identifier_length == 256
    assert settings.max_warning_count == 50
    assert settings.max_source_ref_count == 100
    assert settings.max_metadata_bytes == 16384

    with pytest.raises(ValidationError):
        ExperimentalComparisonCollectionComparisonSequenceSettings(
            max_comparison_count=0
        )


def test_negative_counts_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonCollectionComparisonReference(
            collection_comparison_id="comparison-001",
            left_comparison_collection_id="left-001",
            right_comparison_collection_id="right-001",
            added_count=-1,
            removed_count=0,
            retained_count=0,
        )


def test_digest_changed_may_be_unknown() -> None:
    item = ExperimentalComparisonCollectionComparisonReference(
        collection_comparison_id="comparison-001",
        left_comparison_collection_id="left-001",
        right_comparison_collection_id="right-001",
        added_count=0,
        removed_count=0,
        retained_count=1,
        digest_changed=None,
    )

    assert item.digest_changed is None


def test_result_has_no_runtime_authentication_or_semantic_fields() -> None:
    item = reference("comparison-001")
    policy = ExperimentalComparisonCollectionComparisonSequenceDigestPolicy()
    manifest = ExperimentalComparisonCollectionComparisonSequenceManifest(
        comparison_sequence_id="sequence-001",
        comparison_references=(item,),
        comparison_count=1,
        comparison_references_digest=digest_comparison_references((item,), policy),
        digest_policy=policy,
        created_at=datetime.now(timezone.utc),
        warnings=(),
        source_refs=(),
        sequence_metadata={},
    )
    result = ExperimentalComparisonCollectionComparisonSequenceResult(manifest=manifest)
    fields = result.manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
