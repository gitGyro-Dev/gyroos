from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonCollectionComparisonSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_reference_count: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=50, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=0, le=1048576)


class ExperimentalComparisonCollectionReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_collection_id: str
    series_comparison_ids: tuple[str, ...]
    collection_digest: str | None = None

    @field_validator("collection_digest")
    @classmethod
    def validate_collection_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.lower()
        if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
            raise ValueError("collection_digest must be a 64-character lowercase hex label")
        return normalized


class ExperimentalComparisonCollectionComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    collection_comparison_id: str
    left_collection: ExperimentalComparisonCollectionReference
    right_collection: ExperimentalComparisonCollectionReference
    created_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonCollectionComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    collection_comparison_id: str
    left_comparison_collection_id: str
    right_comparison_collection_id: str
    added_series_comparison_ids: tuple[str, ...]
    removed_series_comparison_ids: tuple[str, ...]
    retained_series_comparison_ids: tuple[str, ...]
    left_collection_digest: str | None = None
    right_collection_digest: str | None = None
    digest_changed: bool | None = None
    created_at: datetime
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonCollectionComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_collection_comparison_created: bool = True
    report: ExperimentalComparisonCollectionComparisonReport


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
