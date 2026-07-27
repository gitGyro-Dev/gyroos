import pytest

from app.vnext.inspection_comparison_register_comparison import (
    ExperimentalComparisonRegisterComparisonRequest,
    ExperimentalComparisonRegisterComparisonSettings,
    ExperimentalComparisonRegisterReference,
)
from app.vnext.inspection_comparison_register_comparison_service import (
    ExperimentalComparisonRegisterComparisonDuplicateError,
    ExperimentalComparisonRegisterComparisonIdentityError,
    ExperimentalComparisonRegisterComparisonResourceLimitError,
    ExperimentalComparisonRegisterComparisonService,
)


def reference(register_id: str, ids: tuple[str, ...], digest: str | None = None):
    return ExperimentalComparisonRegisterReference(
        comparison_register_id=register_id,
        sequence_comparison_ids=ids,
        register_digest=digest,
    )


def request(
    *,
    left=None,
    right=None,
    metadata=None,
):
    return ExperimentalComparisonRegisterComparisonRequest(
        register_comparison_id="register-comparison-001",
        left_register=left
        or reference(
            "register-left",
            ("sequence-cmp-001", "sequence-cmp-002"),
            "a" * 64,
        ),
        right_register=right
        or reference(
            "register-right",
            ("sequence-cmp-002", "sequence-cmp-003"),
            "b" * 64,
        ),
        comparison_metadata=metadata or {},
    )


def test_compare_computes_deterministic_membership_difference() -> None:
    result = ExperimentalComparisonRegisterComparisonService().compare(request())
    report = result.report

    assert report.added_sequence_comparison_ids == ("sequence-cmp-003",)
    assert report.removed_sequence_comparison_ids == ("sequence-cmp-001",)
    assert report.retained_sequence_comparison_ids == ("sequence-cmp-002",)
    assert report.digest_changed is True


def test_ordering_uses_right_for_added_and_left_for_removed_and_retained() -> None:
    result = ExperimentalComparisonRegisterComparisonService().compare(
        request(
            left=reference(
                "register-left",
                ("sequence-cmp-003", "sequence-cmp-001", "sequence-cmp-002"),
            ),
            right=reference(
                "register-right",
                ("sequence-cmp-004", "sequence-cmp-002", "sequence-cmp-005", "sequence-cmp-003"),
            ),
        )
    )

    assert result.report.added_sequence_comparison_ids == (
        "sequence-cmp-004",
        "sequence-cmp-005",
    )
    assert result.report.removed_sequence_comparison_ids == ("sequence-cmp-001",)
    assert result.report.retained_sequence_comparison_ids == (
        "sequence-cmp-003",
        "sequence-cmp-002",
    )


def test_same_register_is_rejected() -> None:
    with pytest.raises(ExperimentalComparisonRegisterComparisonIdentityError):
        ExperimentalComparisonRegisterComparisonService().compare(
            request(
                left=reference("register-same", ("sequence-cmp-001",)),
                right=reference("register-same", ("sequence-cmp-002",)),
            )
        )


def test_duplicate_sequence_comparison_ids_are_rejected() -> None:
    with pytest.raises(ExperimentalComparisonRegisterComparisonDuplicateError):
        ExperimentalComparisonRegisterComparisonService().compare(
            request(
                left=reference(
                    "register-left",
                    ("sequence-cmp-001", "sequence-cmp-001"),
                )
            )
        )


def test_reference_count_limit_is_enforced() -> None:
    service = ExperimentalComparisonRegisterComparisonService(
        ExperimentalComparisonRegisterComparisonSettings(
            max_sequence_comparison_references_per_side=1
        )
    )
    with pytest.raises(ExperimentalComparisonRegisterComparisonResourceLimitError):
        service.compare(request())


def test_metadata_byte_limit_is_enforced() -> None:
    service = ExperimentalComparisonRegisterComparisonService(
        ExperimentalComparisonRegisterComparisonSettings(max_metadata_bytes=4)
    )
    with pytest.raises(ExperimentalComparisonRegisterComparisonResourceLimitError):
        service.compare(request(metadata={"purpose": "inspection"}))


def test_digest_changed_is_false_or_none_as_declared() -> None:
    service = ExperimentalComparisonRegisterComparisonService()
    equal_result = service.compare(
        request(
            left=reference("register-left", ("sequence-cmp-001",), "a" * 64),
            right=reference("register-right", ("sequence-cmp-001",), "a" * 64),
        )
    )
    missing_result = service.compare(
        request(
            left=reference("register-left", ("sequence-cmp-001",), None),
            right=reference("register-right", ("sequence-cmp-001",), "a" * 64),
        )
    )

    assert equal_result.report.digest_changed is False
    assert missing_result.report.digest_changed is None


def test_result_has_no_runtime_authentication_or_semantic_outputs() -> None:
    report = ExperimentalComparisonRegisterComparisonService().compare(request()).report
    fields = report.__class__.model_fields

    forbidden = {
        "auth_state",
        "risk_level",
        "semantic_trend",
        "operator_response",
        "runtime_state",
        "difference_object",
        "boundary_evaluation",
        "next_action",
    }
    assert forbidden.isdisjoint(fields)
