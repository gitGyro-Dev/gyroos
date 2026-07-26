from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from threading import RLock

from .models import ExperimentalRecordEnvelope


class ExperimentalRecordRepository(ABC):
    """Minimal experimental repository contract for opaque vNext envelopes."""

    @abstractmethod
    def save(self, envelope: ExperimentalRecordEnvelope) -> ExperimentalRecordEnvelope:
        raise NotImplementedError

    @abstractmethod
    def get(self, record_id: str) -> ExperimentalRecordEnvelope | None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        *,
        process_id: str | None = None,
        record_type: str | None = None,
    ) -> list[ExperimentalRecordEnvelope]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        raise NotImplementedError


class InMemoryExperimentalRecordRepository(ExperimentalRecordRepository):
    """Thread-safe in-memory repository for isolated experimental envelopes.

    Storage is process-local and ephemeral. Save replaces an envelope with the
    same record_id; replacement does not imply canonical authority, versioning,
    or current-record selection.
    """

    def __init__(self) -> None:
        self._records: dict[str, ExperimentalRecordEnvelope] = {}
        self._lock = RLock()

    def save(self, envelope: ExperimentalRecordEnvelope) -> ExperimentalRecordEnvelope:
        stored = envelope.model_copy(deep=True)
        with self._lock:
            self._records[stored.record_id] = stored
        return stored.model_copy(deep=True)

    def get(self, record_id: str) -> ExperimentalRecordEnvelope | None:
        with self._lock:
            envelope = self._records.get(record_id)
            return envelope.model_copy(deep=True) if envelope is not None else None

    def list(
        self,
        *,
        process_id: str | None = None,
        record_type: str | None = None,
    ) -> list[ExperimentalRecordEnvelope]:
        with self._lock:
            records = list(self._records.values())

        filtered = [
            record
            for record in records
            if (process_id is None or record.process_id == process_id)
            and (record_type is None or record.record_type == record_type)
        ]
        return [record.model_copy(deep=True) for record in filtered]

    def delete(self, record_id: str) -> bool:
        with self._lock:
            return self._records.pop(record_id, None) is not None
