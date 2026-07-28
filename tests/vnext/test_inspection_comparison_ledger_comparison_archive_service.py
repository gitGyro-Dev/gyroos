from datetime import datetime, timezone

import pytest

from app.vnext.inspection_comparison_ledger_comparison_archive import (
    ExperimentalComparisonLedgerComparisonArchiveRequest,
    ExperimentalComparisonLedgerComparisonArchiveSettings,
    ExperimentalComparisonLedgerComparisonReference,
)
from app.vnext.inspection_comparison_ledger_comparison_archive_service import (
    ExperimentalComparisonLedgerComparisonArchiveDuplicateError,
    ExperimentalComparisonLedgerComparisonArchiveResourceLimitError,
    ExperimentalComparisonLedgerComparisonArchiveService,
)


def reference(identifier: str) -> ExperimentalComparisonLedgerComparisonReference:
    return ExperimentalComparisonLedgerComparisonReference(
        ledger_comparison_id=identifier,
        left_comparison_ledger_id=f"left-{identifier}",
        right_comparison_ledger_id=f"right-{identifier}",
        added_count=1,
        removed_count=2,
        retained_count=3,
        digest_changed=False,
    )


def request(*references: ExperimentalComparisonLedgerComparisonReference, metadata=None):
    return ExperimentalComparisonLedgerComparisonArchiveRequest(
        comparison_archive_id="archive-1",
        ledger_comparisons=references,
        created_at=datetime.now(timezone.utc),
        metadata=metadata or {},
    )


def test_create_archive_preserves_request_order_and_digest() -> None:
    service = ExperimentalComparisonLedgerComparisonArchiveService()
    result = service.create_archive(request(reference("cmp-2"), reference("cmp-1")))

    assert result.result == "comparison_archive_created"
    assert [
        item.ledger_comparison_id for item in result.manifest.ledger_comparisons
    ] == ["cmp-2", "cmp-1"]
    assert result.manifest.reference_count == 2
    assert len(result.manifest.archive_digest) == 64


def test_create_archive_rejects_duplicate_comparison_ids() -> None:
    service = ExperimentalComparisonLedgerComparisonArchiveService()

    with pytest.raises(ExperimentalComparisonLedgerComparisonArchiveDuplicateError):
        service.create_archive(request(reference("cmp-1"), reference("cmp-1")))


def test_create_archive_enforces_reference_count_limit() -> None:
    service = ExperimentalComparisonLedgerComparisonArchiveService(
        ExperimentalComparisonLedgerComparisonArchiveSettings(max_references=1)
    )

    with pytest.raises(
        ExperimentalComparisonLedgerComparisonArchiveResourceLimitError
    ):
        service.create_archive(request(reference("cmp-1"), reference("cmp-2")))


def test_create_archive_enforces_metadata_byte_limit() -> None:
    service = ExperimentalComparisonLedgerComparisonArchiveService(
        ExperimentalComparisonLedgerComparisonArchiveSettings(max_metadata_bytes=8)
    )

    with pytest.raises(
        ExperimentalComparisonLedgerComparisonArchiveResourceLimitError
    ):
        service.create_archive(request(reference("cmp-1"), metadata={"text": "long"}))


def test_create_archive_does_not_emit_runtime_or_authentication_outputs() -> None:
    service = ExperimentalComparisonLedgerComparisonArchiveService()
    payload = service.create_archive(request(reference("cmp-1"))).model_dump(mode="json")
    text = str(payload)

    assert "operator_response" not in text
    assert "auth_state" not in text
    assert "risk" not in text
    assert "difference_object" not in text
