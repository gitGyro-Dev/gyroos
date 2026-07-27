from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DigestAlgorithm = Literal["SHA-256"]
DigestCanonicalization = Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"]


class ExperimentalComparisonRegisterComparisonSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_sequence_comparison_references_per_side: int = Field(default=128, ge=1, le=1024)
    max_identifier_length: int = Field(default=200, ge=1, le=1024)
    max_warning_count: int = Field(default=64, ge=0, le=512)
    max_metadata_bytes: int = Field(default=16_384, ge=0, le=1_048_576)


class ExperimentalComparisonRegisterReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_register_id: str = Field(min_length=1, max_length=200)
    sequence_comparison_ids: tuple[str, ...] = Field(min_length=1)
    register_digest: str | None = None

    @field_validator("register_digest")
    @classmethod
    def validate_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError("register_digest must be a lowercase SHA-256 hex label")
        return value


class ExperimentalComparisonRegisterComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    register_comparison_id: str = Field(min_length=1, max_length=200)
    left_register: ExperimentalComparisonRegisterReference
    right_register: ExperimentalComparisonRegisterReference
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonRegisterComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    register_comparison_id: str
    left_comparison_register_id: str
    right_comparison_register_id: str
    added_sequence_comparison_ids: tuple[str, ...]
    removed_sequence_comparison_ids: tuple[str, ...]
    retained_sequence_comparison_ids: tuple[str, ...]
    left_register_digest: str | None
    right_register_digest: str | None
    digest_changed: bool | None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    warnings: tuple[str, ...] = ()
    comparison_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonRegisterComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_register_comparison_created: bool = True
    report: ExperimentalComparisonRegisterComparisonReport
