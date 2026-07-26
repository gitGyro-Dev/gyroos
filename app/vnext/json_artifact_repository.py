from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from uuid import uuid4

from pydantic import ValidationError

from .experimental_repository import ExperimentalRecordRepository
from .models import ExperimentalRecordEnvelope


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


class JsonArtifactExperimentalRecordRepository(ExperimentalRecordRepository):
    """One-record-per-file JSON repository for opaque experimental envelopes."""

    def __init__(
        self,
        settings: JsonArtifactRepositorySettings,
        path_policy: JsonArtifactPathPolicy | None = None,
    ) -> None:
        self._settings = settings
        self._paths = path_policy or JsonArtifactPathPolicy(settings)
        self._lock = RLock()

    def save(self, envelope: ExperimentalRecordEnvelope) -> ExperimentalRecordEnvelope:
        artifact = self._paths.artifact_path(envelope.record_id)
        temporary = self._paths.temporary_path(envelope.record_id)
        try:
            serialized = json.dumps(
                envelope.model_dump(mode="json"),
                ensure_ascii=False,
                indent=self._settings.indent,
                sort_keys=True,
            )
        except (TypeError, ValueError) as exc:
            raise ArtifactSerializationError(
                f"failed to serialize experimental record {envelope.record_id}"
            ) from exc

        with self._lock:
            try:
                self._paths.root.mkdir(parents=True, exist_ok=True)
                with temporary.open("w", encoding=self._settings.encoding, newline="\n") as handle:
                    handle.write(serialized)
                    handle.write("\n")
                    handle.flush()
                    if self._settings.fsync_on_save:
                        os.fsync(handle.fileno())
                os.replace(temporary, artifact)
            except OSError as exc:
                raise ArtifactStorageError(
                    f"failed to save experimental record {envelope.record_id}"
                ) from exc
            finally:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
        return envelope.model_copy(deep=True)

    def get(self, record_id: str) -> ExperimentalRecordEnvelope | None:
        artifact = self._paths.artifact_path(record_id)
        with self._lock:
            if not artifact.exists():
                return None
            return self._read_artifact(artifact)

    def list(
        self,
        *,
        process_id: str | None = None,
        record_type: str | None = None,
    ) -> list[ExperimentalRecordEnvelope]:
        with self._lock:
            if not self._paths.root.exists():
                return []
            artifacts = list(self._paths.root.glob(f"*{self._settings.suffix}"))
            envelopes = [self._read_artifact(path) for path in artifacts if path.is_file()]

        return [
            envelope.model_copy(deep=True)
            for envelope in envelopes
            if (process_id is None or envelope.process_id == process_id)
            and (record_type is None or envelope.record_type == record_type)
        ]

    def delete(self, record_id: str) -> bool:
        artifact = self._paths.artifact_path(record_id)
        with self._lock:
            try:
                artifact.unlink()
                return True
            except FileNotFoundError:
                return False
            except OSError as exc:
                raise ArtifactStorageError(
                    f"failed to delete experimental record {record_id}"
                ) from exc

    def _read_artifact(self, artifact: Path) -> ExperimentalRecordEnvelope:
        try:
            text = artifact.read_text(encoding=self._settings.encoding)
        except UnicodeError as exc:
            raise ArtifactDeserializationError(
                f"failed to decode JSON artifact {artifact.name}"
            ) from exc
        except OSError as exc:
            raise ArtifactStorageError(
                f"failed to read JSON artifact {artifact.name}"
            ) from exc

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ArtifactDeserializationError(
                f"failed to parse JSON artifact {artifact.name}"
            ) from exc

        try:
            envelope = ExperimentalRecordEnvelope.model_validate(data)
        except ValidationError as exc:
            raise ArtifactValidationError(
                f"invalid experimental envelope in {artifact.name}"
            ) from exc

        expected_path = self._paths.artifact_path(envelope.record_id)
        if expected_path != artifact.resolve(strict=False):
            raise ArtifactValidationError(
                f"artifact filename does not match envelope record_id in {artifact.name}"
            )
        return envelope.model_copy(deep=True)
