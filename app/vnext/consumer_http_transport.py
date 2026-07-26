from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .consumer_boundary import (
    ExperimentalConsumerSnapshot,
    ExperimentalHttpTransportSettings,
)
from .consumer_boundary_service import CallerSuppliedExperimentalEnvelopeAdapter


class ExperimentalHttpTransportError(RuntimeError):
    pass


class ExperimentalHttpNotFoundError(ExperimentalHttpTransportError):
    pass


class ExperimentalHttpResponseError(ExperimentalHttpTransportError):
    pass


class ExperimentalHttpDecodeError(ExperimentalHttpTransportError):
    pass


@dataclass(frozen=True, slots=True)
class ExperimentalHttpResponse:
    status_code: int
    body: bytes
    content_type: str | None = None


class ExperimentalReadOnlyHttpClient:
    def get(
        self,
        *,
        url: str,
        headers: dict[str, str],
        timeout_seconds: float,
        verify_tls: bool,
    ) -> ExperimentalHttpResponse:
        request = Request(url=url, headers=headers, method="GET")
        context = None if verify_tls else ssl._create_unverified_context()
        try:
            with urlopen(request, timeout=timeout_seconds, context=context) as response:
                return ExperimentalHttpResponse(
                    status_code=response.status,
                    body=response.read(),
                    content_type=response.headers.get("content-type"),
                )
        except HTTPError as exc:
            body = exc.read() if exc.fp is not None else b""
            return ExperimentalHttpResponse(
                status_code=exc.code,
                body=body,
                content_type=exc.headers.get("content-type") if exc.headers else None,
            )
        except (URLError, TimeoutError, OSError) as exc:
            raise ExperimentalHttpTransportError(
                "experimental record HTTP transport failed"
            ) from exc


class ExperimentalRecordHttpAdapter:
    """Fetch one record through the verified GET-only experimental API."""

    def __init__(
        self,
        settings: ExperimentalHttpTransportSettings,
        client: ExperimentalReadOnlyHttpClient | None = None,
        envelope_adapter: CallerSuppliedExperimentalEnvelopeAdapter | None = None,
    ) -> None:
        self._settings = settings
        self._client = client or ExperimentalReadOnlyHttpClient()
        self._envelope_adapter = envelope_adapter or CallerSuppliedExperimentalEnvelopeAdapter()

    def fetch_record(self, record_id: str) -> ExperimentalConsumerSnapshot:
        url = f"{self._settings.base_url}/vnext/experimental/records/{record_id}"
        headers = {"Accept": "application/json"}
        if self._settings.bearer_token:
            headers["Authorization"] = f"Bearer {self._settings.bearer_token}"

        response = self._client.get(
            url=url,
            headers=headers,
            timeout_seconds=self._settings.timeout_seconds,
            verify_tls=self._settings.verify_tls,
        )
        if response.status_code == 404:
            raise ExperimentalHttpNotFoundError(
                f"experimental record not found: {record_id}"
            )
        if response.status_code < 200 or response.status_code >= 300:
            raise ExperimentalHttpResponseError(
                f"experimental record request failed with status {response.status_code}"
            )

        try:
            payload: Any = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExperimentalHttpDecodeError(
                "response is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise ExperimentalHttpDecodeError("response JSON must be an object")

        try:
            return self._envelope_adapter.adapt(payload)
        except (ValueError, TypeError) as exc:
            raise ExperimentalHttpDecodeError(
                "response does not match the experimental record envelope"
            ) from exc
