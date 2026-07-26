from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .consumer_compatibility import (
    ExperimentalContractDescriptor,
    ExperimentalConsumerCompatibilityResult,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ExperimentalInspectionReceiptSettings:
    max_receipt_id_length: int = 256
    max_source_ref_count: int = 64
    max_warning_count: int = 64
    max_metadata_bytes: int = 65_536
    allow_incompatible_attempt_receipts: bool = True

    def __post_init__(self) -> None:
        for name, value in (
            ("max_receipt_id_length", self.max_receipt_id_length),
            ("max_source_ref_count", self.max_source_ref_count),
            ("max_warning_count", self.max_warning_count),
            ("max_metadata_bytes", self.max_metadata_bytes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class ExperimentalInspectionReceiptModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DigestAlgorithm(str, Enum):
    SHA256 = "SHA-256"


class ExperimentalDigestPolicy(ExperimentalInspectionReceiptModel):
    algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
    canonicalization: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"
    include_payload_digest: bool = True
    include_metadata_digest: bool = True

    @field_validator("canonicalization")
    @classmethod
    def validate_canonicalization(cls, value: str) -> str:
        if value != "JSON_SORTED_KEYS_UTF8_COMPACT_V1":
            raise ValueError("unsupported canonicalization policy")
        return value

    def canonical_json_bytes(self, value: Any) -> bytes:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

    def digest(self, value: Any) -> str:
        if self.algorithm != DigestAlgorithm.SHA256:
            raise ValueError("unsupported digest algorithm")
        return hashlib.sha256(self.canonical_json_bytes(value)).hexdigest()


class ExperimentalInspectionReceiptRequest(ExperimentalInspectionReceiptModel):
    receipt_id: str
    source_record_id: str
    source_process_id: str
    source_record_type: str
    source_contract: ExperimentalContractDescriptor
    consumer_contract: ExperimentalContractDescriptor
    compatibility_result: ExperimentalConsumerCompatibilityResult
    payload: dict[str, Any] | None = None
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    source_refs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    receipt_metadata: dict[str, Any] = Field(default_factory=dict)
    inspected_at: datetime = Field(default_factory=utc_now)


class ExperimentalInspectionReceipt(ExperimentalInspectionReceiptModel):
    receipt_id: str
    source_record_id: str
    source_process_id: str
    source_record_type: str
    source_contract: ExperimentalContractDescriptor
    consumer_contract: ExperimentalContractDescriptor
    compatibility_result: ExperimentalConsumerCompatibilityResult
    payload_digest: str | None = None
    metadata_digest: str | None = None
    digest_algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
    canonicalization: str = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"
    source_refs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    receipt_metadata: dict[str, Any] = Field(default_factory=dict)
    inspected_at: datetime


class ExperimentalInspectionReceiptResult(ExperimentalInspectionReceiptModel):
    receipt_created: bool
    receipt: ExperimentalInspectionReceipt
