from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonSetComparisonSeriesSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_references: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=2048)
    max_warnings: int = Field(default=50, ge=0, le=500)
    max_source_refs: int = Field(default=100, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=0, le=1048576)


class ExperimentalComparisonSetComparisonSeriesDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: Literal["SHA-256"] = "SHA-256"
    canonicalization: Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"] = (
        "JSON_SORTED_KEYS_UTF8_COMPACT_V1"
    )


class ExperimentalComparisonSetComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    set_comparison_id: str = Field(min_length=1)
    left_comparison_set_id: str = Field(min_length=1)
    right_comparison_set_id: str = Field(min_length=1)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None

    @field_validator(
        "set_comparison_id",
        "left_comparison_set_id",
        "right_comparison_set_id",
    )
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("identifier must not be blank")
        return normalized


class ExperimentalComparisonSetComparisonSeriesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_series_id: str = Field(min_length=1)
    set_comparison_references: tuple[
        ExperimentalComparisonSetComparisonReference, ...
    ]
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    series_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("comparison_series_id")
    @classmethod
    def validate_series_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("comparison_series_id must not be blank")
        return normalized


class ExperimentalComparisonSetComparisonSeriesManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_series_id: str
    set_comparison_references: tuple[
        ExperimentalComparisonSetComparisonReference, ...
    ]
    reference_count: int = Field(ge=0)
    series_digest: str = Field(min_length=64, max_length=64)
    digest_policy: ExperimentalComparisonSetComparisonSeriesDigestPolicy
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    series_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonSetComparisonSeriesResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_series_created: Literal[True] = True
    manifest: ExperimentalComparisonSetComparisonSeriesManifest


def canonical_reference_payload(
    references: tuple[ExperimentalComparisonSetComparisonReference, ...],
) -> bytes:
    payload = [reference.model_dump(mode="json") for reference in references]
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_series_digest(
    references: tuple[ExperimentalComparisonSetComparisonReference, ...],
) -> str:
    return hashlib.sha256(canonical_reference_payload(references)).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
