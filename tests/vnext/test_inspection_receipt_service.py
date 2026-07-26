import pytest

from app.vnext.consumer_compatibility import (
    CompatibilityDisposition,
    ExperimentalContractDescriptor,
    ExperimentalConsumerCompatibilityResult,
)
from app.vnext.inspection_receipt import (
    ExperimentalInspectionReceiptRequest,
    ExperimentalInspectionReceiptSettings,
)
from app.vnext.inspection_receipt_service import (
    ExperimentalInspectionReceiptService,
    ExperimentalReceiptCompatibilityError,
    ExperimentalReceiptIdentityError,
    ExperimentalReceiptResourceLimitError,
)


def descriptor(version: str = "1.0.0", record_type: str = "TrajectoryGraph"):
    return ExperimentalContractDescriptor(
        source_api_namespace="/vnext/experimental",
        source_contract_version=version,
        consumer_contract_version=version,
        record_type=record_type,
    )


def compatibility(
    compatible: bool = True,
    disposition: CompatibilityDisposition = CompatibilityDisposition.COMPATIBLE,
):
    return ExperimentalConsumerCompatibilityResult(
        compatible_for_inspection=compatible,
        disposition=disposition,
        source_contract_version="1.0.0",
        consumer_contract_version="1.0.0",
        record_type="TrajectoryGraph",
        warnings=["minor_version_mismatch"] if compatible else [],
        rejection_reason=None if compatible else "unsupported_major_version",
    )


def request(**overrides):
    values = {
        "receipt_id": "receipt-001",
        "source_record_id": "record-001",
        "source_process_id": "process-001",
        "source_record_type": "TrajectoryGraph",
        "source_contract": descriptor(),
        "consumer_contract": descriptor(),
        "compatibility_result": compatibility(),
        "payload": {"nodes": []},
        "source_metadata": {"source": "api"},
        "source_refs": ["record-001"],
        "warnings": ["caller_warning"],
        "receipt_metadata": {"purpose": "inspection"},
    }
    values.update(overrides)
    return ExperimentalInspectionReceiptRequest(**values)


def test_service_creates_request_local_receipt_with_digests() -> None:
    result = ExperimentalInspectionReceiptService().create_receipt(request())

    assert result.receipt_created is True
    assert len(result.receipt.payload_digest or "") == 64
    assert len(result.receipt.metadata_digest or "") == 64
    assert result.receipt.warnings == [
        "minor_version_mismatch",
        "caller_warning",
    ]
    assert "payload" not in type(result.receipt).model_fields
    assert "source_metadata" not in type(result.receipt).model_fields


def test_service_allows_incompatible_attempt_receipt_by_default() -> None:
    result = ExperimentalInspectionReceiptService().create_receipt(
        request(
            compatibility_result=compatibility(
                compatible=False,
                disposition=CompatibilityDisposition.INCOMPATIBLE,
            )
        )
    )

    assert result.receipt_created is True
    assert result.receipt.compatibility_result.compatible_for_inspection is False


def test_service_can_reject_incompatible_attempt_receipts_by_policy() -> None:
    service = ExperimentalInspectionReceiptService(
        settings=ExperimentalInspectionReceiptSettings(
            allow_incompatible_attempt_receipts=False
        )
    )

    with pytest.raises(ExperimentalReceiptCompatibilityError):
        service.create_receipt(
            request(
                compatibility_result=compatibility(
                    compatible=False,
                    disposition=CompatibilityDisposition.INCOMPATIBLE,
                )
            )
        )


def test_service_rejects_descriptor_record_type_mismatch() -> None:
    with pytest.raises(ExperimentalReceiptIdentityError):
        ExperimentalInspectionReceiptService().create_receipt(
            request(source_contract=descriptor(record_type="StabilityScene"))
        )


def test_service_rejects_inconsistent_compatibility_result() -> None:
    with pytest.raises(ExperimentalReceiptCompatibilityError):
        ExperimentalInspectionReceiptService().create_receipt(
            request(
                compatibility_result=compatibility(
                    compatible=True,
                    disposition=CompatibilityDisposition.INCOMPATIBLE,
                )
            )
        )


def test_service_enforces_receipt_resource_limits() -> None:
    service = ExperimentalInspectionReceiptService(
        settings=ExperimentalInspectionReceiptSettings(max_source_ref_count=1)
    )

    with pytest.raises(ExperimentalReceiptResourceLimitError):
        service.create_receipt(request(source_refs=["a", "b"]))


def test_receipt_result_does_not_define_runtime_or_authentication_outputs() -> None:
    receipt = ExperimentalInspectionReceiptService().create_receipt(request()).receipt
    fields = type(receipt).model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
