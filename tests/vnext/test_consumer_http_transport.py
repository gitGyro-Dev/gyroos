import json

import pytest

from app.vnext.consumer_boundary import ExperimentalHttpTransportSettings
from app.vnext.consumer_http_transport import (
    ExperimentalHttpDecodeError,
    ExperimentalHttpNotFoundError,
    ExperimentalHttpResponse,
    ExperimentalHttpResponseError,
    ExperimentalRecordHttpAdapter,
)


class StubClient:
    def __init__(self, response: ExperimentalHttpResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def get(
        self,
        *,
        url: str,
        headers: dict[str, str],
        timeout_seconds: float,
        verify_tls: bool,
    ) -> ExperimentalHttpResponse:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "timeout_seconds": timeout_seconds,
                "verify_tls": verify_tls,
            }
        )
        return self.response


def make_success_response() -> ExperimentalHttpResponse:
    body = json.dumps(
        {
            "record": {
                "record_id": "record-001",
                "process_id": "process-001",
                "record_type": "TrajectoryGraph",
                "payload": {"trajectory_node_refs": []},
                "provisional": True,
                "metadata": {},
            }
        }
    ).encode("utf-8")
    return ExperimentalHttpResponse(
        status_code=200,
        body=body,
        content_type="application/json",
    )


def test_fetch_record_uses_get_endpoint_and_bearer_header() -> None:
    client = StubClient(make_success_response())
    adapter = ExperimentalRecordHttpAdapter(
        ExperimentalHttpTransportSettings(
            base_url="https://gyroos.example",
            bearer_token="secret-token",
            timeout_seconds=3.0,
            verify_tls=True,
        ),
        client=client,
    )

    snapshot = adapter.fetch_record("record-001")

    assert snapshot.record_id == "record-001"
    assert client.calls == [
        {
            "url": "https://gyroos.example/vnext/experimental/records/record-001",
            "headers": {
                "Accept": "application/json",
                "Authorization": "Bearer secret-token",
            },
            "timeout_seconds": 3.0,
            "verify_tls": True,
        }
    ]


def test_fetch_record_raises_explicit_errors() -> None:
    not_found = ExperimentalRecordHttpAdapter(
        ExperimentalHttpTransportSettings(base_url="https://gyroos.example"),
        client=StubClient(ExperimentalHttpResponse(status_code=404, body=b"{}")),
    )
    with pytest.raises(ExperimentalHttpNotFoundError):
        not_found.fetch_record("missing")

    unavailable = ExperimentalRecordHttpAdapter(
        ExperimentalHttpTransportSettings(base_url="https://gyroos.example"),
        client=StubClient(ExperimentalHttpResponse(status_code=503, body=b"{}")),
    )
    with pytest.raises(ExperimentalHttpResponseError):
        unavailable.fetch_record("record-001")


def test_fetch_record_rejects_invalid_json_and_envelope() -> None:
    invalid_json = ExperimentalRecordHttpAdapter(
        ExperimentalHttpTransportSettings(base_url="https://gyroos.example"),
        client=StubClient(ExperimentalHttpResponse(status_code=200, body=b"not-json")),
    )
    with pytest.raises(ExperimentalHttpDecodeError):
        invalid_json.fetch_record("record-001")

    invalid_envelope = ExperimentalRecordHttpAdapter(
        ExperimentalHttpTransportSettings(base_url="https://gyroos.example"),
        client=StubClient(
            ExperimentalHttpResponse(
                status_code=200,
                body=json.dumps({"record": "invalid"}).encode("utf-8"),
            )
        ),
    )
    with pytest.raises(ExperimentalHttpDecodeError):
        invalid_envelope.fetch_record("record-001")


def test_transport_response_has_no_authentication_outcomes() -> None:
    fields = set(ExperimentalHttpResponse.__dataclass_fields__)
    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
