from datetime import UTC, datetime

import pytest

from app.vnext.inspection_comparison_ledger_comparison import (
    ExperimentalComparisonLedgerComparisonRequest,
    ExperimentalComparisonLedgerComparisonSettings,
    ExperimentalComparisonLedgerReference,
)
from app.vnext.inspection_comparison_ledger_comparison_service import (
    ExperimentalComparisonLedgerComparisonDuplicateError,
    ExperimentalComparisonLedgerComparisonIdentityError,
    ExperimentalComparisonLedgerComparisonResourceLimitError,
    ExperimentalComparisonLedgerComparisonService,
)


def make_reference(
    ledger_id: str,
    ids: tuple[str, ...],
    digest: str | None,
) -> ExperimentalComparisonLedgerReference:
    return ExperimentalComparisonLedgerReference(
        comparison_ledger_id=ledger_id,
        register_comparison_ids=ids,
        ledger_digest=digest,
    )


def make_request(
    left: ExperimentalComparisonLedgerReference,
    right: ExperimentalComparisonLedgerReference,
    metadata=None,
):
    return ExperimentalComparisonLedgerComparisonRequest(
        ledger_comparison_id="ledger-comparison-1",
        left=left,
        right=right,
        created_at=datetime.now(UTC),
        metadata=metadata or {},
    )


def test_compare_preserves_deterministic_side_ordering():
    service = ExperimentalComparisonLedgerComparisonService()
    result = service.compare(
        make_request(
            make_reference(
                "ledger-left",
                ("register-b", "register-a", "register-c"),
                "a" * 64,
            ),
            make_reference(
                "ledger-right",
                ("register-c", "register-d", "register-a"),
                "b" * 64,
            ),
        )
    )

    report = result.report
    assert report.added_register_comparison_ids == ("register-d",)
    assert report.removed_register_comparison_ids == ("register-b",)
    assert report.retained_register_comparison_ids == ("register-a", "register-c")
    assert report.digest_changed is True
    assert result.result == "comparison_ledger_comparison_created"


def test_digest_changed_false_and_none_are_supported():
    service = ExperimentalComparisonLedgerComparisonService()
    same = "c" * 64

    false_result = service.compare(
        make_request(
            make_reference("ledger-left", (), same),
            make_reference("ledger-right", (), same),
        )
    )
    assert false_result.report.digest_changed is False

    none_result = service.compare(
        make_request(
            make_reference("ledger-left", (), None),
            make_reference("ledger-right", (), same),
        )
    )
    assert none_result.report.digest_changed is None


def test_same_ledger_is_rejected():
    service = ExperimentalComparisonLedgerComparisonService()
    with pytest.raises(ExperimentalComparisonLedgerComparisonIdentityError):
        service.compare(
            make_request(
                make_reference("ledger-same", (), None),
                make_reference("ledger-same", (), None),
            )
        )


def test_duplicate_reference_within_side_is_rejected():
    service = ExperimentalComparisonLedgerComparisonService()
    with pytest.raises(ExperimentalComparisonLedgerComparisonDuplicateError):
        service.compare(
            make_request(
                make_reference("ledger-left", ("register-1", "register-1"), None),
                make_reference("ledger-right", (), None),
            )
        )


def test_reference_and_metadata_bounds_are_enforced():
    service = ExperimentalComparisonLedgerComparisonService(
        ExperimentalComparisonLedgerComparisonSettings(
            max_references_per_side=1,
            max_metadata_bytes=8,
        )
    )

    with pytest.raises(ExperimentalComparisonLedgerComparisonResourceLimitError):
        service.compare(
            make_request(
                make_reference("ledger-left", ("a", "b"), None),
                make_reference("ledger-right", (), None),
            )
        )

    with pytest.raises(ExperimentalComparisonLedgerComparisonResourceLimitError):
        service.compare(
            make_request(
                make_reference("ledger-left", (), None),
                make_reference("ledger-right", (), None),
                metadata={"long": "value"},
            )
        )


def test_output_has_no_runtime_authentication_or_semantic_fields():
    service = ExperimentalComparisonLedgerComparisonService()
    report = service.compare(
        make_request(
            make_reference("ledger-left", (), None),
            make_reference("ledger-right", (), None),
        )
    ).report.model_dump()

    assert "operator_response" not in report
    assert "auth_state" not in report
    assert "risk" not in report
    assert "difference_object" not in report
    assert "boundary_evaluation" not in report
