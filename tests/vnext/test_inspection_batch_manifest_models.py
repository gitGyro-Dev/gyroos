import pytest
from pydantic import ValidationError

from app.vnext.inspection_batch_manifest import (
    ExperimentalInspectionBatchDigestPolicy,
    ExperimentalInspectionBatchRequest,
    ExperimentalInspectionBatchSettings,
    ExperimentalInspectionReceiptReference,
)


def reference(receipt_id: str = "receipt-001") -> ExperimentalInspectionReceiptReference:
    return ExperimentalInspectionReceiptReference(
        receipt_id=receipt_id,
        source_record_id="record-001",
        source_process_id="process-001",
        source_record_type="TrajectoryGraph",
        source_contract_version="1.0.0",
        consumer_contract_version="1.0.0",
        compatible_for_inspection=True,
        payload_digest="a" * 64,
        metadata_digest="b" * 64,
    )


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalInspectionBatchSettings(max_receipt_count=0)


def test_digest_is_deterministic_and_key_order_independent() -> None:
    policy = ExperimentalInspectionBatchDigestPolicy()
    first = policy.digest([{"b": 2, "a": 1}])
    second = policy.digest([{"a": 1, "b": 2}])

    assert first == second
    assert len(first) == 64


def test_digest_is_order_sensitive_for_receipt_references() -> None:
    policy = ExperimentalInspectionBatchDigestPolicy()
    first = policy.digest([{"receipt_id": "a"}, {"receipt_id": "b"}])
    second = policy.digest([{"receipt_id": "b"}, {"receipt_id": "a"}])

    assert first != second


def test_request_is_closed_and_frozen() -> None:
    request = ExperimentalInspectionBatchRequest(
        manifest_id="manifest-001",
        receipt_references=(reference(),),
    )

    with pytest.raises(ValidationError):
        ExperimentalInspectionBatchRequest(
            **request.model_dump(mode="python"),
            auth_state="AUTH_STABLE",
        )

    with pytest.raises(ValidationError):
        request.manifest_id = "changed"


def test_models_do_not_define_runtime_or_authentication_fields() -> None:
    fields = ExperimentalInspectionBatchRequest.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
