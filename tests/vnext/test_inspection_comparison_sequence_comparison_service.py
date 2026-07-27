import pytest

from app.vnext.inspection_comparison_sequence_comparison import (
    ExperimentalComparisonSequenceComparisonRequest,
    ExperimentalComparisonSequenceComparisonSettings,
    ExperimentalComparisonSequenceReference,
)
from app.vnext.inspection_comparison_sequence_comparison_service import (
    ExperimentalComparisonSequenceComparisonDuplicateError,
    ExperimentalComparisonSequenceComparisonIdentityError,
    ExperimentalComparisonSequenceComparisonResourceLimitError,
    ExperimentalComparisonSequenceComparisonService,
)


def request() -> ExperimentalComparisonSequenceComparisonRequest:
    return ExperimentalComparisonSequenceComparisonRequest(
        sequence_comparison_id="sequence-comparison-001",
        left_sequence=ExperimentalComparisonSequenceReference(
            comparison_sequence_id="sequence-left",
            collection_comparison_ids=("collection-cmp-001", "collection-cmp-002"),
            sequence_digest="a" * 64,
        ),
        right_sequence=ExperimentalComparisonSequenceReference(
            comparison_sequence_id="sequence-right",
            collection_comparison_ids=("collection-cmp-002", "collection-cmp-003"),
            sequence_digest="b" * 64,
        ),
        comparison_metadata={"purpose": "inspection"},
    )


def test_compare_returns_deterministic_membership_difference() -> None:
    report = ExperimentalComparisonSequenceComparisonService().compare(request()).report

    assert report.added_collection_comparison_ids == ("collection-cmp-003",)
    assert report.removed_collection_comparison_ids == ("collection-cmp-001",)
    assert report.retained_collection_comparison_ids == ("collection-cmp-002",)
    assert report.digest_changed is True


def test_compare_preserves_side_based_ordering() -> None:
    value = request().model_copy(
        update={
            "left_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-left",
                collection_comparison_ids=("b", "a", "c"),
                sequence_digest="a" * 64,
            ),
            "right_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-right",
                collection_comparison_ids=("c", "d", "a"),
                sequence_digest="a" * 64,
            ),
        }
    )
    report = ExperimentalComparisonSequenceComparisonService().compare(value).report

    assert report.added_collection_comparison_ids == ("d",)
    assert report.removed_collection_comparison_ids == ("b",)
    assert report.retained_collection_comparison_ids == ("a", "c")
    assert report.digest_changed is False


def test_same_sequence_is_rejected() -> None:
    value = request().model_copy(
        update={
            "right_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-left"
            )
        }
    )

    with pytest.raises(ExperimentalComparisonSequenceComparisonIdentityError):
        ExperimentalComparisonSequenceComparisonService().compare(value)


def test_duplicate_reference_within_side_is_rejected() -> None:
    value = request().model_copy(
        update={
            "left_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-left",
                collection_comparison_ids=("duplicate", "duplicate"),
            )
        }
    )

    with pytest.raises(ExperimentalComparisonSequenceComparisonDuplicateError):
        ExperimentalComparisonSequenceComparisonService().compare(value)


def test_reference_count_and_metadata_are_bounded() -> None:
    settings = ExperimentalComparisonSequenceComparisonSettings(
        max_reference_count=1,
        max_metadata_bytes=2,
    )
    service = ExperimentalComparisonSequenceComparisonService(settings)

    with pytest.raises(ExperimentalComparisonSequenceComparisonResourceLimitError):
        service.compare(request())

    value = request().model_copy(
        update={
            "left_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-left",
                collection_comparison_ids=("one",),
            ),
            "right_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-right",
                collection_comparison_ids=("two",),
            ),
        }
    )
    with pytest.raises(ExperimentalComparisonSequenceComparisonResourceLimitError):
        service.compare(value)


def test_digest_changed_is_none_when_a_digest_is_missing() -> None:
    value = request().model_copy(
        update={
            "right_sequence": ExperimentalComparisonSequenceReference(
                comparison_sequence_id="sequence-right",
                collection_comparison_ids=("collection-cmp-002",),
            )
        }
    )

    report = ExperimentalComparisonSequenceComparisonService().compare(value).report
    assert report.digest_changed is None


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    report = ExperimentalComparisonSequenceComparisonService().compare(request()).report
    fields = report.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
