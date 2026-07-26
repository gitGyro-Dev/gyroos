import pytest
from pydantic import ValidationError

from app.vnext.experimental_api import (
    ExperimentalApiSettings,
    ExperimentalRecordCreateRequest,
    ExperimentalRecordListResponse,
)


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalApiSettings(max_payload_bytes=0)


def test_create_request_converts_to_opaque_envelope() -> None:
    request = ExperimentalRecordCreateRequest(
        record_id="record-001",
        process_id="process-001",
        record_type="TrajectoryGraph",
        payload={"nested": {"value": 1}},
        metadata={"source": "test"},
    )

    envelope = request.to_envelope()

    assert envelope.record_id == "record-001"
    assert envelope.record_type == "TrajectoryGraph"
    assert envelope.payload == {"nested": {"value": 1}}
    assert not hasattr(envelope, "current")
    assert not hasattr(envelope, "canonical")


def test_create_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ExperimentalRecordCreateRequest(
            record_id="record-001",
            process_id="process-001",
            record_type="TrajectoryGraph",
            payload={},
            current=True,
        )


def test_create_request_rejects_long_record_id() -> None:
    with pytest.raises(ValidationError):
        ExperimentalRecordCreateRequest(
            record_id="x" * 129,
            process_id="process-001",
            record_type="TrajectoryGraph",
            payload={},
        )


def test_create_request_rejects_long_record_type() -> None:
    with pytest.raises(ValidationError):
        ExperimentalRecordCreateRequest(
            record_id="record-001",
            process_id="process-001",
            record_type="x" * 129,
            payload={},
        )


def test_create_request_rejects_oversized_payload() -> None:
    with pytest.raises(ValidationError):
        ExperimentalRecordCreateRequest(
            record_id="record-001",
            process_id="process-001",
            record_type="TrajectoryGraph",
            payload={"value": "x" * 262_144},
        )


def test_create_request_rejects_non_json_serializable_payload() -> None:
    with pytest.raises(ValidationError):
        ExperimentalRecordCreateRequest(
            record_id="record-001",
            process_id="process-001",
            record_type="TrajectoryGraph",
            payload={"value": object()},
        )


def test_list_response_declares_unspecified_ordering() -> None:
    response = ExperimentalRecordListResponse(records=[], count=0)
    assert response.ordering == "UNSPECIFIED"
