from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalComparisonLedgerComparisonSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_identifier_length: int = Field(default=128, ge=1, le=512)
    max_references_per_side: int = Field(default=128, ge=1, le=2048)
    max_warnings: int = Field(default=32, ge=0, le=256)
    max_metadata_bytes: int = Field(default=4096, ge=0, le=65536)


class ExperimentalComparisonLedgerReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    comparison_ledger_id: str = Field(min_length=1, max_length=512)
    register_comparison_ids: tuple[str, ...] = Field(default_factory=tuple)
    ledger_digest: str | None = None

    @field_validator("ledger_digest")
    @classmethod
    def validate_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError("ledger_digest must be a lowercase SHA-256 hex label")
        return value


class ExperimentalComparisonLedgerComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ledger_comparison_id: str = Field(min_length=1, max_length=512)
    left: ExperimentalComparisonLedgerReference
    right: ExperimentalComparisonLedgerReference
    created_at: datetime
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentalComparisonLedgerComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ledger_comparison_id: str
    left_comparison_ledger_id: str
    right_comparison_ledger_id: str
    added_register_comparison_ids: tuple[str, ...]
    removed_register_comparison_ids: tuple[str, ...]
    retained_register_comparison_ids: tuple[str, ...]
    left_ledger_digest: str | None
    right_ledger_digest: str | None
    digest_changed: bool | None
    created_at: datetime
    warnings: tuple[str, ...]
    metadata: dict[str, Any]


class ExperimentalComparisonLedgerComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    result: str = "comparison_ledger_comparison_created"
    report: ExperimentalComparisonLedgerComparisonReport
