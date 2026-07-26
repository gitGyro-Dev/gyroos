from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalReviewBundleComparisonModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


@dataclass(frozen=True, slots=True)
class ExperimentalReviewBundleComparisonSettings:
    max_identifier_length: int = 128
    max_comparison_reference_count: int = 256
    max_warning_count: int = 32
    max_metadata_bytes: int = 16384

    def __post_init__(self) -> None:
        for name, value in (
            ("max_identifier_length", self.max_identifier_length),
            ("max_comparison_reference_count", self.max_comparison_reference_count),
            ("max_warning_count", self.max_warning_count),
            ("max_metadata_bytes", self.max_metadata_bytes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class ExperimentalReviewBundleReference(ExperimentalReviewBundleComparisonModel):
    review_bundle_id: str
    comparison_ids: tuple[str, ...] = Field(default_factory=tuple)
    bundle_digest: str | None = None

    @field_validator("review_bundle_id")
    @classmethod
    def reject_blank_bundle_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("review_bundle_id must not be empty")
        return normalized

    @field_validator("comparison_ids")
    @classmethod
    def normalize_comparison_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in value)
        if any(not item for item in normalized):
            raise ValueError("comparison_ids must not contain empty values")
        return normalized

    @field_validator("bundle_digest")
    @classmethod
    def validate_optional_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
            raise ValueError("bundle_digest must be a 64-character lowercase hexadecimal SHA-256 label")
        return normalized


class ExperimentalReviewBundleComparisonRequest(ExperimentalReviewBundleComparisonModel):
    bundle_comparison_id: str
    left_bundle: ExperimentalReviewBundleReference
    right_bundle: ExperimentalReviewBundleReference
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("bundle_comparison_id")
    @classmethod
    def reject_blank_comparison_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("bundle_comparison_id must not be empty")
        return normalized

    @field_validator("warnings")
    @classmethod
    def normalize_warnings(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(item.strip() for item in value if item.strip())


class ExperimentalReviewBundleComparisonReport(ExperimentalReviewBundleComparisonModel):
    bundle_comparison_id: str
    left_review_bundle_id: str
    right_review_bundle_id: str
    added_comparison_ids: tuple[str, ...]
    removed_comparison_ids: tuple[str, ...]
    retained_comparison_ids: tuple[str, ...]
    left_bundle_digest: str | None
    right_bundle_digest: str | None
    digest_changed: bool | None
    created_at: datetime
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, object] = Field(default_factory=dict)


class ExperimentalReviewBundleComparisonResult(ExperimentalReviewBundleComparisonModel):
    review_bundle_comparison_created: bool = True
    report: ExperimentalReviewBundleComparisonReport


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


experimental_review_bundle_comparison_settings = ExperimentalReviewBundleComparisonSettings()
