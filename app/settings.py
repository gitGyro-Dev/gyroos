from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class RuntimeEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _read_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc


@dataclass(frozen=True)
class RuntimeSettings:
    environment: RuntimeEnvironment
    database_path: Path
    host: str
    port: int
    debug: bool
    sqlite_timeout_seconds: float
    authentication_required: bool
    api_bearer_token: str | None

    @classmethod
    def from_env(cls) -> "RuntimeSettings":
        raw_environment = os.getenv("GYROOS_ENV", RuntimeEnvironment.DEVELOPMENT.value)
        try:
            environment = RuntimeEnvironment(raw_environment.strip().lower())
        except ValueError as exc:
            allowed = ", ".join(item.value for item in RuntimeEnvironment)
            raise ValueError(f"GYROOS_ENV must be one of: {allowed}") from exc

        default_database = {
            RuntimeEnvironment.DEVELOPMENT: Path("runtime.db"),
            RuntimeEnvironment.TEST: Path(".runtime-test.db"),
            RuntimeEnvironment.PRODUCTION: Path(""),
        }[environment]

        raw_database_path = os.getenv("GYROOS_DATABASE_PATH")
        database_path = Path(raw_database_path) if raw_database_path else default_database

        default_authentication_required = environment == RuntimeEnvironment.PRODUCTION
        raw_token = os.getenv("GYROOS_API_BEARER_TOKEN")
        api_bearer_token = raw_token.strip() if raw_token and raw_token.strip() else None

        settings = cls(
            environment=environment,
            database_path=database_path,
            host=os.getenv("GYROOS_HOST", "127.0.0.1"),
            port=_read_int("GYROOS_PORT", 8000),
            debug=_read_bool(
                "GYROOS_DEBUG",
                environment == RuntimeEnvironment.DEVELOPMENT,
            ),
            sqlite_timeout_seconds=_read_float("GYROOS_SQLITE_TIMEOUT_SECONDS", 5.0),
            authentication_required=_read_bool(
                "GYROOS_AUTH_REQUIRED",
                default_authentication_required,
            ),
            api_bearer_token=api_bearer_token,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.host.strip():
            raise ValueError("GYROOS_HOST must not be empty")
        if self.port < 1 or self.port > 65535:
            raise ValueError("GYROOS_PORT must be between 1 and 65535")
        if self.sqlite_timeout_seconds <= 0:
            raise ValueError("GYROOS_SQLITE_TIMEOUT_SECONDS must be greater than zero")

        # Preserve the H-1 production configuration contract before applying
        # the H-2 authentication boundary. This keeps failures deterministic:
        # storage and debug configuration are validated before auth secrets.
        if self.environment == RuntimeEnvironment.PRODUCTION:
            if not str(self.database_path).strip() or str(self.database_path) == ".":
                raise ValueError("GYROOS_DATABASE_PATH is required in production")
            if self.debug:
                raise ValueError("GYROOS_DEBUG must be disabled in production")
            if not self.authentication_required:
                raise ValueError("GYROOS_AUTH_REQUIRED must be enabled in production")

        if self.authentication_required and not self.api_bearer_token:
            raise ValueError(
                "GYROOS_API_BEARER_TOKEN is required when authentication is enabled"
            )


settings = RuntimeSettings.from_env()
