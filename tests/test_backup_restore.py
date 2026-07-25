from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.backup import create_backup, restore_backup
from app.models import LoopStepRequest
from app.repository_errors import RepositoryIntegrityError
from app.runtime import ProcessExecutor
from app.sqlite_repository import SCHEMA_VERSION, SQLiteStore
from tests.test_sqlite_repository import base_request


def test_backup_and_restore_round_trip_preserves_runtime_records(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    backup = tmp_path / "backups" / "runtime-backup.db"
    restored = tmp_path / "restored" / "runtime.db"

    request = LoopStepRequest.model_validate(base_request())
    result = ProcessExecutor(SQLiteStore(source)).execute(request)

    backup_result = create_backup(source, backup)
    restore_result = restore_backup(backup, restored)

    assert backup_result.schema_version == SCHEMA_VERSION
    assert restore_result.schema_version == SCHEMA_VERSION
    assert backup_result.record_count == restore_result.record_count
    assert backup_result.record_count > 0

    restored_store = SQLiteStore(restored)
    restored_process = restored_store.get_process(result.process_id)
    assert restored_process is not None
    assert restored_process.process_id == result.process_id
    assert restored_store.get_current_scope(request.loop_id) == result.process_id


def test_backup_refuses_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    backup = tmp_path / "runtime-backup.db"
    SQLiteStore(source)
    backup.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="backup file already exists"):
        create_backup(source, backup)


def test_restore_refuses_existing_destination_without_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    backup = tmp_path / "runtime-backup.db"
    destination = tmp_path / "restored.db"
    SQLiteStore(source)
    create_backup(source, backup)
    destination.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="restore destination already exists"):
        restore_backup(backup, destination)


def test_restore_overwrite_replaces_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    backup = tmp_path / "runtime-backup.db"
    destination = tmp_path / "restored.db"
    SQLiteStore(source)
    create_backup(source, backup)
    destination.write_bytes(b"invalid")

    result = restore_backup(backup, destination, overwrite=True)

    assert result.restored_path == destination.resolve()
    assert SQLiteStore(destination).get_database_schema_version() == SCHEMA_VERSION


def test_restore_rejects_corrupt_backup_without_replacing_destination(tmp_path: Path) -> None:
    backup = tmp_path / "corrupt.db"
    destination = tmp_path / "restored.db"
    backup.write_bytes(b"not a sqlite database")
    destination.write_bytes(b"preserve-me")

    with pytest.raises(RepositoryIntegrityError):
        restore_backup(backup, destination, overwrite=True)

    assert destination.read_bytes() == b"preserve-me"


def test_backup_refuses_source_destination_identity(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    SQLiteStore(source)

    with pytest.raises(ValueError, match="backup path must differ"):
        create_backup(source, source)


def test_restore_validates_database_integrity(tmp_path: Path) -> None:
    source = tmp_path / "runtime.db"
    backup = tmp_path / "runtime-backup.db"
    destination = tmp_path / "restored.db"
    SQLiteStore(source)
    create_backup(source, backup)

    with sqlite3.connect(backup) as connection:
        connection.execute(
            "UPDATE schema_metadata SET metadata_value = '999' "
            "WHERE metadata_key = 'database_schema_version'"
        )

    with pytest.raises(Exception, match="unsupported database schema version"):
        restore_backup(backup, destination)
