import pytest

from app.vnext.inspection_comparison_collection_comparison import (
    ExperimentalComparisonCollectionComparisonRequest,
    ExperimentalComparisonCollectionComparisonSettings,
    ExperimentalComparisonCollectionReference,
)
from app.vnext.inspection_comparison_collection_comparison_service import (
    ExperimentalComparisonCollectionComparisonDuplicateError,
    ExperimentalComparisonCollectionComparisonIdentityError,
    ExperimentalComparisonCollectionComparisonResourceLimitError,
    ExperimentalComparisonCollectionComparisonService,
)


def reference(collection_id: str, ids: tuple[str, ...], digest: str | None):
    return ExperimentalComparisonCollectionReference(
        comparison_collection_id=collection_id,
        series_comparison_ids=ids,
        collection_digest=digest,
    )


def request(**overrides):
    data = {
        "collection_comparison_id": "collection-comparison-001",
        "left_collection": reference(
            "collection-left",
            ("series-cmp-001", "series-cmp-002"),
            "a" * 64,
        ),
        "right_collection": reference(
            "collection-right",
            ("series-cmp-002", "series-cmp-003"),
            "b" * 64,
        ),
        "warnings": (),
        "comparison_metadata": {"purpose": "inspection"},
    }
    data.update(overrides)
    return ExperimentalComparisonCollectionComparisonRequest(**data)


def test_compare_returns_deterministic_membership_difference() -> None:
    result = ExperimentalComparisonCollectionComparisonService().compare(request())
    report = result.report

    assert report.added_series_comparison_ids == ("series-cmp-003",)
    assert report.removed_series_comparison_ids == ("series-cmp-001",)
    assert report.retained_series_comparison_ids == ("series-cmp-002",)
    assert report.digest_changed is True


def test_ordering_follows_declared_side_order() -> None:
    result = ExperimentalComparisonCollectionComparisonService().compare(
        request(
            left_collection=reference(
                "collection-left",
                ("series-cmp-002", "series-cmp-001", "series-cmp-004"),
                "a" * 64,
            ),
            right_collection=reference(
                "collection-right",
                ("series-cmp-004", "series-cmp-003", "series-cmp-002"),
                "b" * 64,
            ),
        )
    )

    assert result.report.added_series_comparison_ids == ("series-cmp-003",)
    assert result.report.removed_series_comparison_ids == ("series-cmp-001",)
    assert result.report.retained_series_comparison_ids == (
        "series-cmp-002",
        "series-cmp-004",
    )


def test_same_collection_is_rejected() -> None:
    with pytest.raises(ExperimentalComparisonCollectionComparisonIdentityError):
        ExperimentalComparisonCollectionComparisonService().compare(
            request(
                right_collection=reference(
                    "collection-left",
                    ("series-cmp-002",),
                    "b" * 64,
                )
            )
        )


def test_duplicate_reference_within_side_is_rejected() -> None:
    with pytest.raises(ExperimentalComparisonCollectionComparisonDuplicateError):
        ExperimentalComparisonCollectionComparisonService().compare(
            request(
                left_collection=reference(
                    "collection-left",
                    ("series-cmp-001", "series-cmp-001"),
                    "a" * 64,
                )
            )
        )


def test_reference_count_and_metadata_are_bounded() -> None:
    service = ExperimentalComparisonCollectionComparisonService(
        ExperimentalComparisonCollectionComparisonSettings(
            max_reference_count=1,
            max_metadata_bytes=4,
        )
    )

    with pytest.raises(ExperimentalComparisonCollectionComparisonResourceLimitError):
        service.compare(request())

    service = ExperimentalComparisonCollectionComparisonService(
        ExperimentalComparisonCollectionComparisonSettings(max_metadata_bytes=4)
    )
    with pytest.raises(ExperimentalComparisonCollectionComparisonResourceLimitError):
        service.compare(request(comparison_metadata={"long": "value"}))


def test_digest_changed_is_none_when_a_digest_is_missing() -> None:
    result = ExperimentalComparisonCollectionComparisonService().compare(
        request(
            left_collection=reference(
                "collection-left",
                ("series-cmp-001",),
                None,
            )
        )
    )
    assert result.report.digest_changed is None


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    result = ExperimentalComparisonCollectionComparisonService().compare(request())
    fields = result.report.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
