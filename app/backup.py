from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from .repository_errors import RepositoryIntegrityError, RepositorySchemaMismatch
from .sqlite_repository import SCHEMA_VERSION, SQLiteStore


@dataclass(frozen=True)
class BackupResult:
    source_path: Path
    backup_path: Path
    schema_version: str
    record_count: int


@dataclass(frozen=True)
class RestoreResult:
    backup_path: Path
    restored_path: Path
    schema_version: str
    record_count: int


def _resolved(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _validate_database(path: Path, *, timeout_seconds: float) -> tuple[str, int]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"database file not found: {path}")

    try:
        with sqlite3.connect(path, timeout=timeout_seconds) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or str(integrity[0]).lower() != "ok":
                raise RepositoryIntegrityError(
                    f"SQLite integrity check failed for {path}: {integrity}"
                )
    except sqlite3.DatabaseError as exc:
        raise RepositoryIntegrityError(f"failed to open SQLite database: {path}") from exc

    store = SQLiteStore(path, timeout_seconds=timeout_seconds)
    schema_version = store.get_database_schema_version()
    if schema_version != SCHEMA_VERSION:
        raise RepositorySchemaMismatch(
            f"unsupported database schema version {schema_version}; runtime supports {SCHEMA_VERSION}"
        )

    with sqlite3.connect(path, timeout=timeout_seconds) as connection:
        row = connection.execute("SELECT COUNT(*) FROM runtime_records").fetchone()
    return schema_version, 0 if row is None else int(row[0])


def create_backup(
    source_path: str | Path,
    backup_path: str | Path,
    *,
    timeout_seconds: float = 5.0,
) -> BackupResult:
    source = _resolved(source_path)
    destination = _resolved(backup_path)

    if source == destination:
        raise ValueError("backup path must differ from source database path")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"source database file not found: {source}")
    if destination.exists():
        raise FileExistsError(f"backup file already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(source, timeout=timeout_seconds) as source_connection:
            with sqlite3.connect(destination, timeout=timeout_seconds) as backup_connection:
                source_connection.backup(backup_connection)
        schema_version, record_count = _validate_database(
            destination,
            timeout_seconds=timeout_seconds,
        )
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return BackupResult(
        source_path=source,
        backup_path=destination,
        schema_version=schema_version,
        record_count=record_count,
    )


def restore_backup(
    backup_path: str | Path,
    restored_path: str | Path,
    *,
    timeout_seconds: float = 5.0,
    overwrite: bool = False,
) -> RestoreResult:
    source = _resolved(backup_path)
    destination = _resolved(restored_path)

    if source == destination:
        raise ValueError("restore path must differ from backup path")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"backup file not found: {source}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"restore destination already exists: {destination}")

    schema_version, record_count = _validate_database(
        source,
        timeout_seconds=timeout_seconds,
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(
            prefix=f".{destination.name}.",
            suffix=".restore.tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)

        with sqlite3.connect(source, timeout=timeout_seconds) as source_connection:
            with sqlite3.connect(temporary_path, timeout=timeout_seconds) as target_connection:
                source_connection.backup(target_connection)

        restored_schema, restored_count = _validate_database(
            temporary_path,
            timeout_seconds=timeout_seconds,
        )
        if restored_schema != schema_version or restored_count != record_count:
            raise RepositoryIntegrityError(
                "restored database verification does not match backup metadata"
            )

        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return RestoreResult(
        backup_path=source,
        restored_path=destination,
        schema_version=schema_version,
        record_count=record_count,
    )
