from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .models import ApiError, LoopStepRequest, LoopStepResult
from .repositories import store
from .runtime import ProcessExecutor, ReferenceError

app = FastAPI(
    title="GyroOS Bounded Runtime API",
    version="0.1.0",
    description="One HTTP request executes one bounded Gyro Process.",
)
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


@app.exception_handler(ValidationError)
def validation_error_handler(_, exc: ValidationError) -> JSONResponse:
    return api_error(
        422,
        code="GYRO_API_VALIDATION_SCHEMA",
        message=str(exc),
        category="VALIDATION",
        phase="REQUEST_VALIDATION",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "runtime": "bounded", "version": app.version}


@app.post("/loop/step", response_model=LoopStepResult)
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
    except Exception as exc:  # pragma: no cover - defensive boundary
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


@app.get("/process/{process_id}", response_model=LoopStepResult)
def get_process(process_id: str):
    result = store.get_process(process_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Process not found")
    return result


@app.get("/memory/record/{record_id}")
def get_memory_record(record_id: str):
    record = store.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return record
