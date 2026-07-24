from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.security import authorize_bearer
from app.settings import RuntimeEnvironment, RuntimeSettings

client = TestClient(app)


def auth_settings(*, required: bool, token: str | None) -> RuntimeSettings:
    return RuntimeSettings(
        environment=RuntimeEnvironment.TEST,
        database_path=Path(".runtime-test.db"),
        host="127.0.0.1",
        port=8000,
        debug=False,
        sqlite_timeout_seconds=5.0,
        authentication_required=required,
        api_bearer_token=token,
        max_request_body_bytes=1_048_576,
        rate_limit_requests=120,
        rate_limit_window_seconds=60,
        max_concurrent_requests=32,
    )


def test_health_remains_public() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_authorization_rejects_missing_bearer() -> None:
    with pytest.raises(HTTPException) as exc_info:
        authorize_bearer(None, auth_settings(required=True, token="test-secret"))

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_authorization_rejects_invalid_bearer() -> None:
    with pytest.raises(HTTPException) as exc_info:
        authorize_bearer(
            "Bearer wrong-secret",
            auth_settings(required=True, token="test-secret"),
        )

    assert exc_info.value.status_code == 401


def test_authorization_accepts_configured_bearer() -> None:
    authorize_bearer(
        "Bearer test-secret",
        auth_settings(required=True, token="test-secret"),
    )


def test_authorization_disabled_profile_preserves_local_compatibility() -> None:
    authorize_bearer(None, auth_settings(required=False, token=None))
