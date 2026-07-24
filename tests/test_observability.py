from __future__ import annotations

import json
import logging
from io import StringIO

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.observability import JsonFormatter, RequestDiagnosticsMiddleware


def create_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestDiagnosticsMiddleware, logger_name="gyroos.test.request")

    @app.get("/ok")
    def ok() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_request_id_is_generated_and_returned() -> None:
    response = create_client().get("/ok")

    assert response.status_code == 200
    assert response.headers["x-request-id"].startswith("req_")


def test_supplied_request_id_is_preserved() -> None:
    response = create_client().get(
        "/ok",
        headers={"X-Request-ID": "external-request-123"},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "external-request-123"


def test_json_formatter_emits_structured_fields_without_secrets() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("gyroos.test.formatter")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.info(
        "request_completed",
        extra={
            "request_id": "req_test",
            "method": "GET",
            "path": "/process/example",
            "status_code": 200,
            "duration_ms": 1.25,
            "client_host": "testclient",
        },
    )

    payload = json.loads(stream.getvalue())
    assert payload["event"] == "request_completed"
    assert payload["request_id"] == "req_test"
    assert payload["method"] == "GET"
    assert payload["path"] == "/process/example"
    assert payload["status_code"] == 200
    serialized = stream.getvalue()
    assert "authorization" not in serialized.lower()
    assert "bearer" not in serialized.lower()
    assert "api_bearer_token" not in serialized.lower()
    assert "database_path" not in serialized.lower()


def test_request_log_contains_completion_diagnostics(caplog) -> None:
    caplog.set_level(logging.INFO, logger="gyroos.test.request")

    response = create_client().get(
        "/ok",
        headers={"X-Request-ID": "diagnostic-request"},
    )

    assert response.status_code == 200
    records = [record for record in caplog.records if record.name == "gyroos.test.request"]
    assert len(records) == 1
    record = records[0]
    assert record.getMessage() == "request_completed"
    assert record.request_id == "diagnostic-request"
    assert record.method == "GET"
    assert record.path == "/ok"
    assert record.status_code == 200
    assert record.duration_ms >= 0
