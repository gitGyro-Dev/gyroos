from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.models import LoopStepRequest
from app.repository_errors import RepositoryBusyError
from app.runtime import ProcessExecutor
from app.sqlite_repository import SQLiteStore
from tests.test_sqlite_repository import base_request


def test_sqlite_store_enables_wal_and_busy_timeout(tmp_path: Path) -> None:
    database = tmp_path / "runtime.db"
    store = SQLiteStore(database, timeout_seconds=0.25)

    with store._connect() as connection:
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        busy_timeout = connection.execute("PRAGMA busy_timeout").fetchone()[0]

    assert str(journal_mode).lower() == "wal"
    assert busy_timeout == 250


def test_locked_database_is_translated_to_repository_busy(tmp_path: Path) -> None:
    database = tmp_path / "runtime.db"
    store = SQLiteStore(database, timeout_seconds=0.05)
    request = LoopStepRequest.model_validate(
        base_request(request_id="locked_request", loop_id="locked_loop")
    )

    lock_connection = sqlite3.connect(database, timeout=0.05)
    lock_connection.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(RepositoryBusyError, match="locked"):
            ProcessExecutor(store).execute(request)
    finally:
        lock_connection.rollback()
        lock_connection.close()

    verification = SQLiteStore(database)
    assert verification.get_current_scope(request.loop_id) is None
    assert verification.get_idempotent(
        request.loop_id,
        request.idempotency_key or "",
    ) is None


def test_write_succeeds_after_lock_release(tmp_path: Path) -> None:
    database = tmp_path / "runtime.db"
    store = SQLiteStore(database, timeout_seconds=0.05)
    request = LoopStepRequest.model_validate(
        base_request(request_id="released_request", loop_id="released_loop")
    )

    lock_connection = sqlite3.connect(database, timeout=0.05)
    lock_connection.execute("BEGIN IMMEDIATE")
    lock_connection.rollback()
    lock_connection.close()

    result = ProcessExecutor(store).execute(request)

    assert store.get_current_scope(request.loop_id) == result.process_id
