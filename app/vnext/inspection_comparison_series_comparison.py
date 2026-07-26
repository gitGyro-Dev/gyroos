from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonSeriesComparisonSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_reference_count_per_side: int = Field(default=256, ge=1, le=4096)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=32, ge=0, le=1024)
    max_metadata_bytes: int = Field(default=16_384, ge=0, le=1_048_576)


class ExperimentalComparisonSeriesReference(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    comparison_series_id: str = Field(min_length=1)
    set_comparison_ids: tuple[str, ...] = ()
    series_digest: str | None = None

    @field_validator("comparison_series_id")
    @classmethod
    def validate_series_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("comparison_series_id must not be blank")
        return value

    @field_validator("set_comparison_ids")
    @classmethod
    def validate_set_comparison_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(value.strip() for value in values)
        if any(not value for value in normalized):
            raise ValueError("set_comparison_ids must not contain blank values")
        return normalized

    @field_validator("series_digest")
    @classmethod
    def validate_series_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
            raise ValueError("series_digest must be a 64-character lowercase hexadecimal label")
        return normalized


class ExperimentalComparisonSeriesComparisonRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    series_comparison_id: str = Field(min_length=1)
    left_series: ExperimentalComparisonSeriesReference
    right_series: ExperimentalComparisonSeriesReference
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("series_comparison_id")
    @classmethod
    def validate_series_comparison_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("series_comparison_id must not be blank")
        return value


class ExperimentalComparisonSeriesComparisonReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    series_comparison_id: str
    left_comparison_series_id: str
    right_comparison_series_id: str
    added_set_comparison_ids: tuple[str, ...]
    removed_set_comparison_ids: tuple[str, ...]
    retained_set_comparison_ids: tuple[str, ...]
    left_series_digest: str | None
    right_series_digest: str | None
    digest_changed: bool | None
    created_at: datetime
    warnings: tuple[str, ...]
    comparison_metadata: dict[str, Any]


class ExperimentalComparisonSeriesComparisonResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    comparison_series_comparison_created: Literal[True] = True
    report: ExperimentalComparisonSeriesComparisonReport


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
