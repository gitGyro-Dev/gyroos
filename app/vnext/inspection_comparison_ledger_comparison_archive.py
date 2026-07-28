from __future__ import annotations

from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonLedgerComparisonArchiveSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_references: int = Field(default=100, ge=1, le=1000)
    max_identifier_length: int = Field(default=256, ge=1, le=2048)
    max_warnings: int = Field(default=50, ge=0, le=500)
    max_source_refs: int = Field(default=100, ge=0, le=1000)
    max_metadata_bytes: int = Field(default=16_384, ge=0, le=1_048_576)


class ExperimentalComparisonLedgerComparisonArchiveDigestAlgorithm(str, Enum):
    SHA_256 = "SHA-256"


class ExperimentalComparisonLedgerComparisonArchiveCanonicalization(str, Enum):
    JSON_SORTED_KEYS_UTF8_COMPACT_V1 = "JSON_SORTED_KEYS_UTF8_COMPACT_V1"


class ExperimentalComparisonLedgerComparisonArchiveDigestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: ExperimentalComparisonLedgerComparisonArchiveDigestAlgorithm = (
        ExperimentalComparisonLedgerComparisonArchiveDigestAlgorithm.SHA_256
    )
    canonicalization: ExperimentalComparisonLedgerComparisonArchiveCanonicalization = (
        ExperimentalComparisonLedgerComparisonArchiveCanonicalization.JSON_SORTED_KEYS_UTF8_COMPACT_V1
    )


class ExperimentalComparisonLedgerComparisonReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ledger_comparison_id: str = Field(min_length=1, max_length=256)
    left_comparison_ledger_id: str = Field(min_length=1, max_length=256)
    right_comparison_ledger_id: str = Field(min_length=1, max_length=256)
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    digest_changed: bool | None = None


class ExperimentalComparisonLedgerComparisonArchiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_archive_id: str = Field(min_length=1, max_length=256)
    ledger_comparisons: tuple[ExperimentalComparisonLedgerComparisonReference, ...]
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)
    digest_policy: ExperimentalComparisonLedgerComparisonArchiveDigestPolicy = Field(
        default_factory=ExperimentalComparisonLedgerComparisonArchiveDigestPolicy
    )

    @field_validator("ledger_comparisons")
    @classmethod
    def require_references(
        cls,
        value: tuple[ExperimentalComparisonLedgerComparisonReference, ...],
    ) -> tuple[ExperimentalComparisonLedgerComparisonReference, ...]:
        if not value:
            raise ValueError("ledger_comparisons must not be empty")
        return value


class ExperimentalComparisonLedgerComparisonArchiveManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_archive_id: str
    ledger_comparisons: tuple[ExperimentalComparisonLedgerComparisonReference, ...]
    reference_count: int = Field(ge=1)
    archive_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    digest_policy: ExperimentalComparisonLedgerComparisonArchiveDigestPolicy
    created_at: datetime
    warnings: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonLedgerComparisonArchiveResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    result: str = Field(default="comparison_archive_created")
    manifest: ExperimentalComparisonLedgerComparisonArchiveManifest


def canonicalize_comparison_ledger_comparison_references(
    references: tuple[ExperimentalComparisonLedgerComparisonReference, ...],
    policy: ExperimentalComparisonLedgerComparisonArchiveDigestPolicy,
) -> bytes:
    if (
        policy.algorithm
        != ExperimentalComparisonLedgerComparisonArchiveDigestAlgorithm.SHA_256
        or policy.canonicalization
        != ExperimentalComparisonLedgerComparisonArchiveCanonicalization.JSON_SORTED_KEYS_UTF8_COMPACT_V1
    ):
        raise ValueError("unsupported comparison archive digest policy")

    payload = [reference.model_dump(mode="json") for reference in references]
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_comparison_ledger_comparison_archive_digest(
    references: tuple[ExperimentalComparisonLedgerComparisonReference, ...],
    policy: ExperimentalComparisonLedgerComparisonArchiveDigestPolicy,
) -> str:
    return sha256(
        canonicalize_comparison_ledger_comparison_references(references, policy)
    ).hexdigest()
