from __future__ import annotations

import concurrent.futures
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models import LoopStepRequest
from app.runtime import ProcessExecutor
from app.sqlite_repository import SQLiteStore
from tests.test_bounded_api import base_request as api_base_request
from tests.test_sqlite_repository import base_request as sqlite_base_request


def _post_step(index: int) -> tuple[int, str]:
    payload = api_base_request(
        request_id=f"load_http_{index}",
        loop_id=f"load_http_loop_{index}",
    )
    with TestClient(app) as client:
        response = client.post("/loop/step", json=payload)
    return response.status_code, response.json().get("process_id", "")


def test_concurrent_http_requests_complete_without_partial_results() -> None:
    request_count = 24
    started = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(_post_step, range(request_count)))

    elapsed = time.monotonic() - started
    statuses = [status for status, _ in results]
    process_ids = [process_id for _, process_id in results]

    assert statuses == [200] * request_count
    assert len(set(process_ids)) == request_count
    assert all(process_ids)
    assert elapsed < 15.0


def _publish_sqlite(database: Path, index: int) -> str:
    request = LoopStepRequest.model_validate(
        sqlite_base_request(
            request_id=f"load_sqlite_{index}",
            loop_id=f"load_sqlite_loop_{index}",
        )
    )
    store = SQLiteStore(database, timeout_seconds=10.0)
    return ProcessExecutor(store).execute(request).process_id


def test_concurrent_sqlite_publications_preserve_repository_integrity(
    tmp_path: Path,
) -> None:
    database = tmp_path / "load.db"
    SQLiteStore(database)
    publication_count = 20
    started = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        process_ids = list(
            pool.map(lambda index: _publish_sqlite(database, index), range(publication_count))
        )

    elapsed = time.monotonic() - started
    verification_store = SQLiteStore(database)

    assert len(set(process_ids)) == publication_count
    assert all(verification_store.get_process(process_id) is not None for process_id in process_ids)
    assert verification_store.get_database_schema_version() == "1"

    with verification_store._connect() as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        process_count = connection.execute(
            "SELECT COUNT(*) FROM runtime_records WHERE record_type = 'LoopStepResult'"
        ).fetchone()[0]
        scope_count = connection.execute("SELECT COUNT(*) FROM current_scope").fetchone()[0]
        idempotency_count = connection.execute(
            "SELECT COUNT(*) FROM idempotency_entries"
        ).fetchone()[0]

    assert integrity == "ok"
    assert process_count == publication_count
    assert scope_count == publication_count
    assert idempotency_count == publication_count
    assert elapsed < 20.0


def test_sustained_sequential_publication_remains_reconstructable(tmp_path: Path) -> None:
    database = tmp_path / "sustained.db"
    store = SQLiteStore(database)
    executor = ProcessExecutor(store)
    process_ids: list[str] = []

    for index in range(100):
        request = LoopStepRequest.model_validate(
            sqlite_base_request(
                request_id=f"sustained_{index}",
                loop_id="sustained_loop",
            )
        )
        process_ids.append(executor.execute(request).process_id)

    restarted = SQLiteStore(database)
    history = restarted.list_process_history(loop_id="sustained_loop", limit=100)

    assert len(process_ids) == 100
    assert len(set(process_ids)) == 100
    assert len(history.items) == 100
    assert history.next_cursor is None
    assert all(restarted.get_process(process_id) is not None for process_id in process_ids)
