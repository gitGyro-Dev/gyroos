from __future__ import annotations


class RepositoryError(RuntimeError):
    """Base error for storage-independent Runtime repository failures."""


class RecordIdentityCollision(RepositoryError):
    """Raised when a canonical record identity already exists."""


class IdempotencyConflict(RepositoryError):
    """Raised when one idempotency scope is reused with a different digest."""


class RepositoryBusyError(RepositoryError):
    """Raised when the repository is temporarily unavailable due to lock contention."""


class RepositoryIntegrityError(RepositoryError):
    """Raised when persistent repository integrity is violated."""


class RepositorySerializationError(RepositoryError):
    """Raised when canonical records cannot be serialized or reconstructed."""


class RepositorySchemaMismatch(RepositoryError):
    """Raised when stored schema metadata is unsupported."""
