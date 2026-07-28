from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.vnext.inspection_comparison_ledger_comparison import (
    ExperimentalComparisonLedgerComparisonRequest,
    ExperimentalComparisonLedgerComparisonResult,
    ExperimentalComparisonLedgerComparisonSettings,
    ExperimentalComparisonLedgerReference,
)


def make_reference(ledger_id: str, digest: str | None = None):
    return ExperimentalComparisonLedgerReference(
        comparison_ledger_id=ledger_id,
        register_comparison_ids=("register-comparison-1",),
        ledger_digest=digest,
    )


def test_models_are_closed_and_frozen():
    request = ExperimentalComparisonLedgerComparisonRequest(
        ledger_comparison_id="ledger-comparison-1",
        left=make_reference("ledger-left"),
        right=make_reference("ledger-right"),
        created_at=datetime.now(UTC),
    )

    with pytest.raises(ValidationError):
        request.ledger_comparison_id = "changed"

    with pytest.raises(ValidationError):
        ExperimentalComparisonLedgerReference(
            comparison_ledger_id="ledger-1",
            register_comparison_ids=(),
            unexpected=True,
        )


def test_digest_label_must_be_lowercase_sha256_hex():
    valid = "a" * 64
    assert make_reference("ledger-1", valid).ledger_digest == valid

    with pytest.raises(ValidationError):
        make_reference("ledger-1", "A" * 64)

    with pytest.raises(ValidationError):
        make_reference("ledger-1", "abc")


def test_settings_bounds_are_enforced():
    settings = ExperimentalComparisonLedgerComparisonSettings()
    assert settings.max_references_per_side == 128

    with pytest.raises(ValidationError):
        ExperimentalComparisonLedgerComparisonSettings(max_references_per_side=0)


def test_result_meaning_is_bounded_and_non_runtime():
    fields = set(ExperimentalComparisonLedgerComparisonResult.model_fields)
    assert fields == {"result", "report"}
    assert "operator_response" not in fields
    assert "auth_state" not in fields
    assert "risk" not in fields
    assert "difference_object" not in fields
