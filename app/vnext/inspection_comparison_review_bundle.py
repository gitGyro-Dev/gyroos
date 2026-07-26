from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonReviewBundleModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


@dataclass(frozen=True, slots=True)
class ExperimentalComparisonReviewBundleSettings:
    max_comparison_count: int = 128
    max_identifier_length: int = 128
    max_warning_count: int = 64
    max_source_ref_count: int = 64
    max_metadata_bytes: int = 16_384

    def __post_init__(self) -> None:
        for name, value in (
            ("max_comparison_count", self.max_comparison_count),
            ("max_identifier_length", self.max_identifier_length),
            ("max_warning_count", self.max_warning_count),
            ("max_source_ref_count", self.max_source_ref_count),
            ("max_metadata_bytes", self.max_metadata_bytes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class ReviewBundleDigestAlgorithm(StrEnum):
    SHA256 = "SHA-256"


class ExperimentalComparisonReviewBundleDigestPolicy(ExperimentalComparisonReviewBundleModel):
    algorithm: ReviewBundleDigestAlgorithm = ReviewBundleDigestAlgorithm.SHA256
    canonicalization: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"

    @field_validator("canonicalization")
    @classmethod
    def validate_canonicalization(cls, value: str) -> str:
        if value != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
            raise ValueError("unsupported canonicalization profile")
        return value

    def digest(self, value: Any) -> str:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class ExperimentalComparisonReportReference(ExperimentalComparisonReviewBundleModel):
    comparison_id: str
    left_manifest_id: str
    right_manifest_id: str
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None

    @field_validator("comparison_id", "left_manifest_id", "right_manifest_id")
    @classmethod
    def reject_blank_identifiers(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("comparison reference identifiers must not be empty")
        return normalized


class ExperimentalComparisonReviewBundleRequest(ExperimentalComparisonReviewBundleModel):
    review_bundle_id: str
    comparison_references: tuple[ExperimentalComparisonReportReference, ...]
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("review_bundle_id")
    @classmethod
    def reject_blank_bundle_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("review_bundle_id must not be empty")
        return normalized


class ExperimentalComparisonReviewBundle(ExperimentalComparisonReviewBundleModel):
    review_bundle_id: str
    comparison_references: tuple[ExperimentalComparisonReportReference, ...]
    ordered_reference_digest: str
    digest_algorithm: ReviewBundleDigestAlgorithm
    canonicalization: str
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonReviewBundleResult(ExperimentalComparisonReviewBundleModel):
    review_bundle_created: bool
    bundle: ExperimentalComparisonReviewBundle


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


experimental_comparison_review_bundle_settings = ExperimentalComparisonReviewBundleSettings()
