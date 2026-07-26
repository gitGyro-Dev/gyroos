from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.security import require_runtime_bearer

from .experimental_api import (
    ExperimentalApiError,
    ExperimentalRecordCreateRequest,
    ExperimentalRecordListResponse,
    ExperimentalRecordResponse,
    experimental_api_settings,
)
from .experimental_api_provider import get_experimental_repository
from .experimental_repository import ExperimentalRecordRepository


router = APIRouter(
    prefix="/vnext/experimental",
    tags=["vNext Experimental"],
    dependencies=[Depends(require_runtime_bearer)],
)


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


@router.post(
    "/records",
    response_model=ExperimentalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_record(
    request: ExperimentalRecordCreateRequest,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    stored = repository.save(request.to_envelope())
    return ExperimentalRecordResponse(record=stored)


@router.get("/records/{record_id}", response_model=ExperimentalRecordResponse)
def get_experimental_record(
    record_id: str,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    record = repository.get(record_id)
    if record is None:
        return experimental_error(
            404,
            code="GYRO_VNEXT_EXPERIMENTAL_RECORD_NOT_FOUND",
            message=f"Experimental record not found: {record_id}",
            category="NOT_FOUND",
            phase="EXPERIMENTAL_RECORD_RETRIEVAL",
        )
    return ExperimentalRecordResponse(record=record)


@router.get("/records", response_model=ExperimentalRecordListResponse)
def list_experimental_records(
    process_id: str | None = Query(default=None),
    record_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1),
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    bounded_limit = min(limit, experimental_api_settings.max_list_results)
    records = repository.list(process_id=process_id, record_type=record_type)[:bounded_limit]
    return ExperimentalRecordListResponse(records=records, count=len(records))


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experimental_record(
    record_id: str,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    deleted = repository.delete(record_id)
    if not deleted:
        return experimental_error(
            404,
            code="GYRO_VNEXT_EXPERIMENTAL_RECORD_NOT_FOUND",
            message=f"Experimental record not found: {record_id}",
            category="NOT_FOUND",
            phase="EXPERIMENTAL_RECORD_DELETE",
        )
    return None
