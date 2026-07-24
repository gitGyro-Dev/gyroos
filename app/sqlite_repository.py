from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, TypeAlias

from pydantic import BaseModel, ValidationError

from .models import (
    BoundaryEvidence,
    BoundaryStateRecord,
    ContextEvidence,
    DeferredRelationRecord,
    LoopStepResult,
    OperatorResponse,
    ProcessHistoryItem,
    ProcessHistoryPage,
    RuntimeContinuityResult,
    SliceDone,
    StabilityResult,
    TrajectoryEdge,
    TrajectoryEdgePage,
    VoidEvidence,
)
from .repository_errors import (
    IdempotencyConflict,
    RecordIdentityCollision,
    RepositoryBusyError,
    RepositoryIntegrityError,
    RepositorySchemaMismatch,
    RepositorySerializationError,
)

CanonicalRecord: TypeAlias = (
    LoopStepResult
    | SliceDone
    | StabilityResult
    | OperatorResponse
    | RuntimeContinuityResult
    | BoundaryEvidence
    | BoundaryStateRecord
    | ContextEvidence
    | VoidEvidence
    | DeferredRelationRecord
    | TrajectoryEdge
)

SCHEMA_VERSION = "1"
RUNTIME_VERSION = "priority-h1"
MAX_HISTORY_LIMIT = 100
DEFAULT_HISTORY_LIMIT = 20
DEFAULT_SQLITE_TIMEOUT_SECONDS = 5.0
_SCHEMA_METADATA_KEY = "database_schema_version"
_REQUIRED_TABLES = {
    "runtime_records",
    "current_scope",
    "idempotency_entries",
}

_RECORD_REGISTRY: dict[str, type[BaseModel]] = {
    "LoopStepResult": LoopStepResult,
    "SliceDone": SliceDone,
    "StabilityResult": StabilityResult,
    "OperatorResponse": OperatorResponse,
    "RuntimeContinuityResult": RuntimeContinuityResult,
    "BoundaryEvidence": BoundaryEvidence,
    "BoundaryStateRecord": BoundaryStateRecord,
    "ContextEvidence": ContextEvidence,
    "VoidEvidence": VoidEvidence,
    "DeferredRelationRecord": DeferredRelationRecord,
    "TrajectoryEdge": TrajectoryEdge,
}

_RECORD_ID_FIELDS: dict[type[BaseModel], str] = {
    LoopStepResult: "process_id",
    SliceDone: "slice_id",
    StabilityResult: "stability_result_id",
    OperatorResponse: "operator_response_id",
    RuntimeContinuityResult: "continuity_result_id",
    BoundaryEvidence: "boundary_evidence_id",
    BoundaryStateRecord: "boundary_state_record_id",
    ContextEvidence: "context_evidence_id",
    VoidEvidence: "void_evidence_id",
    DeferredRelationRecord: "deferred_relation_record_id",
    TrajectoryEdge: "trajectory_edge_id",
}


def _canonical_json(record: BaseModel) -> str:
    try:
        payload = record.model_dump(mode="json")
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise RepositorySerializationError(
            f"failed to serialize {type(record).__name__}"
        ) from exc


def _digest(payload_json: str) -> str:
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _record_id(record: CanonicalRecord) -> str:
    field_name = _RECORD_ID_FIELDS.get(type(record))
    if field_name is None:
        raise RepositorySerializationError(
            f"unsupported canonical record type: {type(record).__name__}"
        )
    value = getattr(record, field_name, None)
    if not value:
        raise RepositorySerializationError(
            f"canonical record {type(record).__name__} has no value for {field_name}"
        )
    return str(value)


def _record_type(record: CanonicalRecord) -> str:
    name = type(record).__name__
    if name not in _RECORD_REGISTRY:
        raise RepositorySerializationError(f"unsupported canonical record type: {name}")
    return name


def _collect_records(result: LoopStepResult) -> list[CanonicalRecord]:
    records: list[CanonicalRecord] = [
        result,
        result.slice_done,
        result.stability,
        result.operator_response,
        result.continuity,
        *result.slice_done.boundary_evidence,
        *result.slice_done.boundary_state_records,
        *result.slice_done.context_evidence,
        *result.slice_done.void_evidence,
        *result.trajectory_edges,
    ]
    if result.deferred_relation_record is not None:
        records.append(result.deferred_relation_record)

    record_ids = [_record_id(record) for record in records]
    if len(record_ids) != len(set(record_ids)):
        duplicates = sorted(
            record_id for record_id in set(record_ids) if record_ids.count(record_id) > 1
        )
        raise RecordIdentityCollision(
            f"duplicate record identities in publication group: {duplicates}"
        )
    return records


