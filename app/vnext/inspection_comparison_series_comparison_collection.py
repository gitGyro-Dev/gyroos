from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComparisonCollectionDigestAlgorithm(str, Enum):
    SHA256 = "SHA-256"


class ExperimentalComparisonSeriesComparisonCollectionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_comparison_count: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=50, ge=0, le=1000)
    max_source_ref_count: int = Field(default=50, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=0, le=1048576)


class ExperimentalComparisonSeriesComparisonCollectionDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: ComparisonCollectionDigestAlgorithm = ComparisonCollectionDigestAlgorithm.SHA256
    canonicalization_profile: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"


class ExperimentalComparisonSeriesComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    series_comparison_id: str = Field(min_length=1)
    left_comparison_series_id: str = Field(min_length=1)
    right_comparison_series_id: str = Field(min_length=1)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None


class ExperimentalComparisonSeriesComparisonCollectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_collection_id: str = Field(min_length=1)
    comparison_references: tuple[ExperimentalComparisonSeriesComparisonReference, ...]
    created_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    collection_metadata: dict[str, Any] = Field(default_factory=dict)
    digest_policy: ExperimentalComparisonSeriesComparisonCollectionDigestPolicy = Field(
        default_factory=ExperimentalComparisonSeriesComparisonCollectionDigestPolicy
    )

    @field_validator("comparison_references")
    @classmethod
    def comparison_references_must_not_be_empty(
        cls,
        value: tuple[ExperimentalComparisonSeriesComparisonReference, ...],
    ) -> tuple[ExperimentalComparisonSeriesComparisonReference, ...]:
        if not value:
            raise ValueError("comparison_references must not be empty")
        return value


class ExperimentalComparisonSeriesComparisonCollectionManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_collection_id: str
    comparison_references: tuple[ExperimentalComparisonSeriesComparisonReference, ...]
    comparison_count: int = Field(ge=1)
    comparison_references_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    digest_policy: ExperimentalComparisonSeriesComparisonCollectionDigestPolicy
    created_at: datetime
    warnings: tuple[str, ...]
    source_refs: tuple[str, ...]
    collection_metadata: dict[str, Any]


class ExperimentalComparisonSeriesComparisonCollectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_collection_created: bool = True
    manifest: ExperimentalComparisonSeriesComparisonCollectionManifest


def canonical_comparison_references_json(
    references: tuple[ExperimentalComparisonSeriesComparisonReference, ...],
) -> str:
    payload = [reference.model_dump(mode="json") for reference in references]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_comparison_references(
    references: tuple[ExperimentalComparisonSeriesComparisonReference, ...],
    policy: ExperimentalComparisonSeriesComparisonCollectionDigestPolicy,
) -> str:
    if policy.algorithm is not ComparisonCollectionDigestAlgorithm.SHA256:
        raise ValueError(f"unsupported digest algorithm: {policy.algorithm}")
    if policy.canonicalization_profile != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
        raise ValueError(
            "unsupported canonicalization profile: "
            f"{policy.canonicalization_profile}"
        )
    canonical = canonical_comparison_references_json(references)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
