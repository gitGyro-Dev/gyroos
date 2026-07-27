from pydantic import ValidationError
import pytest

from app.vnext.inspection_comparison_register_comparison_ledger import (
    ExperimentalComparisonRegisterComparisonLedgerDigestPolicy,
    ExperimentalComparisonRegisterComparisonLedgerRequest,
    ExperimentalComparisonRegisterComparisonLedgerSettings,
    ExperimentalComparisonRegisterComparisonReference,
)


def reference(identifier: str) -> ExperimentalComparisonRegisterComparisonReference:
    return ExperimentalComparisonRegisterComparisonReference(
        register_comparison_id=identifier,
        left_comparison_register_id=f"{identifier}-left",
        right_comparison_register_id=f"{identifier}-right",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=True,
    )


def test_models_are_closed_and_frozen() -> None:
    item = reference("register-comparison-001")

    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonReference(
            **item.model_dump(),
            unexpected="not-allowed",
        )

    with pytest.raises(ValidationError):
        item.added_count = 9


def test_request_rejects_empty_reference_set() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonLedgerRequest(
            comparison_ledger_id="ledger-001",
            comparison_references=(),
        )


def test_digest_is_deterministic() -> None:
    policy = ExperimentalComparisonRegisterComparisonLedgerDigestPolicy()
    references = (reference("register-comparison-001"), reference("register-comparison-002"))

    assert policy.digest(references) == policy.digest(references)
    assert len(policy.digest(references)) == 64


def test_digest_is_order_sensitive() -> None:
    policy = ExperimentalComparisonRegisterComparisonLedgerDigestPolicy()
    first = reference("register-comparison-001")
    second = reference("register-comparison-002")

    assert policy.digest((first, second)) != policy.digest((second, first))


def test_settings_are_bounded() -> None:
    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonLedgerSettings(
            max_comparison_references=0
        )

    with pytest.raises(ValidationError):
        ExperimentalComparisonRegisterComparisonLedgerSettings(
            max_metadata_bytes=65537
        )
