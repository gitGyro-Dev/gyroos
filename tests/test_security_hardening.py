from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.settings import RuntimeEnvironment, RuntimeSettings


client = TestClient(app)


def production_settings(token: str) -> RuntimeSettings:
    return RuntimeSettings(
        environment=RuntimeEnvironment.PRODUCTION,
        database_path=Path("/var/lib/gyroos/runtime.db"),
        host="0.0.0.0",
        port=8080,
        debug=False,
        sqlite_timeout_seconds=5.0,
        authentication_required=True,
        api_bearer_token=token,
        max_request_body_bytes=1_048_576,
        rate_limit_requests=120,
        rate_limit_window_seconds=60,
        max_concurrent_requests=32,
    )


def test_production_rejects_short_bearer_token() -> None:
    settings = production_settings("too-short")
    with pytest.raises(ValueError, match="at least 32 characters"):
        settings.validate()


def test_production_rejects_placeholder_bearer_token() -> None:
    settings = production_settings("production-secret")
    with pytest.raises(ValueError, match="placeholder value"):
        settings.validate()


def test_runtime_settings_repr_excludes_bearer_token() -> None:
    token = "gyroos-production-token-0123456789abcdef"
    rendered = repr(production_settings(token))
    assert token not in rendered
    assert "api_bearer_token" not in rendered


@pytest.mark.parametrize("path", ["/health", "/process/missing-process"])
def test_security_headers_are_applied_to_responses(path: str) -> None:
    response = client.get(path)

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )
