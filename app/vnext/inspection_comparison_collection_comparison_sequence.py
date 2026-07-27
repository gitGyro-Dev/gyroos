from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonCollectionComparisonSequenceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_comparison_count: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=50, ge=0, le=1000)
    max_source_ref_count: int = Field(default=100, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=1, le=1048576)


class ExperimentalComparisonCollectionComparisonSequenceDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: Literal["SHA-256"] = "SHA-256"
    canonicalization: Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"] = (
        "JSON_SORTED_KEYS_UTF8_COMPACT_V1"
    )


class ExperimentalComparisonCollectionComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    collection_comparison_id: str
    left_comparison_collection_id: str
    right_comparison_collection_id: str
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None

    @field_validator(
        "collection_comparison_id",
        "left_comparison_collection_id",
        "right_comparison_collection_id",
    )
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier must not be blank")
        return value


class ExperimentalComparisonCollectionComparisonSequenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_sequence_id: str
    comparison_references: tuple[ExperimentalComparisonCollectionComparisonReference, ...]
    digest_policy: ExperimentalComparisonCollectionComparisonSequenceDigestPolicy = Field(
        default_factory=ExperimentalComparisonCollectionComparisonSequenceDigestPolicy
    )
    created_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    sequence_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("comparison_sequence_id")
    @classmethod
    def validate_sequence_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("comparison_sequence_id must not be blank")
        return value


class ExperimentalComparisonCollectionComparisonSequenceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_sequence_id: str
    comparison_references: tuple[ExperimentalComparisonCollectionComparisonReference, ...]
    comparison_count: int = Field(ge=0)
    comparison_references_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    digest_policy: ExperimentalComparisonCollectionComparisonSequenceDigestPolicy
    created_at: datetime
    warnings: tuple[str, ...]
    source_refs: tuple[str, ...]
    sequence_metadata: dict[str, Any]


class ExperimentalComparisonCollectionComparisonSequenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_sequence_created: Literal[True] = True
    manifest: ExperimentalComparisonCollectionComparisonSequenceManifest


def canonical_comparison_references_json(
    references: tuple[ExperimentalComparisonCollectionComparisonReference, ...],
) -> str:
    return json.dumps(
        [reference.model_dump(mode="json") for reference in references],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def digest_comparison_references(
    references: tuple[ExperimentalComparisonCollectionComparisonReference, ...],
    policy: ExperimentalComparisonCollectionComparisonSequenceDigestPolicy,
) -> str:
    if policy.algorithm != "SHA-256":
        raise ValueError("unsupported digest algorithm")
    if policy.canonicalization != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
        raise ValueError("unsupported canonicalization profile")
    return hashlib.sha256(
        canonical_comparison_references_json(references).encode("utf-8")
    ).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
