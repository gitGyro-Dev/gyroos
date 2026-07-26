from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExperimentalManifestComparisonModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


@dataclass(frozen=True, slots=True)
class ExperimentalManifestComparisonSettings:
    max_receipt_count_per_manifest: int = 256
    max_manifest_id_length: int = 256
    max_comparison_id_length: int = 256
    max_digest_length: int = 128
    max_warning_count: int = 32
    max_metadata_bytes: int = 65_536

    def __post_init__(self) -> None:
        for name, value in (
            ("max_receipt_count_per_manifest", self.max_receipt_count_per_manifest),
            ("max_manifest_id_length", self.max_manifest_id_length),
            ("max_comparison_id_length", self.max_comparison_id_length),
            ("max_digest_length", self.max_digest_length),
            ("max_warning_count", self.max_warning_count),
            ("max_metadata_bytes", self.max_metadata_bytes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class ExperimentalManifestReference(ExperimentalManifestComparisonModel):
    manifest_id: str
    receipt_ids: tuple[str, ...]
    manifest_digest: str | None = None

    @field_validator("manifest_id")
    @classmethod
    def reject_blank_manifest_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("manifest_id must not be empty")
        return normalized

    @field_validator("receipt_ids")
    @classmethod
    def reject_blank_receipt_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(value.strip() for value in values)
        if any(not value for value in normalized):
            raise ValueError("receipt_ids must not contain empty values")
        return normalized

    @field_validator("manifest_digest")
    @classmethod
    def normalize_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("manifest_digest must not be blank")
        if any(character not in "0123456789abcdef" for character in normalized):
            raise ValueError("manifest_digest must be a lowercase hexadecimal label")
        return normalized


class ExperimentalManifestComparisonRequest(ExperimentalManifestComparisonModel):
    comparison_id: str
    left: ExperimentalManifestReference
    right: ExperimentalManifestReference
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("comparison_id")
    @classmethod
    def reject_blank_comparison_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("comparison_id must not be empty")
        return normalized


class ExperimentalManifestComparisonReport(ExperimentalManifestComparisonModel):
    comparison_id: str
    left_manifest_id: str
    right_manifest_id: str
    added_receipt_ids: tuple[str, ...]
    removed_receipt_ids: tuple[str, ...]
    retained_receipt_ids: tuple[str, ...]
    left_manifest_digest: str | None = None
    right_manifest_digest: str | None = None
    digest_changed: bool | None = None
    created_at: datetime = Field(default_factory=utc_now)
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, object] = Field(default_factory=dict)


class ExperimentalManifestComparisonResult(ExperimentalManifestComparisonModel):
    comparison_report_created: bool
    report: ExperimentalManifestComparisonReport


experimental_manifest_comparison_settings = ExperimentalManifestComparisonSettings()
