from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .models import (
    ApiError,
    CurrentScopeState,
    LoopStepRequest,
    LoopStepResult,
    MemoryRecordEnvelope,
    ProcessHistoryPage,
    TrajectoryEdgePage,
)
from .repositories import store
from .repository_errors import (
    RepositoryBusyError,
    RepositoryIntegrityError,
    RepositorySchemaMismatch,
    RepositorySerializationError,
)
from .resource_limits import ResourceLimitMiddleware
from .runtime import ProcessExecutor, ReferenceError
from .security import require_runtime_bearer
from .settings import settings

app = FastAPI(
    title="GyroOS Bounded Runtime API",
    version="0.1.0",
    description="One HTTP request executes one bounded Gyro Process.",
    debug=settings.debug,
)
app.add_middleware(ResourceLimitMiddleware, runtime_settings=settings)
protected = APIRouter(dependencies=[Depends(require_runtime_bearer)])
executor = ProcessExecutor(store)


def api_error(
    status_code: int,
    *,
    code: str,
    message: str,
    category: str,
    phase: str,
    request_id: str | None = None,
    loop_id: str | None = None,
    retryable: bool = False,
) -> JSONResponse:
    payload = ApiError(
        error_id=f"error_{uuid4().hex}",
        error_code=code,
        message=message,
        category=category,
        phase=phase,
        request_id=request_id,
        loop_id=loop_id,
        retryable=retryable,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
def request_validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    return api_error(
        422,
        code="GYRO_API_VALIDATION_SCHEMA",
        message=str(exc),
        category="VALIDATION",
        phase="REQUEST_VALIDATION",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "runtime": "bounded",
        "version": app.version,
        "environment": settings.environment.value,
    }


@protected.post("/loop/step", response_model=LoopStepResult)
def loop_step(request: LoopStepRequest):
    try:
        return executor.execute(request)
    except ReferenceError as exc:
        return api_error(
            404,
            code="GYRO_API_NOT_FOUND_RECORD",
            message=str(exc),
            category="NOT_FOUND",
            phase="REFERENCE_RESOLUTION",
            request_id=request.request_id,
            loop_id=request.loop_id,
        )
    except RepositoryBusyError as exc:
        return api_error(
            503,
            code="GYRO_API_REPOSITORY_BUSY",
            message=str(exc),
            category="REPOSITORY",
            phase="PUBLICATION",
            request_id=request.request_id,
            loop_id=request.loop_id,
            retryable=True,
        )
    except RuntimeError as exc:
        message = str(exc)
        if "conflict" in message:
            return api_error(
                409,
                code="GYRO_API_IDENTITY_OR_SCOPE_CONFLICT",
                message=message,
                category="IDENTITY_CONFLICT",
                phase="EXECUTION_PRECONDITION",
                request_id=request.request_id,
                loop_id=request.loop_id,
            )
        return api_error(
            500,
            code="GYRO_API_INTERNAL_RUNTIME",
            message=message,
            category="INTERNAL",
            phase="PROCESS_EXECUTION",
            request_id=request.request_id,
            loop_id=request.loop_id,
        )
    except ValueError as exc:
        return api_error(
            422,
            code="GYRO_API_VALIDATION_OBJECT_RELATION",
            message=str(exc),
            category="VALIDATION",
            phase="CROSS_OBJECT_VALIDATION",
            request_id=request.request_id,
            loop_id=request.loop_id,
        )
    except Exception:  # pragma: no cover - defensive boundary
        return api_error(
            500,
            code="GYRO_API_INTERNAL_UNEXPECTED",
            message="Unexpected bounded Runtime failure.",
            category="INTERNAL",
            phase="PROCESS_EXECUTION",
            request_id=request.request_id,
            loop_id=request.loop_id,
            retryable=False,
        )


@protected.get("/loop/state/{loop_id}", response_model=CurrentScopeState)
def get_loop_state(loop_id: str):
    process_id = store.get_current_scope(loop_id)
    if process_id is None:
        return api_error(
            404,
            code="GYRO_API_NOT_FOUND_CURRENT_SCOPE",
            message=f"Current scope not found for loop_id={loop_id}",
            category="NOT_FOUND",
            phase="CURRENT_SCOPE_QUERY",
            loop_id=loop_id,
        )

    process = store.get_process(process_id)
    if process is None:
        error = RepositoryIntegrityError(
            f"current scope for loop_id={loop_id} references missing process_id={process_id}"
        )
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_INTEGRITY",
            message=str(error),
            category="REPOSITORY",
            phase="CURRENT_SCOPE_QUERY",
            loop_id=loop_id,
        )

    return CurrentScopeState(
        loop_id=loop_id,
        current_process_id=process_id,
        process=process,
    )


