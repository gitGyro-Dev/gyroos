from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DigestAlgorithm = Literal["SHA-256"]
DigestCanonicalization = Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"]


class ExperimentalComparisonSequenceComparisonRegisterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_comparison_count: int = Field(default=128, ge=1, le=1024)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=64, ge=0, le=1024)
    max_source_ref_count: int = Field(default=64, ge=0, le=1024)
    max_metadata_bytes: int = Field(default=16_384, ge=0, le=1_048_576)


class ExperimentalComparisonSequenceComparisonRegisterDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: DigestAlgorithm = "SHA-256"
    canonicalization: DigestCanonicalization = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"


class ExperimentalComparisonSequenceComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence_comparison_id: str = Field(min_length=1)
    left_comparison_sequence_id: str = Field(min_length=1)
    right_comparison_sequence_id: str = Field(min_length=1)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None

    @field_validator(
        "sequence_comparison_id",
        "left_comparison_sequence_id",
        "right_comparison_sequence_id",
    )
    @classmethod
    def reject_blank_identifier(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier must not be blank")
        return value


class ExperimentalComparisonSequenceComparisonRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_register_id: str = Field(min_length=1)
    comparison_references: tuple[
        ExperimentalComparisonSequenceComparisonReference, ...
    ] = Field(min_length=1)
    digest_policy: ExperimentalComparisonSequenceComparisonRegisterDigestPolicy = Field(
        default_factory=ExperimentalComparisonSequenceComparisonRegisterDigestPolicy
    )
    created_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    register_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("comparison_register_id")
    @classmethod
    def reject_blank_register_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("comparison_register_id must not be blank")
        return value


class ExperimentalComparisonSequenceComparisonRegisterManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_register_id: str
    comparison_references: tuple[
        ExperimentalComparisonSequenceComparisonReference, ...
    ]
    comparison_count: int = Field(ge=1)
    comparison_references_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    digest_policy: ExperimentalComparisonSequenceComparisonRegisterDigestPolicy
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    register_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonSequenceComparisonRegisterResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_register_created: Literal[True] = True
    manifest: ExperimentalComparisonSequenceComparisonRegisterManifest


def utc_now() -> datetime:
    return datetime.now(UTC)


def digest_comparison_references(
    references: tuple[ExperimentalComparisonSequenceComparisonReference, ...],
    policy: ExperimentalComparisonSequenceComparisonRegisterDigestPolicy,
) -> str:
    if policy.algorithm != "SHA-256":
        raise ValueError("unsupported digest algorithm")
    if policy.canonicalization != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
        raise ValueError("unsupported digest canonicalization")

    canonical = json.dumps(
        [reference.model_dump(mode="json") for reference in references],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
