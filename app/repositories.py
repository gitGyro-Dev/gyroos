from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock

from .models import (
    LoopStepResult,
    ProcessHistoryItem,
    ProcessHistoryPage,
    TrajectoryEdge,
    TrajectoryEdgePage,
)

MAX_HISTORY_LIMIT = 100
DEFAULT_HISTORY_LIMIT = 20


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


@dataclass
class InMemoryStore:
    processes: dict[str, LoopStepResult] = field(default_factory=dict)
    records: dict[str, object] = field(default_factory=dict)
    idempotency: dict[tuple[str, str], tuple[str, LoopStepResult]] = field(default_factory=dict)
    current_scope: dict[str, str] = field(default_factory=dict)
    process_history: dict[str, list[str]] = field(default_factory=dict)
    trajectory_history: list[str] = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock)

    def get_process(self, process_id: str) -> LoopStepResult | None:
        return self.processes.get(process_id)

    def get_record(self, record_id: str) -> object | None:
        return self.records.get(record_id)

    def get_current_scope(self, loop_id: str) -> str | None:
        return self.current_scope.get(loop_id)

    def get_idempotent(self, loop_id: str, key: str) -> tuple[str, LoopStepResult] | None:
        return self.idempotency.get((loop_id, key))

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
        process_ids = self.process_history.get(loop_id, [])
        selected_ids = process_ids[offset : offset + limit]
        items = [_history_item(self.processes[process_id]) for process_id in selected_ids]
        next_offset = offset + len(selected_ids)
        next_cursor = str(next_offset) if next_offset < len(process_ids) else None
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
        matching_edges = [
            edge
            for record_id in self.trajectory_history
            if isinstance((edge := self.records.get(record_id)), TrajectoryEdge)
            and _matches_trajectory_ref(edge, trajectory_ref)
        ]
        selected = matching_edges[offset : offset + limit]
        next_offset = offset + len(selected)
        next_cursor = str(next_offset) if next_offset < len(matching_edges) else None
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
        """Publish one complete result group under one lock."""
        artifacts = {
            result.process_id: result,
            result.slice_done.slice_id: result.slice_done,
            result.stability.stability_result_id: result.stability,
            result.operator_response.operator_response_id: result.operator_response,
            result.continuity.continuity_result_id: result.continuity,
        }
        for item in result.slice_done.boundary_evidence:
            artifacts[item.boundary_evidence_id] = item
        for item in result.slice_done.boundary_state_records:
            artifacts[item.boundary_state_record_id] = item
        for item in result.slice_done.context_evidence:
            artifacts[item.context_evidence_id] = item
        for item in result.slice_done.void_evidence:
            artifacts[item.void_evidence_id] = item
        if result.deferred_relation_record is not None:
            artifacts[
                result.deferred_relation_record.deferred_relation_record_id
            ] = result.deferred_relation_record
        for item in result.trajectory_edges:
            artifacts[item.trajectory_edge_id] = item

        with self._lock:
            collision = set(artifacts).intersection(self.records)
            if collision:
                raise ValueError(f"artifact identity collision: {sorted(collision)}")
            self.processes[result.process_id] = result
            self.records.update(artifacts)
            self.current_scope[result.loop_id] = result.process_id
            self.process_history.setdefault(result.loop_id, []).append(result.process_id)
            self.trajectory_history.extend(
                item.trajectory_edge_id for item in result.trajectory_edges
            )
            if idempotency_key:
                self.idempotency[(result.loop_id, idempotency_key)] = (
                    request_digest,
                    result,
                )


store = InMemoryStore()
