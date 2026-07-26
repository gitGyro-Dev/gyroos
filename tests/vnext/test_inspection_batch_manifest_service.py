import pytest

from app.vnext.inspection_batch_manifest import (
    ExperimentalInspectionBatchRequest,
    ExperimentalInspectionBatchSettings,
    ExperimentalInspectionReceiptReference,
)
from app.vnext.inspection_batch_manifest_service import (
    ExperimentalInspectionBatchDuplicateError,
    ExperimentalInspectionBatchIdentityError,
    ExperimentalInspectionBatchResourceLimitError,
    ExperimentalInspectionBatchService,
)


def reference(receipt_id: str, record_id: str) -> ExperimentalInspectionReceiptReference:
    return ExperimentalInspectionReceiptReference(
        receipt_id=receipt_id,
        source_record_id=record_id,
        source_process_id="process-001",
        source_record_type="TrajectoryGraph",
        source_contract_version="1.0.0",
        consumer_contract_version="1.0.0",
        compatible_for_inspection=True,
        payload_digest="a" * 64,
        metadata_digest="b" * 64,
    )


def request(**overrides) -> ExperimentalInspectionBatchRequest:
    values = {
        "manifest_id": "manifest-001",
        "receipt_references": (
            reference("receipt-001", "record-001"),
            reference("receipt-002", "record-002"),
        ),
        "warnings": ("caller_warning",),
        "source_refs": ("batch-source",),
        "manifest_metadata": {"purpose": "review"},
    }
    values.update(overrides)
    return ExperimentalInspectionBatchRequest(**values)


def test_service_creates_request_local_manifest_with_digest() -> None:
    result = ExperimentalInspectionBatchService().create_manifest(request())

    assert result.batch_manifest_created is True
    assert result.manifest.manifest_id == "manifest-001"
    assert len(result.manifest.receipt_reference_digest) == 64
    assert result.manifest.warnings == ("caller_warning",)
    assert "auth_state" not in type(result.manifest).model_fields


def test_service_preserves_explicit_receipt_order() -> None:
    result = ExperimentalInspectionBatchService().create_manifest(request())

    assert tuple(ref.receipt_id for ref in result.manifest.receipt_references) == (
        "receipt-001",
        "receipt-002",
    )


def test_service_rejects_duplicate_receipt_ids() -> None:
    with pytest.raises(ExperimentalInspectionBatchDuplicateError):
        ExperimentalInspectionBatchService().create_manifest(
            request(
                receipt_references=(
                    reference("receipt-001", "record-001"),
                    reference("receipt-001", "record-002"),
                )
            )
        )


def test_service_rejects_empty_receipt_reference_set() -> None:
    with pytest.raises(ExperimentalInspectionBatchIdentityError):
        ExperimentalInspectionBatchService().create_manifest(
            request(receipt_references=())
        )


def test_service_enforces_receipt_count_limit() -> None:
    service = ExperimentalInspectionBatchService(
        settings=ExperimentalInspectionBatchSettings(max_receipt_count=1)
    )

    with pytest.raises(ExperimentalInspectionBatchResourceLimitError):
        service.create_manifest(request())


def test_service_enforces_metadata_byte_limit() -> None:
    service = ExperimentalInspectionBatchService(
        settings=ExperimentalInspectionBatchSettings(max_metadata_bytes=4)
    )

    with pytest.raises(ExperimentalInspectionBatchResourceLimitError):
        service.create_manifest(request(manifest_metadata={"large": "value"}))


def test_manifest_result_does_not_define_runtime_or_authentication_outputs() -> None:
    manifest = ExperimentalInspectionBatchService().create_manifest(request()).manifest
    fields = type(manifest).model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
