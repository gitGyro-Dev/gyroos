from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.resource_limits import FixedWindowRateLimiter, ResourceLimitMiddleware
from app.settings import RuntimeEnvironment, RuntimeSettings


def settings_for_limits(
    *,
    max_request_body_bytes: int = 32,
    rate_limit_requests: int = 2,
    rate_limit_window_seconds: int = 60,
    max_concurrent_requests: int = 2,
) -> RuntimeSettings:
    return RuntimeSettings(
        environment=RuntimeEnvironment.TEST,
        database_path=Path(":memory:"),
        host="127.0.0.1",
        port=8000,
        debug=False,
        sqlite_timeout_seconds=5.0,
        authentication_required=False,
        api_bearer_token=None,
        max_request_body_bytes=max_request_body_bytes,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window_seconds=rate_limit_window_seconds,
        max_concurrent_requests=max_concurrent_requests,
    )


def create_test_client(runtime_settings: RuntimeSettings) -> TestClient:
    app = FastAPI()
    app.add_middleware(ResourceLimitMiddleware, runtime_settings=runtime_settings)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/echo")
    async def echo(payload: dict) -> dict:
        return payload

    return TestClient(app)


def test_request_body_over_limit_returns_413() -> None:
    client = create_test_client(settings_for_limits(max_request_body_bytes=16))

    response = client.post("/echo", json={"payload": "x" * 64})

    assert response.status_code == 413
    assert response.json()["error_code"] == "GYRO_API_REQUEST_TOO_LARGE"
    assert response.json()["phase"] == "REQUEST_ADMISSION"


def test_request_within_limit_reaches_endpoint() -> None:
    client = create_test_client(settings_for_limits(max_request_body_bytes=128))

    response = client.post("/echo", json={"ok": True})

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_rate_limit_returns_429_and_retry_after() -> None:
    client = create_test_client(settings_for_limits(rate_limit_requests=2))

    assert client.post("/echo", json={"index": 1}).status_code == 200
    assert client.post("/echo", json={"index": 2}).status_code == 200
    response = client.post("/echo", json={"index": 3})

    assert response.status_code == 429
    assert response.json()["error_code"] == "GYRO_API_RATE_LIMITED"
    assert int(response.headers["retry-after"]) >= 1


def test_health_is_excluded_from_resource_limits() -> None:
    client = create_test_client(
        settings_for_limits(max_request_body_bytes=1, rate_limit_requests=1)
    )

    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200


@pytest.mark.asyncio
async def test_fixed_window_limiter_expires_old_entries() -> None:
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=10)

    allowed, retry_after = await limiter.allow("client", now=100.0)
    assert allowed is True
    assert retry_after == 0

    allowed, retry_after = await limiter.allow("client", now=101.0)
    assert allowed is False
    assert retry_after >= 1

    allowed, retry_after = await limiter.allow("client", now=111.0)
    assert allowed is True
    assert retry_after == 0
