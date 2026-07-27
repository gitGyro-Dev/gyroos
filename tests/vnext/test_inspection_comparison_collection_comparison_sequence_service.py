import pytest

from app.vnext.inspection_comparison_collection_comparison_sequence import (
    ExperimentalComparisonCollectionComparisonReference,
    ExperimentalComparisonCollectionComparisonSequenceRequest,
    ExperimentalComparisonCollectionComparisonSequenceSettings,
)
from app.vnext.inspection_comparison_collection_comparison_sequence_service import (
    ExperimentalComparisonCollectionComparisonSequenceDuplicateError,
    ExperimentalComparisonCollectionComparisonSequenceIdentityError,
    ExperimentalComparisonCollectionComparisonSequenceResourceLimitError,
    ExperimentalComparisonCollectionComparisonSequenceService,
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


def request_with(
    references: tuple[ExperimentalComparisonCollectionComparisonReference, ...],
    *,
    metadata: dict | None = None,
) -> ExperimentalComparisonCollectionComparisonSequenceRequest:
    return ExperimentalComparisonCollectionComparisonSequenceRequest(
        comparison_sequence_id="sequence-001",
        comparison_references=references,
        warnings=(),
        source_refs=("source-001",),
        sequence_metadata=metadata or {},
    )


def test_create_sequence_preserves_order_and_digest() -> None:
    first = reference("comparison-001")
    second = reference("comparison-002")

    result = ExperimentalComparisonCollectionComparisonSequenceService().create_sequence(
        request_with((first, second))
    )

    assert result.comparison_sequence_created is True
    assert result.manifest.comparison_count == 2
    assert [
        item.collection_comparison_id
        for item in result.manifest.comparison_references
    ] == ["comparison-001", "comparison-002"]
    assert len(result.manifest.comparison_references_digest) == 64


def test_duplicate_reference_is_rejected() -> None:
    item = reference("comparison-001")

    with pytest.raises(ExperimentalComparisonCollectionComparisonSequenceDuplicateError):
        ExperimentalComparisonCollectionComparisonSequenceService().create_sequence(
            request_with((item, item))
        )


def test_empty_reference_set_is_rejected() -> None:
    with pytest.raises(ExperimentalComparisonCollectionComparisonSequenceIdentityError):
        ExperimentalComparisonCollectionComparisonSequenceService().create_sequence(
            request_with(())
        )


def test_reference_count_limit_is_enforced() -> None:
    service = ExperimentalComparisonCollectionComparisonSequenceService(
        ExperimentalComparisonCollectionComparisonSequenceSettings(
            max_comparison_count=1
        )
    )

    with pytest.raises(
        ExperimentalComparisonCollectionComparisonSequenceResourceLimitError
    ):
        service.create_sequence(
            request_with((reference("comparison-001"), reference("comparison-002")))
        )


def test_metadata_byte_limit_is_enforced() -> None:
    service = ExperimentalComparisonCollectionComparisonSequenceService(
        ExperimentalComparisonCollectionComparisonSequenceSettings(
            max_metadata_bytes=8
        )
    )

    with pytest.raises(
        ExperimentalComparisonCollectionComparisonSequenceResourceLimitError
    ):
        service.create_sequence(
            request_with((reference("comparison-001"),), metadata={"value": "too-long"})
        )


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    result = ExperimentalComparisonCollectionComparisonSequenceService().create_sequence(
        request_with((reference("comparison-001"),))
    )
    fields = result.manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