@protected.get("/loop/history/{loop_id}", response_model=ProcessHistoryPage)
def get_loop_history(
    loop_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
):
    try:
        return store.list_process_history(loop_id=loop_id, limit=limit, cursor=cursor)
    except ValueError as exc:
        return api_error(
            422,
            code="GYRO_API_VALIDATION_HISTORY_CURSOR",
            message=str(exc),
            category="VALIDATION",
            phase="PROCESS_HISTORY_QUERY",
            loop_id=loop_id,
        )
    except RepositoryIntegrityError as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_INTEGRITY",
            message=str(exc),
            category="REPOSITORY",
            phase="PROCESS_HISTORY_QUERY",
            loop_id=loop_id,
        )


@protected.get("/trajectory/{trajectory_ref}", response_model=TrajectoryEdgePage)
def get_trajectory(
    trajectory_ref: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
):
    try:
        return store.list_trajectory_edges(
            trajectory_ref=trajectory_ref,
            limit=limit,
            cursor=cursor,
        )
    except ValueError as exc:
        return api_error(
            422,
            code="GYRO_API_VALIDATION_TRAJECTORY_CURSOR",
            message=str(exc),
            category="VALIDATION",
            phase="TRAJECTORY_QUERY",
        )
    except RepositoryIntegrityError as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_INTEGRITY",
            message=str(exc),
            category="REPOSITORY",
            phase="TRAJECTORY_QUERY",
        )


@protected.get("/process/{process_id}", response_model=LoopStepResult)
def get_process(process_id: str):
    try:
        result = store.get_process(process_id)
    except RepositoryIntegrityError as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_INTEGRITY",
            message=str(exc),
            category="REPOSITORY",
            phase="PROCESS_RETRIEVAL",
        )
    if result is None:
        return api_error(
            404,
            code="GYRO_API_NOT_FOUND_PROCESS",
            message=f"Process not found: {process_id}",
            category="NOT_FOUND",
            phase="PROCESS_RETRIEVAL",
        )
    return result


@protected.get("/memory/record/{record_id}", response_model=MemoryRecordEnvelope)
def get_memory_record(record_id: str):
    try:
        record = store.get_record(record_id)
    except RepositorySchemaMismatch as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_SCHEMA_MISMATCH",
            message=str(exc),
            category="REPOSITORY",
            phase="MEMORY_RECORD_RECONSTRUCTION",
        )
    except RepositorySerializationError as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_RECONSTRUCTION",
            message=str(exc),
            category="REPOSITORY",
            phase="MEMORY_RECORD_RECONSTRUCTION",
        )
    except RepositoryIntegrityError as exc:
        return api_error(
            500,
            code="GYRO_API_REPOSITORY_INTEGRITY",
            message=str(exc),
            category="REPOSITORY",
            phase="MEMORY_RECORD_RECONSTRUCTION",
        )

    if record is None:
        return api_error(
            404,
            code="GYRO_API_NOT_FOUND_MEMORY_RECORD",
            message=f"Memory record not found: {record_id}",
            category="NOT_FOUND",
            phase="MEMORY_RECORD_RETRIEVAL",
        )

    return MemoryRecordEnvelope(
        record_id=record_id,
        record_type=type(record).__name__,
        record=record,
    )


app.include_router(protected)
