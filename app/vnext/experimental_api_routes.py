from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.security import require_runtime_bearer
from .consumer_compatibility import (
    ExperimentalConsumerCompatibilityRequest,
    ExperimentalConsumerCompatibilityResult,
)
from .consumer_compatibility_service import (
    ExperimentalCompatibilityError,
    ExperimentalConsumerCompatibilityService,
)
from .experimental_api import (
    ExperimentalRecordCreateRequest,
    ExperimentalRecordListResponse,
    ExperimentalRecordResponse,
    experimental_api_settings,
)
from .experimental_api_provider import get_experimental_repository
from .experimental_error_response import experimental_error
from .experimental_repository import ExperimentalRecordRepository
from .inspection_api_routes import inspection_router


router = APIRouter(
    prefix="/vnext/experimental",
    tags=["vNext Experimental"],
    dependencies=[Depends(require_runtime_bearer)],
)
compatibility_service = ExperimentalConsumerCompatibilityService()


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


@router.post(
    "/compatibility/check",
    response_model=ExperimentalConsumerCompatibilityResult,
)
def check_experimental_consumer_compatibility(
    request: ExperimentalConsumerCompatibilityRequest,
):
    try:
        return compatibility_service.check(request)
    except ExperimentalCompatibilityError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPATIBILITY_INVALID_VERSION",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPATIBILITY_CHECK",
        )


router.include_router(inspection_router)
