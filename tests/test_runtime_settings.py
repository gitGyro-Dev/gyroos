from __future__ import annotations

from pathlib import Path

import pytest

from app.settings import RuntimeEnvironment, RuntimeSettings
from app.sqlite_repository import SQLiteStore


def clear_runtime_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GYROOS_ENV",
        "GYROOS_DATABASE_PATH",
        "GYROOS_HOST",
        "GYROOS_PORT",
        "GYROOS_DEBUG",
        "GYROOS_SQLITE_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)


def test_development_profile_uses_safe_local_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_runtime_env(monkeypatch)

    settings = RuntimeSettings.from_env()

    assert settings.environment == RuntimeEnvironment.DEVELOPMENT
    assert settings.database_path == Path("runtime.db")
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.debug is True
    assert settings.sqlite_timeout_seconds == 5.0


def test_test_profile_has_isolated_default_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_runtime_env(monkeypatch)
    monkeypatch.setenv("GYROOS_ENV", "test")

    settings = RuntimeSettings.from_env()

    assert settings.environment == RuntimeEnvironment.TEST
    assert settings.database_path == Path(".runtime-test.db")
    assert settings.debug is False


def test_production_requires_explicit_persistent_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_runtime_env(monkeypatch)
    monkeypatch.setenv("GYROOS_ENV", "production")

    with pytest.raises(ValueError, match="GYROOS_DATABASE_PATH is required"):
        RuntimeSettings.from_env()


def test_production_rejects_debug_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_runtime_env(monkeypatch)
    monkeypatch.setenv("GYROOS_ENV", "production")
    monkeypatch.setenv("GYROOS_DATABASE_PATH", "/var/lib/gyroos/runtime.db")
    monkeypatch.setenv("GYROOS_DEBUG", "true")

    with pytest.raises(ValueError, match="GYROOS_DEBUG must be disabled"):
        RuntimeSettings.from_env()


def test_production_accepts_explicit_safe_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_runtime_env(monkeypatch)
    monkeypatch.setenv("GYROOS_ENV", "production")
    monkeypatch.setenv("GYROOS_DATABASE_PATH", "/var/lib/gyroos/runtime.db")
    monkeypatch.setenv("GYROOS_HOST", "0.0.0.0")
    monkeypatch.setenv("GYROOS_PORT", "8080")
    monkeypatch.setenv("GYROOS_DEBUG", "false")
    monkeypatch.setenv("GYROOS_SQLITE_TIMEOUT_SECONDS", "12.5")

    settings = RuntimeSettings.from_env()

    assert settings.environment == RuntimeEnvironment.PRODUCTION
    assert settings.database_path == Path("/var/lib/gyroos/runtime.db")
    assert settings.host == "0.0.0.0"
    assert settings.port == 8080
    assert settings.debug is False
    assert settings.sqlite_timeout_seconds == 12.5


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("GYROOS_ENV", "unknown", "GYROOS_ENV must be one of"),
        ("GYROOS_PORT", "zero", "GYROOS_PORT must be an integer"),
        ("GYROOS_PORT", "70000", "GYROOS_PORT must be between"),
        ("GYROOS_DEBUG", "sometimes", "GYROOS_DEBUG must be a boolean"),
        (
            "GYROOS_SQLITE_TIMEOUT_SECONDS",
            "0",
            "GYROOS_SQLITE_TIMEOUT_SECONDS must be greater than zero",
        ),
    ],
)
def test_invalid_environment_values_fail_fast(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
    message: str,
) -> None:
    clear_runtime_env(monkeypatch)
    monkeypatch.setenv(name, value)

    with pytest.raises(ValueError, match=message):
        RuntimeSettings.from_env()


def test_sqlite_store_accepts_configured_timeout(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "configured.db", timeout_seconds=9.25)
    assert store.timeout_seconds == 9.25


def test_sqlite_store_rejects_non_positive_timeout(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be greater than zero"):
        SQLiteStore(tmp_path / "invalid.db", timeout_seconds=0)
