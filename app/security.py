from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .settings import RuntimeSettings, settings


def authorize_bearer(authorization: str | None, runtime_settings: RuntimeSettings) -> None:
    """Validate one configured bearer token without mutating Runtime state."""
    if not runtime_settings.authentication_required:
        return

    scheme, separator, credential = (authorization or "").partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expected = runtime_settings.api_bearer_token or ""
    if not secrets.compare_digest(credential, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_runtime_bearer(
    authorization: str | None = Header(default=None),
) -> None:
    """FastAPI dependency for protected Runtime endpoints."""
    authorize_bearer(authorization, settings)
