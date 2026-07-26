from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ExperimentalRepositoryError(Exception):
    """Base error for isolated experimental repository operations."""


class InvalidArtifactRecordIdError(ExperimentalRepositoryError):
    """Raised when a record ID cannot be represented safely as one artifact path."""


class ArtifactSerializationError(ExperimentalRepositoryError):
    """Raised when an experimental envelope cannot be serialized."""


class ArtifactDeserializationError(ExperimentalRepositoryError):
    """Raised when artifact bytes cannot be decoded or parsed as JSON."""


class ArtifactValidationError(ExperimentalRepositoryError):
    """Raised when parsed artifact content is not a valid experimental envelope."""


class ArtifactStorageError(ExperimentalRepositoryError):
    """Raised when the filesystem cannot complete an artifact operation."""


@dataclass(frozen=True, slots=True)
class JsonArtifactRepositorySettings:
    """Explicit settings for an isolated one-record-per-file JSON repository."""

    root: Path
    encoding: str = "utf-8"
    indent: int = 2
    suffix: str = ".json"
    fsync_on_save: bool = True

    def __post_init__(self) -> None:
        root = Path(self.root)
        if not self.encoding:
            raise ValueError("encoding must not be empty")
        if self.indent < 0:
            raise ValueError("indent must be zero or greater")
        if not self.suffix.startswith(".") or self.suffix in {".", ".."}:
            raise ValueError("suffix must be a non-empty file extension beginning with '.'")
        object.__setattr__(self, "root", root)
