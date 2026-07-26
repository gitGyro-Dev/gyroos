from __future__ import annotations

from threading import RLock

from .experimental_repository import (
    ExperimentalRecordRepository,
    InMemoryExperimentalRecordRepository,
)


class ExperimentalRepositoryProvider:
    """Explicit provider boundary for the public experimental API repository."""

    def __init__(self, repository: ExperimentalRecordRepository) -> None:
        self._repository = repository
        self._lock = RLock()

    def get_repository(self) -> ExperimentalRecordRepository:
        with self._lock:
            return self._repository

    def replace_repository(self, repository: ExperimentalRecordRepository) -> None:
        """Test-only/configuration replacement; not a canonical backend switch."""
        with self._lock:
            self._repository = repository


experimental_repository_provider = ExperimentalRepositoryProvider(
    InMemoryExperimentalRecordRepository()
)


def get_experimental_repository() -> ExperimentalRecordRepository:
    return experimental_repository_provider.get_repository()
