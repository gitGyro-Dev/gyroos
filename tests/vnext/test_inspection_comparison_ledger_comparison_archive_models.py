from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_ledger_comparison_archive import (
    ExperimentalComparisonLedgerComparisonArchiveDigestPolicy,
    ExperimentalComparisonLedgerComparisonArchiveRequest,
    ExperimentalComparisonLedgerComparisonArchiveSettings,
    ExperimentalComparisonLedgerComparisonReference,
    compute_comparison_ledger_comparison_archive_digest,
)


def reference(identifier: str) -> ExperimentalComparisonLedgerComparisonReference:
    return ExperimentalComparisonLedgerComparisonReference(
        ledger_comparison_id=identifier,
        left_comparison_ledger_id=f"left-{identifier}",
        right_comparison_ledger_id=f"right-{identifier}",
        added_count=1,
        removed_count=0,
        retained_count=2,
        digest_changed=True,
    )


def test_archive_models_are_closed_and_frozen() -> None:
    item = reference("cmp-1")

    with pytest.raises(ValidationError):
        ExperimentalComparisonLedgerComparisonReference(
            ledger_comparison_id="cmp-1",
            left_comparison_ledger_id="left",
            right_comparison_ledger_id="right",
            added_count=0,
            removed_count=0,
            retained_count=0,
            unexpected="not-allowed",
        )

    with pytest.raises(ValidationError):
        item.ledger_comparison_id = "changed"


def test_archive_request_requires_at_least_one_reference() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonLedgerComparisonArchiveRequest(
            comparison_archive_id="archive-1",
            ledger_comparisons=(),
            created_at=datetime.now(timezone.utc),
        )


def test_archive_digest_is_deterministic() -> None:
    policy = ExperimentalComparisonLedgerComparisonArchiveDigestPolicy()
    references = (reference("cmp-1"), reference("cmp-2"))

    first = compute_comparison_ledger_comparison_archive_digest(references, policy)
    second = compute_comparison_ledger_comparison_archive_digest(references, policy)

    assert first == second
    assert len(first) == 64


def test_archive_digest_is_order_sensitive() -> None:
    policy = ExperimentalComparisonLedgerComparisonArchiveDigestPolicy()
    first = (reference("cmp-1"), reference("cmp-2"))
    second = tuple(reversed(first))

    assert compute_comparison_ledger_comparison_archive_digest(
        first, policy
    ) != compute_comparison_ledger_comparison_archive_digest(second, policy)


def test_archive_settings_are_bounded() -> None:
    settings = ExperimentalComparisonLedgerComparisonArchiveSettings()
    assert settings.max_references == 100

    with pytest.raises(ValidationError):
        ExperimentalComparisonLedgerComparisonArchiveSettings(max_references=0)


def test_archive_models_do_not_expose_runtime_or_authentication_fields() -> None:
    fields = set(ExperimentalComparisonLedgerComparisonArchiveRequest.model_fields)
    assert "operator_response" not in fields
    assert "auth_state" not in fields
    assert "risk" not in fields
    assert "difference_object" not in fields
