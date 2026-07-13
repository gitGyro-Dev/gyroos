from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock

from .models import LoopStepResult


@dataclass
class InMemoryStore:
    processes: dict[str, LoopStepResult] = field(default_factory=dict)
    records: dict[str, object] = field(default_factory=dict)
    idempotency: dict[tuple[str, str], tuple[str, LoopStepResult]] = field(default_factory=dict)
    current_scope: dict[str, str] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock)

    def get_process(self, process_id: str) -> LoopStepResult | None:
        return self.processes.get(process_id)

    def get_record(self, record_id: str) -> object | None:
        return self.records.get(record_id)

    def get_current_scope(self, loop_id: str) -> str | None:
        return self.current_scope.get(loop_id)

    def get_idempotent(self, loop_id: str, key: str) -> tuple[str, LoopStepResult] | None:
        return self.idempotency.get((loop_id, key))

    def publish(
        self,
        *,
        result: LoopStepResult,
        request_digest: str,
        idempotency_key: str | None,
    ) -> None:
        """Publish one complete result group under one lock.

        Generated artifacts are inserted only after the executor has validated the
        complete result group. This is the in-memory atomic publication boundary.
        """
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

        with self._lock:
            collision = set(artifacts).intersection(self.records)
            if collision:
                raise ValueError(f"artifact identity collision: {sorted(collision)}")
            self.processes[result.process_id] = result
            self.records.update(artifacts)
            self.current_scope[result.loop_id] = result.process_id
            if idempotency_key:
                self.idempotency[(result.loop_id, idempotency_key)] = (
                    request_digest,
                    result,
                )


store = InMemoryStore()
