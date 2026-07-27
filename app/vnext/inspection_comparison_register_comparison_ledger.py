from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonRegisterComparisonLedgerSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_comparison_references: int = Field(default=64, ge=1, le=256)
    max_identifier_length: int = Field(default=128, ge=1, le=512)
    max_warning_count: int = Field(default=32, ge=0, le=256)
    max_source_ref_count: int = Field(default=32, ge=0, le=256)
    max_metadata_bytes: int = Field(default=8192, ge=0, le=65536)


class ExperimentalComparisonRegisterComparisonLedgerDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: Literal["SHA-256"] = "SHA-256"
    canonicalization: Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"] = (
        "JSON_SORTED_KEYS_UTF8_COMPACT_V1"
    )

    def digest(self, references: tuple[ExperimentalComparisonRegisterComparisonReference, ...]) -> str:
        canonical = json.dumps(
            [reference.model_dump(mode="json") for reference in references],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


class ExperimentalComparisonRegisterComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    register_comparison_id: str = Field(min_length=1, max_length=512)
    left_comparison_register_id: str = Field(min_length=1, max_length=512)
    right_comparison_register_id: str = Field(min_length=1, max_length=512)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None


class ExperimentalComparisonRegisterComparisonLedgerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_ledger_id: str = Field(min_length=1, max_length=512)
    comparison_references: tuple[ExperimentalComparisonRegisterComparisonReference, ...]
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    ledger_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("comparison_references")
    @classmethod
    def references_must_not_be_empty(
        cls,
        value: tuple[ExperimentalComparisonRegisterComparisonReference, ...],
    ) -> tuple[ExperimentalComparisonRegisterComparisonReference, ...]:
        if not value:
            raise ValueError("comparison_references must not be empty")
        return value


class ExperimentalComparisonRegisterComparisonLedgerManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_ledger_id: str
    comparison_references: tuple[ExperimentalComparisonRegisterComparisonReference, ...]
    comparison_count: int = Field(ge=1)
    digest_algorithm: Literal["SHA-256"]
    digest_canonicalization: Literal["JSON_SORTED_KEYS_UTF8_COMPACT_V1"]
    ledger_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    ledger_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonRegisterComparisonLedgerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_ledger_created: Literal[True] = True
    manifest: ExperimentalComparisonRegisterComparisonLedgerManifest


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
