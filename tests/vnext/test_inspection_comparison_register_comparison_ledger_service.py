import pytest

from app.vnext.inspection_comparison_register_comparison_ledger import (
    ExperimentalComparisonRegisterComparisonLedgerRequest,
    ExperimentalComparisonRegisterComparisonLedgerSettings,
    ExperimentalComparisonRegisterComparisonReference,
)
from app.vnext.inspection_comparison_register_comparison_ledger_service import (
    ExperimentalComparisonRegisterComparisonLedgerDuplicateError,
    ExperimentalComparisonRegisterComparisonLedgerResourceLimitError,
    ExperimentalComparisonRegisterComparisonLedgerService,
)


def reference(identifier: str) -> ExperimentalComparisonRegisterComparisonReference:
    return ExperimentalComparisonRegisterComparisonReference(
        register_comparison_id=identifier,
        left_comparison_register_id=f"{identifier}-left",
        right_comparison_register_id=f"{identifier}-right",
        added_count=1,
        removed_count=1,
        retained_count=2,
        digest_changed=False,
    )


def request(*references: ExperimentalComparisonRegisterComparisonReference):
    return ExperimentalComparisonRegisterComparisonLedgerRequest(
        comparison_ledger_id="ledger-001",
        comparison_references=references,
        warnings=("inspection-only",),
        source_refs=("source-001",),
        ledger_metadata={"purpose": "inspection"},
    )


def test_create_ledger_preserves_order_and_creates_digest() -> None:
    first = reference("register-comparison-001")
    second = reference("register-comparison-002")

    result = ExperimentalComparisonRegisterComparisonLedgerService().create_ledger(
        request(first, second)
    )

    assert result.comparison_ledger_created is True
    assert result.manifest.comparison_references == (first, second)
    assert result.manifest.comparison_count == 2
    assert len(result.manifest.ledger_digest) == 64


def test_duplicate_register_comparison_id_is_rejected() -> None:
    duplicate = reference("register-comparison-001")

    with pytest.raises(ExperimentalComparisonRegisterComparisonLedgerDuplicateError):
        ExperimentalComparisonRegisterComparisonLedgerService().create_ledger(
            request(duplicate, duplicate)
        )


def test_reference_count_limit_is_enforced() -> None:
    service = ExperimentalComparisonRegisterComparisonLedgerService(
        ExperimentalComparisonRegisterComparisonLedgerSettings(
            max_comparison_references=1
        )
    )

    with pytest.raises(ExperimentalComparisonRegisterComparisonLedgerResourceLimitError):
        service.create_ledger(
            request(
                reference("register-comparison-001"),
                reference("register-comparison-002"),
            )
        )


def test_metadata_byte_limit_is_enforced() -> None:
    service = ExperimentalComparisonRegisterComparisonLedgerService(
        ExperimentalComparisonRegisterComparisonLedgerSettings(max_metadata_bytes=2)
    )

    with pytest.raises(ExperimentalComparisonRegisterComparisonLedgerResourceLimitError):
        service.create_ledger(request(reference("register-comparison-001")))


def test_manifest_has_no_runtime_authentication_or_semantic_outputs() -> None:
    manifest = ExperimentalComparisonRegisterComparisonLedgerService().create_ledger(
        request(reference("register-comparison-001"))
    ).manifest
    fields = manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
