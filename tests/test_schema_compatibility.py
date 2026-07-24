from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.repository_errors import RepositorySchemaMismatch
from app.sqlite_repository import SCHEMA_VERSION, SQLiteStore


def create_legacy_schema(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE runtime_records (
                record_id TEXT PRIMARY KEY,
                record_type TEXT NOT NULL,
                process_id TEXT,
                loop_id TEXT,
                canonical_payload TEXT NOT NULL,
                canonical_digest TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                runtime_version TEXT NOT NULL,
                publication_id TEXT NOT NULL,
                publication_order INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE current_scope (
                loop_id TEXT PRIMARY KEY,
                process_id TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE idempotency_entries (
                loop_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                request_digest TEXT NOT NULL,
                process_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(loop_id, idempotency_key)
            );
            """
        )


def test_new_database_registers_current_schema_version(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "runtime.db")

    assert store.get_database_schema_version() == SCHEMA_VERSION


def test_legacy_database_is_validated_and_adopted(tmp_path: Path) -> None:
    database = tmp_path / "legacy.db"
    create_legacy_schema(database)

    store = SQLiteStore(database)

    assert store.get_database_schema_version() == SCHEMA_VERSION
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT metadata_value FROM schema_metadata WHERE metadata_key = ?",
            ("database_schema_version",),
        ).fetchone()
    assert row is not None
    assert row[0] == SCHEMA_VERSION


def test_unknown_database_schema_version_is_rejected(tmp_path: Path) -> None:
    database = tmp_path / "future.db"
    store = SQLiteStore(database)
    assert store.get_database_schema_version() == SCHEMA_VERSION

    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE schema_metadata SET metadata_value = ? WHERE metadata_key = ?",
            ("999", "database_schema_version"),
        )

    with pytest.raises(RepositorySchemaMismatch, match="unsupported database schema version"):
        SQLiteStore(database)


def test_incomplete_legacy_schema_is_rejected(tmp_path: Path) -> None:
    database = tmp_path / "incomplete.db"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE runtime_records(record_id TEXT PRIMARY KEY)"
        )

    with pytest.raises(RepositorySchemaMismatch, match="missing required tables"):
        SQLiteStore(database)


def test_legacy_schema_missing_required_column_is_rejected(tmp_path: Path) -> None:
    database = tmp_path / "missing-column.db"
    create_legacy_schema(database)
    with sqlite3.connect(database) as connection:
        connection.execute("ALTER TABLE current_scope RENAME TO current_scope_old")
        connection.execute(
            "CREATE TABLE current_scope(loop_id TEXT PRIMARY KEY)"
        )
        connection.execute("DROP TABLE current_scope_old")

    with pytest.raises(RepositorySchemaMismatch, match="missing required columns"):
        SQLiteStore(database)
