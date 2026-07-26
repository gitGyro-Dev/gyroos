from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComparisonSetDigestAlgorithm(str, Enum):
    SHA256 = "SHA-256"


class ExperimentalReviewBundleComparisonSetSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_comparison_count: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=4096)
    max_warning_count: int = Field(default=100, ge=0, le=1000)
    max_source_ref_count: int = Field(default=100, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16384, ge=0, le=1048576)


class ExperimentalReviewBundleComparisonSetDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: ComparisonSetDigestAlgorithm = ComparisonSetDigestAlgorithm.SHA256
    canonicalization: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"


class ExperimentalReviewBundleComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bundle_comparison_id: str = Field(min_length=1)
    left_review_bundle_id: str = Field(min_length=1)
    right_review_bundle_id: str = Field(min_length=1)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None

    @field_validator(
        "bundle_comparison_id",
        "left_review_bundle_id",
        "right_review_bundle_id",
    )
    @classmethod
    def reject_blank_identifiers(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier must not be blank")
        return value


class ExperimentalReviewBundleComparisonSetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_set_id: str = Field(min_length=1)
    comparison_references: tuple[ExperimentalReviewBundleComparisonReference, ...]
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)
    digest_policy: ExperimentalReviewBundleComparisonSetDigestPolicy = Field(
        default_factory=ExperimentalReviewBundleComparisonSetDigestPolicy
    )

    @field_validator("comparison_set_id")
    @classmethod
    def reject_blank_set_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("comparison_set_id must not be blank")
        return value


class ExperimentalReviewBundleComparisonSetManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_set_id: str
    comparison_references: tuple[ExperimentalReviewBundleComparisonReference, ...]
    comparison_count: int
    comparison_references_digest: str
    digest_algorithm: ComparisonSetDigestAlgorithm
    canonicalization: str
    created_at: datetime
    warnings: tuple[str, ...]
    source_refs: tuple[str, ...]
    metadata: dict[str, Any]


class ExperimentalReviewBundleComparisonSetResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_set_created: bool
    comparison_set: ExperimentalReviewBundleComparisonSetManifest


def canonical_comparison_references_json(
    references: tuple[ExperimentalReviewBundleComparisonReference, ...],
) -> bytes:
    payload = [reference.model_dump(mode="json") for reference in references]
    try:
        text = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("comparison references are not canonical JSON compatible") from exc
    return text.encode("utf-8")


def digest_comparison_references(
    references: tuple[ExperimentalReviewBundleComparisonReference, ...],
    policy: ExperimentalReviewBundleComparisonSetDigestPolicy,
) -> str:
    if policy.algorithm is not ComparisonSetDigestAlgorithm.SHA256:
        raise ValueError(f"unsupported digest algorithm: {policy.algorithm}")
    if policy.canonicalization != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
        raise ValueError(
            f"unsupported canonicalization profile: {policy.canonicalization}"
        )
    return hashlib.sha256(canonical_comparison_references_json(references)).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
