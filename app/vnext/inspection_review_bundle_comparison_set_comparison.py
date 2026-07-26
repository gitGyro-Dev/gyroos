from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonSetComparisonSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_bundle_comparison_count_per_side: int = Field(default=256, ge=1, le=4096)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=64, ge=0, le=1024)
    max_metadata_bytes: int = Field(default=16_384, ge=0, le=1_048_576)


class ExperimentalComparisonSetReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_set_id: str = Field(min_length=1)
    bundle_comparison_ids: tuple[str, ...]
    set_digest: str | None = None

    @field_validator("set_digest")
    @classmethod
    def validate_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.lower()
        if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
            raise ValueError("set_digest must be a 64-character hexadecimal SHA-256 label")
        return normalized


class ExperimentalComparisonSetComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    set_comparison_id: str = Field(min_length=1)
    left_set: ExperimentalComparisonSetReference
    right_set: ExperimentalComparisonSetReference
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, object] = Field(default_factory=dict)


class ExperimentalComparisonSetComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    set_comparison_id: str
    left_comparison_set_id: str
    right_comparison_set_id: str
    added_bundle_comparison_ids: tuple[str, ...]
    removed_bundle_comparison_ids: tuple[str, ...]
    retained_bundle_comparison_ids: tuple[str, ...]
    left_set_digest: str | None
    right_set_digest: str | None
    digest_changed: bool | None
    created_at: datetime
    warnings: tuple[str, ...]
    comparison_metadata: dict[str, object]


class ExperimentalComparisonSetComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_report_created: bool
    report: ExperimentalComparisonSetComparisonReport


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