def _decode_cursor(cursor: str | None, *, label: str = "history") -> int:
    if cursor is None:
        return 0
    try:
        offset = int(cursor)
    except ValueError as exc:
        raise ValueError(f"{label} cursor must be a non-negative integer offset") from exc
    if offset < 0:
        raise ValueError(f"{label} cursor must be a non-negative integer offset")
    return offset


def _history_item(result: LoopStepResult) -> ProcessHistoryItem:
    return ProcessHistoryItem(
        process_id=result.process_id,
        request_id=result.request_id,
        loop_id=result.loop_id,
        completed_at=result.completed_at,
        stability_status=result.stability.status,
        stability_value=result.stability.value,
        operator_response=result.operator_response.response_type,
        continuity_type=result.continuity.continuity_type,
    )


def _matches_trajectory_ref(edge: TrajectoryEdge, trajectory_ref: str) -> bool:
    return trajectory_ref in {
        edge.relation_ref,
        edge.source_ref,
        edge.target_ref,
        edge.parent_process_ref,
    }


def _is_busy_error(exc: sqlite3.DatabaseError) -> bool:
    message = str(exc).lower()
    return "database is locked" in message or "database is busy" in message


class SQLiteStore:
    """SQLite-backed Runtime repository for the bounded Priority H prototype."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        timeout_seconds: float = DEFAULT_SQLITE_TIMEOUT_SECONDS,
        failure_injector: Callable[[str, int], None] | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self.database_path = str(database_path)
        self.timeout_seconds = float(timeout_seconds)
        self._failure_injector = failure_injector
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.timeout_seconds,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        if self.database_path != ":memory:":
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            existing_tables = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            legacy_schema_present = bool(existing_tables & _REQUIRED_TABLES)

            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runtime_records (
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

                CREATE TABLE IF NOT EXISTS current_scope (
                    loop_id TEXT PRIMARY KEY,
                    process_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS idempotency_entries (
                    loop_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    request_digest TEXT NOT NULL,
                    process_id TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(loop_id, idempotency_key)
                );

                CREATE TABLE IF NOT EXISTS schema_metadata (
                    metadata_key TEXT PRIMARY KEY,
                    metadata_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            row = connection.execute(
                "SELECT metadata_value FROM schema_metadata WHERE metadata_key = ?",
                (_SCHEMA_METADATA_KEY,),
            ).fetchone()
            if row is None:
                if legacy_schema_present:
                    self._validate_legacy_schema(connection)
                connection.execute(
                    """
                    INSERT INTO schema_metadata(metadata_key, metadata_value)
                    VALUES (?, ?)
                    """,
                    (_SCHEMA_METADATA_KEY, SCHEMA_VERSION),
                )
            else:
                stored_version = str(row["metadata_value"])
                if stored_version != SCHEMA_VERSION:
                    raise RepositorySchemaMismatch(
                        "unsupported database schema version "
                        f"{stored_version}; runtime supports {SCHEMA_VERSION}"
                    )

            connection.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_runtime_records_process
                    ON runtime_records(process_id, publication_order);

                CREATE INDEX IF NOT EXISTS idx_runtime_records_loop
                    ON runtime_records(loop_id, publication_order);

                CREATE INDEX IF NOT EXISTS idx_runtime_records_type_publication
                    ON runtime_records(record_type, publication_id, publication_order);
                """
            )

    def _validate_legacy_schema(self, connection: sqlite3.Connection) -> None:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        missing_tables = sorted(_REQUIRED_TABLES - tables)
        if missing_tables:
            raise RepositorySchemaMismatch(
                f"legacy database is missing required tables: {missing_tables}"
            )

        required_columns = {
            "runtime_records": {
                "record_id",
                "record_type",
                "process_id",
                "loop_id",
                "canonical_payload",
                "canonical_digest",
                "schema_version",
                "runtime_version",
                "publication_id",
                "publication_order",
            },
            "current_scope": {"loop_id", "process_id"},
            "idempotency_entries": {
                "loop_id",
                "idempotency_key",
                "request_digest",
                "process_id",
            },
        }
        for table, expected in required_columns.items():
            actual = {
                str(row[1])
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            missing = sorted(expected - actual)
            if missing:
                raise RepositorySchemaMismatch(
                    f"legacy table {table} is missing required columns: {missing}"
                )

    def get_database_schema_version(self) -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_value FROM schema_metadata WHERE metadata_key = ?",
                (_SCHEMA_METADATA_KEY,),
            ).fetchone()
        if row is None:
            raise RepositorySchemaMismatch("database schema version metadata is missing")
        return str(row["metadata_value"])

    def _inject_failure(self, phase: str, position: int) -> None:
        if self._failure_injector is not None:
            self._failure_injector(phase, position)

    def _reconstruct_row(self, row: sqlite3.Row, record_id: str) -> CanonicalRecord:
        if row["schema_version"] != SCHEMA_VERSION:
            raise RepositorySchemaMismatch(
                f"unsupported schema_version={row['schema_version']} for record {record_id}"
            )
        payload_json = str(row["canonical_payload"])
        if _digest(payload_json) != row["canonical_digest"]:
            raise RepositoryIntegrityError(
                f"canonical digest mismatch for record {record_id}"
            )
        model = _RECORD_REGISTRY.get(str(row["record_type"]))
        if model is None:
            raise RepositorySerializationError(
                f"unsupported record type: {row['record_type']}"
            )
        try:
            payload: dict[str, Any] = json.loads(payload_json)
            return model.model_validate(payload)  # type: ignore[return-value]
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RepositorySerializationError(
                f"failed to reconstruct record {record_id}"
            ) from exc

    def get_process(self, process_id: str) -> LoopStepResult | None:
        record = self.get_record(process_id)
        if record is None:
            return None
        if not isinstance(record, LoopStepResult):
            raise RepositoryIntegrityError(f"record {process_id} is not LoopStepResult")
        return record

    def get_record(self, record_id: str) -> CanonicalRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT record_type, canonical_payload, canonical_digest, schema_version
                FROM runtime_records
                WHERE record_id = ?
                """,
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        return self._reconstruct_row(row, record_id)

    def get_current_scope(self, loop_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT process_id FROM current_scope WHERE loop_id = ?",
                (loop_id,),
            ).fetchone()
        return None if row is None else str(row["process_id"])

    def get_idempotent(
        self,
        loop_id: str,
        key: str,
    ) -> tuple[str, LoopStepResult] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT request_digest, process_id
                FROM idempotency_entries
                WHERE loop_id = ? AND idempotency_key = ?
                """,
                (loop_id, key),
            ).fetchone()
        if row is None:
            return None
        result = self.get_process(str(row["process_id"]))
        if result is None:
            raise RepositoryIntegrityError(
                "idempotency entry references a missing Process"
            )
        return str(row["request_digest"]), result

    def list_process_history(
        self,
        *,
        loop_id: str,
        limit: int = DEFAULT_HISTORY_LIMIT,
        cursor: str | None = None,
    ) -> ProcessHistoryPage:
        if limit < 1 or limit > MAX_HISTORY_LIMIT:
            raise ValueError(f"history limit must be between 1 and {MAX_HISTORY_LIMIT}")
        offset = _decode_cursor(cursor)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT record_id, record_type, canonical_payload, canonical_digest, schema_version
                FROM runtime_records
                WHERE loop_id = ? AND record_type = 'LoopStepResult'
                ORDER BY rowid ASC
                LIMIT ? OFFSET ?
                """,
                (loop_id, limit + 1, offset),
            ).fetchall()

        has_more = len(rows) > limit
        selected = rows[:limit]
        items: list[ProcessHistoryItem] = []
        for row in selected:
            record = self._reconstruct_row(row, str(row["record_id"]))
            if not isinstance(record, LoopStepResult):
                raise RepositoryIntegrityError(
                    f"history record {row['record_id']} is not LoopStepResult"
                )
            items.append(_history_item(record))
        next_cursor = str(offset + len(selected)) if has_more else None
        return ProcessHistoryPage(
            loop_id=loop_id,
            items=items,
            limit=limit,
            next_cursor=next_cursor,
        )

    def list_trajectory_edges(
        self,
        *,
        trajectory_ref: str,
        limit: int = DEFAULT_HISTORY_LIMIT,
        cursor: str | None = None,
    ) -> TrajectoryEdgePage:
        if limit < 1 or limit > MAX_HISTORY_LIMIT:
            raise ValueError(f"trajectory limit must be between 1 and {MAX_HISTORY_LIMIT}")
        offset = _decode_cursor(cursor, label="trajectory")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT record_id, record_type, canonical_payload, canonical_digest, schema_version
                FROM runtime_records
                WHERE record_type = 'TrajectoryEdge'
                ORDER BY rowid ASC
                """
            ).fetchall()

        matching: list[TrajectoryEdge] = []
        for row in rows:
            record = self._reconstruct_row(row, str(row["record_id"]))
            if not isinstance(record, TrajectoryEdge):
                raise RepositoryIntegrityError(
                    f"trajectory record {row['record_id']} is not TrajectoryEdge"
                )
            if _matches_trajectory_ref(record, trajectory_ref):
                matching.append(record)

        selected = matching[offset : offset + limit]
        next_offset = offset + len(selected)
        next_cursor = str(next_offset) if next_offset < len(matching) else None
        return TrajectoryEdgePage(
            trajectory_ref=trajectory_ref,
            items=selected,
            limit=limit,
            next_cursor=next_cursor,
        )

    def publish(
        self,
        *,
        result: LoopStepResult,
        request_digest: str,
        idempotency_key: str | None,
    ) -> None:
        records = _collect_records(result)
        publication_id = result.process_id

        try:
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")

                if idempotency_key is not None:
                    prior = connection.execute(
                        """
                        SELECT request_digest, process_id
                        FROM idempotency_entries
                        WHERE loop_id = ? AND idempotency_key = ?
                        """,
                        (result.loop_id, idempotency_key),
                    ).fetchone()
                    if prior is not None:
                        if str(prior["request_digest"]) != request_digest:
                            raise IdempotencyConflict(
                                "idempotency key already exists with a different request digest"
                            )
                        raise RecordIdentityCollision(
                            "idempotent publication already exists"
                        )

                for position, record in enumerate(records):
                    self._inject_failure("before_record_insert", position)
                    payload_json = _canonical_json(record)
                    record_type = _record_type(record)
                    record_id = _record_id(record)
                    process_id = result.process_id
                    loop_id = result.loop_id if isinstance(record, LoopStepResult) else None
                    connection.execute(
                        """
                        INSERT INTO runtime_records (
                            record_id,
                            record_type,
                            process_id,
                            loop_id,
                            canonical_payload,
                            canonical_digest,
                            schema_version,
                            runtime_version,
                            publication_id,
                            publication_order
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record_id,
                            record_type,
                            process_id,
                            loop_id,
                            payload_json,
                            _digest(payload_json),
                            SCHEMA_VERSION,
                            RUNTIME_VERSION,
                            publication_id,
                            position,
                        ),
                    )
                    self._inject_failure("after_record_insert", position)

                self._inject_failure("before_current_scope", len(records))
                connection.execute(
                    """
                    INSERT INTO current_scope(loop_id, process_id)
                    VALUES (?, ?)
                    ON CONFLICT(loop_id) DO UPDATE SET
                        process_id = excluded.process_id,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (result.loop_id, result.process_id),
                )

                if idempotency_key is not None:
                    self._inject_failure("before_idempotency", len(records))
                    connection.execute(
                        """
                        INSERT INTO idempotency_entries(
                            loop_id,
                            idempotency_key,
                            request_digest,
                            process_id
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            result.loop_id,
                            idempotency_key,
                            request_digest,
                            result.process_id,
                        ),
                    )
        except sqlite3.IntegrityError as exc:
            message = str(exc)
            if "idempotency_entries" in message:
                raise IdempotencyConflict(message) from exc
            raise RecordIdentityCollision(message) from exc
        except sqlite3.DatabaseError as exc:
            if _is_busy_error(exc):
                raise RepositoryBusyError(str(exc)) from exc
            raise RepositoryIntegrityError(str(exc)) from exc
