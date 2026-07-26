from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalInspectionBatchModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


@dataclass(frozen=True, slots=True)
class ExperimentalInspectionBatchSettings:
    max_receipt_count: int = 128
    max_receipt_id_length: int = 256
    max_record_id_length: int = 256
    max_process_id_length: int = 256
    max_record_type_length: int = 128
    max_version_length: int = 32
    max_warning_count: int = 64
    max_source_ref_count: int = 256
    max_metadata_bytes: int = 65_536

    def __post_init__(self) -> None:
        for name, value in (
            ("max_receipt_count", self.max_receipt_count),
            ("max_receipt_id_length", self.max_receipt_id_length),
            ("max_record_id_length", self.max_record_id_length),
            ("max_process_id_length", self.max_process_id_length),
            ("max_record_type_length", self.max_record_type_length),
            ("max_version_length", self.max_version_length),
            ("max_warning_count", self.max_warning_count),
            ("max_source_ref_count", self.max_source_ref_count),
            ("max_metadata_bytes", self.max_metadata_bytes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class BatchDigestAlgorithm(StrEnum):
    SHA_256 = "SHA-256"


class ExperimentalInspectionBatchDigestPolicy(ExperimentalInspectionBatchModel):
    algorithm: BatchDigestAlgorithm = BatchDigestAlgorithm.SHA_256
    canonicalization: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"

    @field_validator("canonicalization")
    @classmethod
    def validate_canonicalization(cls, value: str) -> str:
        if value != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
            raise ValueError("unsupported canonicalization profile")
        return value

    def canonical_bytes(self, value: Any) -> bytes:
        try:
            text = json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("value is not canonical JSON compatible") from exc
        return text.encode("utf-8")

    def digest(self, value: Any) -> str:
        return hashlib.sha256(self.canonical_bytes(value)).hexdigest()


class ExperimentalInspectionReceiptReference(ExperimentalInspectionBatchModel):
    receipt_id: str
    source_record_id: str
    source_process_id: str
    source_record_type: str
    source_contract_version: str
    consumer_contract_version: str
    compatible_for_inspection: bool
    payload_digest: str | None = None
    metadata_digest: str | None = None

    @field_validator(
        "receipt_id",
        "source_record_id",
        "source_process_id",
        "source_record_type",
        "source_contract_version",
        "consumer_contract_version",
    )
    @classmethod
    def reject_blank_labels(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("reference labels must not be empty")
        return normalized


class ExperimentalInspectionBatchRequest(ExperimentalInspectionBatchModel):
    manifest_id: str
    receipt_references: tuple[ExperimentalInspectionReceiptReference, ...]
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    manifest_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("manifest_id")
    @classmethod
    def validate_manifest_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("manifest_id must not be empty")
        return normalized


class ExperimentalInspectionBatchManifest(ExperimentalInspectionBatchModel):
    manifest_id: str
    receipt_references: tuple[ExperimentalInspectionReceiptReference, ...]
    receipt_reference_digest: str
    digest_algorithm: BatchDigestAlgorithm
    canonicalization: str
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalInspectionBatchResult(ExperimentalInspectionBatchModel):
    batch_manifest_created: bool
    manifest: ExperimentalInspectionBatchManifest


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
