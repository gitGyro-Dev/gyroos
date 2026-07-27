from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonSequenceComparisonSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_reference_count: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=50, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=0, le=1048576)


class ExperimentalComparisonSequenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_sequence_id: str
    collection_comparison_ids: tuple[str, ...] = ()
    sequence_digest: str | None = None

    @field_validator("sequence_digest")
    @classmethod
    def validate_sequence_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.lower()
        if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
            raise ValueError("sequence_digest must be a 64-character hexadecimal label")
        return normalized


class ExperimentalComparisonSequenceComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence_comparison_id: str
    left_sequence: ExperimentalComparisonSequenceReference
    right_sequence: ExperimentalComparisonSequenceReference
    created_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonSequenceComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence_comparison_id: str
    left_comparison_sequence_id: str
    right_comparison_sequence_id: str
    added_collection_comparison_ids: tuple[str, ...]
    removed_collection_comparison_ids: tuple[str, ...]
    retained_collection_comparison_ids: tuple[str, ...]
    left_sequence_digest: str | None = None
    right_sequence_digest: str | None = None
    digest_changed: bool | None = None
    created_at: datetime
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonSequenceComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_sequence_comparison_created: bool = True
    report: ExperimentalComparisonSequenceComparisonReport


def utc_now() -> datetime:
    return datetime.now(UTC)
