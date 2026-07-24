from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .settings import settings


def require_runtime_bearer(
    authorization: str | None = Header(default=None),
) -> None:
    """Require one configured bearer token for protected Runtime endpoints."""
    if not settings.authentication_required:
        return

    scheme, separator, credential = (authorization or "").partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expected = settings.api_bearer_token or ""
    if not secrets.compare_digest(credential, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
