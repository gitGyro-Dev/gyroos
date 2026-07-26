import pytest
from pydantic import ValidationError

from app.vnext.consumer_compatibility import (
    CompatibilityDisposition,
    ExperimentalContractDescriptor,
    ExperimentalConsumerCompatibilityResult,
)
from app.vnext.inspection_receipt import (
    ExperimentalDigestPolicy,
    ExperimentalInspectionReceiptRequest,
    ExperimentalInspectionReceiptSettings,
)


def make_descriptor(version: str = "1.0.0") -> ExperimentalContractDescriptor:
    return ExperimentalContractDescriptor(
        source_api_namespace="/vnext/experimental",
        source_contract_version=version,
        consumer_contract_version=version,
        record_type="TrajectoryGraph",
    )


def make_compatibility_result() -> ExperimentalConsumerCompatibilityResult:
    return ExperimentalConsumerCompatibilityResult(
        compatible_for_inspection=True,
        disposition=CompatibilityDisposition.COMPATIBLE,
        source_contract_version="1.0.0",
        consumer_contract_version="1.0.0",
        record_type="TrajectoryGraph",
        warnings=[],
        rejection_reason=None,
    )


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalInspectionReceiptSettings(max_warning_count=0)


def test_digest_is_deterministic_and_key_order_independent() -> None:
    policy = ExperimentalDigestPolicy()

    first = policy.digest({"b": 2, "a": 1})
    second = policy.digest({"a": 1, "b": 2})

    assert first == second
    assert len(first) == 64


def test_digest_policy_rejects_unsupported_canonicalization() -> None:
    with pytest.raises(ValidationError):
        ExperimentalDigestPolicy(canonicalization="UNSUPPORTED")


def test_receipt_request_is_closed_and_frozen() -> None:
    request = ExperimentalInspectionReceiptRequest(
        receipt_id="receipt-001",
        source_record_id="record-001",
        source_process_id="process-001",
        source_record_type="TrajectoryGraph",
        source_contract=make_descriptor(),
        consumer_contract=make_descriptor(),
        compatibility_result=make_compatibility_result(),
        payload={"nodes": []},
    )

    with pytest.raises(ValidationError):
        ExperimentalInspectionReceiptRequest(
            **request.model_dump(mode="python"),
            auth_state="AUTH_STABLE",
        )

    with pytest.raises(ValidationError):
        request.receipt_id = "changed"


def test_receipt_models_do_not_define_runtime_or_authentication_fields() -> None:
    fields = ExperimentalInspectionReceiptRequest.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
