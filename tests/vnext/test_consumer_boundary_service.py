import pytest

from app.vnext.consumer_boundary import (
    ExperimentalConsumerReference,
    ExperimentalConsumptionRequest,
)
from app.vnext.consumer_boundary_service import (
    CallerSuppliedExperimentalEnvelopeAdapter,
    ExperimentalProcessMismatchError,
    ExperimentalRecordIdentityMismatchError,
    ExperimentalRecordInspectionService,
    ExperimentalRecordTypeMismatchError,
)


def make_envelope() -> dict:
    return {
        "record": {
            "record_id": "record-001",
            "process_id": "process-001",
            "record_type": "TrajectoryGraph",
            "payload": {"trajectory_node_refs": ["node-001"]},
            "provisional": True,
            "metadata": {"source": "gyroos-api"},
        }
    }


def test_adapter_accepts_wrapped_record_and_copies_payload() -> None:
    envelope = make_envelope()
    snapshot = CallerSuppliedExperimentalEnvelopeAdapter().adapt(envelope)
    envelope["record"]["payload"]["trajectory_node_refs"].append("node-002")

    assert snapshot.record_id == "record-001"
    assert snapshot.payload == {"trajectory_node_refs": ["node-001"]}


def test_inspection_result_is_not_authentication_acceptance() -> None:
    snapshot = CallerSuppliedExperimentalEnvelopeAdapter().adapt(make_envelope())
    result = ExperimentalRecordInspectionService().inspect(
        ExperimentalConsumptionRequest(
            reference=ExperimentalConsumerReference(
                record_id="record-001",
                expected_process_id="process-001",
                expected_record_type="TrajectoryGraph",
            ),
            snapshot=snapshot,
        )
    )

    assert result.accepted_for_inspection is True
    assert result.warnings == ["source_record_is_provisional"]
    assert "auth_state" not in type(result).model_fields
    assert "auth_score" not in type(result).model_fields
    assert "next_action" not in type(result).model_fields


def test_service_rejects_explicit_mismatches() -> None:
    snapshot = CallerSuppliedExperimentalEnvelopeAdapter().adapt(make_envelope())
    service = ExperimentalRecordInspectionService()

    with pytest.raises(ExperimentalRecordIdentityMismatchError):
        service.inspect(
            ExperimentalConsumptionRequest(
                reference=ExperimentalConsumerReference(record_id="other-record"),
                snapshot=snapshot,
            )
        )

    with pytest.raises(ExperimentalProcessMismatchError):
        service.inspect(
            ExperimentalConsumptionRequest(
                reference=ExperimentalConsumerReference(
                    record_id="record-001",
                    expected_process_id="other-process",
                ),
                snapshot=snapshot,
            )
        )

    with pytest.raises(ExperimentalRecordTypeMismatchError):
        service.inspect(
            ExperimentalConsumptionRequest(
                reference=ExperimentalConsumerReference(
                    record_id="record-001",
                    expected_record_type="StabilityScene",
                ),
                snapshot=snapshot,
            )
        )


def test_result_is_independent_from_source_snapshot_mutation() -> None:
    snapshot = CallerSuppliedExperimentalEnvelopeAdapter().adapt(make_envelope())
    result = ExperimentalRecordInspectionService().inspect(
        ExperimentalConsumptionRequest(
            reference=ExperimentalConsumerReference(record_id="record-001"),
            snapshot=snapshot,
        )
    )
    snapshot.payload["trajectory_node_refs"].append("node-002")

    assert result.snapshot.payload == {"trajectory_node_refs": ["node-001"]}
