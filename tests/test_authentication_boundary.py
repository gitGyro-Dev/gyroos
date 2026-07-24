from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings

client = TestClient(app)


def test_health_remains_public(monkeypatch) -> None:
    monkeypatch.setattr(settings, "authentication_required", True)
    monkeypatch.setattr(settings, "api_bearer_token", "test-secret")

    response = client.get("/health")

    assert response.status_code == 200


def test_protected_endpoint_rejects_missing_bearer(monkeypatch) -> None:
    monkeypatch.setattr(settings, "authentication_required", True)
    monkeypatch.setattr(settings, "api_bearer_token", "test-secret")

    response = client.get("/process/missing")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_rejects_invalid_bearer(monkeypatch) -> None:
    monkeypatch.setattr(settings, "authentication_required", True)
    monkeypatch.setattr(settings, "api_bearer_token", "test-secret")

    response = client.get(
        "/process/missing",
        headers={"Authorization": "Bearer wrong-secret"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_accepts_configured_bearer(monkeypatch) -> None:
    monkeypatch.setattr(settings, "authentication_required", True)
    monkeypatch.setattr(settings, "api_bearer_token", "test-secret")

    response = client.get(
        "/process/missing",
        headers={"Authorization": "Bearer test-secret"},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "GYRO_API_NOT_FOUND_PROCESS"


def test_authentication_disabled_profile_preserves_local_compatibility(monkeypatch) -> None:
    monkeypatch.setattr(settings, "authentication_required", False)
    monkeypatch.setattr(settings, "api_bearer_token", None)

    response = client.get("/process/missing")

    assert response.status_code == 404
    assert response.json()["error_code"] == "GYRO_API_NOT_FOUND_PROCESS"
