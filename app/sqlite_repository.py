from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, TypeAlias

from pydantic import BaseModel

from .models import (
    BoundaryEvidence,
    BoundaryStateRecord,
    ContextEvidence,
    DeferredRelationRecord,
    LoopStepResult,
    OperatorResponse,
    RuntimeContinuityResult,
    SliceDone,
    StabilityResult,
    TrajectoryEdge,
    VoidEvidence,
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
RUNTIME_VERSION = "priority-g3"

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
    payload = record.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(payload_json: str) -> str:
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _record_id(record: CanonicalRecord) -> str:
    field_name = _RECORD_ID_FIELDS.get(type(record))
    if field_name is None:
        raise ValueError(f"unsupported canonical record type: {type(record).__name__}")
    value = getattr(record, field_name, None)
    if not value:
        raise ValueError(
            f"canonical record {type(record).__name__} has no value for {field_name}"
        )
    return str(value)


def _record_type(record: CanonicalRecord) -> str:
    name = type(record).__name__
    if name not in _RECORD_REGISTRY:
        raise ValueError(f"unsupported canonical record type: {name}")
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
        raise ValueError(f"duplicate record identities in publication group: {duplicates}")
    return records


class SQLiteStore:
    """SQLite-backed Runtime repository for the bounded Priority G prototype."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
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

                CREATE INDEX IF NOT EXISTS idx_runtime_records_process
                    ON runtime_records(process_id, publication_order);

                CREATE INDEX IF NOT EXISTS idx_runtime_records_loop
                    ON runtime_records(loop_id, publication_order);

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
                """
            )

    def get_process(self, process_id: str) -> LoopStepResult | None:
        record = self.get_record(process_id)
        if record is None:
            return None
        if not isinstance(record, LoopStepResult):
            raise ValueError(f"record {process_id} is not LoopStepResult")
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
        if row["schema_version"] != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version={row['schema_version']} for record {record_id}"
            )
        payload_json = str(row["canonical_payload"])
        if _digest(payload_json) != row["canonical_digest"]:
            raise ValueError(f"canonical digest mismatch for record {record_id}")
        model = _RECORD_REGISTRY.get(str(row["record_type"]))
        if model is None:
            raise ValueError(f"unsupported record type: {row['record_type']}")
        payload: dict[str, Any] = json.loads(payload_json)
        return model.model_validate(payload)  # type: ignore[return-value]

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
            raise ValueError("idempotency entry references a missing Process")
        return str(row["request_digest"]), result

    def publish(
        self,
        *,
        result: LoopStepResult,
        request_digest: str,
        idempotency_key: str | None,
    ) -> None:
        records = _collect_records(result)
        publication_id = result.process_id

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for publication_order, record in enumerate(records):
                payload_json = _canonical_json(record)
                record_id = _record_id(record)
                record_type = _record_type(record)
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
                        publication_order,
                    ),
                )

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

            if idempotency_key:
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
