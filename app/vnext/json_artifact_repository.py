from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


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


class JsonArtifactPathPolicy:
    """Map safe record IDs to repository-contained artifact paths only."""

    def __init__(self, settings: JsonArtifactRepositorySettings) -> None:
        self._settings = settings
        self._root = settings.root.expanduser().resolve(strict=False)

    @property
    def root(self) -> Path:
        return self._root

    def validate_record_id(self, record_id: str) -> str:
        if not record_id or record_id in {".", ".."}:
            raise InvalidArtifactRecordIdError("record_id must not be empty or dot-relative")
        if Path(record_id).is_absolute():
            raise InvalidArtifactRecordIdError("absolute record_id values are not allowed")
        if any(separator in record_id for separator in ("/", "\\")):
            raise InvalidArtifactRecordIdError("record_id must not contain path separators")
        if "\x00" in record_id:
            raise InvalidArtifactRecordIdError("record_id must not contain NUL")
        return record_id

    def artifact_path(self, record_id: str) -> Path:
        safe_id = self.validate_record_id(record_id)
        candidate = (self._root / f"{safe_id}{self._settings.suffix}").resolve(strict=False)
        self._assert_contained(candidate)
        return candidate

    def temporary_path(self, record_id: str) -> Path:
        artifact = self.artifact_path(record_id)
        temporary = artifact.with_name(f".{artifact.name}.{uuid4().hex}.tmp")
        self._assert_contained(temporary)
        return temporary

    def _assert_contained(self, path: Path) -> None:
        try:
            path.relative_to(self._root)
        except ValueError as exc:
            raise InvalidArtifactRecordIdError(
                "artifact path must remain within repository root"
            ) from exc
