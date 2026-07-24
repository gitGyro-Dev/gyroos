from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Request

from .settings import RuntimeSettings, settings

_request_id: ContextVar[str | None] = ContextVar("gyroos_request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None) or _request_id.get()
        if request_id:
            payload["request_id"] = request_id
        for name in (
            "method",
            "path",
            "status_code",
            "duration_ms",
            "client_host",
            "error_code",
            "retryable",
        ):
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = value
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(runtime_settings: RuntimeSettings = settings) -> None:
    root = logging.getLogger()
    root.setLevel(runtime_settings.log_level.value)
    handler = logging.StreamHandler()
    if runtime_settings.json_logging:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
    root.handlers.clear()
    root.addHandler(handler)


class RequestDiagnosticsMiddleware:
    def __init__(self, app, *, logger_name: str = "gyroos.request") -> None:
        self.app = app
        self.logger = logging.getLogger(logger_name)

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        supplied = request.headers.get("x-request-id", "").strip()
        request_id = supplied[:128] if supplied else f"req_{uuid4().hex}"
        token = _request_id.set(request_id)
        started = time.perf_counter()
        status_code = 500

        async def send_with_request_id(message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii", "ignore")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            self.logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "client_host": request.client.host if request.client else "unknown",
                },
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            level = logging.WARNING if status_code >= 400 else logging.INFO
            self.logger.log(
                level,
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "client_host": request.client.host if request.client else "unknown",
                },
            )
        finally:
            _request_id.reset(token)
