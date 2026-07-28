from __future__ import annotations

from fastapi.responses import JSONResponse

from .experimental_api import ExperimentalApiError


def experimental_error(
    status_code: int,
    *,
    code: str,
    message: str,
    category: str,
    phase: str,
    retryable: bool = False,
) -> JSONResponse:
    payload = ExperimentalApiError(
        error_code=code,
        message=message,
        category=category,
        phase=phase,
        retryable=retryable,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))
