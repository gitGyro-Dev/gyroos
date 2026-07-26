from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import ExperimentalRecordEnvelope


@dataclass(frozen=True, slots=True)
class ExperimentalApiSettings:
    """Resource limits for the isolated public experimental record API."""

    max_payload_bytes: int = 262_144
    max_metadata_bytes: int = 32_768
    max_list_results: int = 100
    max_record_id_length: int = 128
    max_record_type_length: int = 128

    def __post_init__(self) -> None:
        for name in (
            "max_payload_bytes",
            "max_metadata_bytes",
            "max_list_results",
            "max_record_id_length",
            "max_record_type_length",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be greater than zero")


class ExperimentalApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExperimentalRecordCreateRequest(ExperimentalApiModel):
    record_id: str = Field(min_length=1)
    process_id: str = Field(min_length=1)
    record_type: str = Field(min_length=1)
    payload: dict[str, Any]
    source_ref: str | None = None
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_public_limits(self) -> "ExperimentalRecordCreateRequest":
        settings = experimental_api_settings
        if len(self.record_id) > settings.max_record_id_length:
            raise ValueError("record_id exceeds experimental API limit")
        if len(self.record_type) > settings.max_record_type_length:
            raise ValueError("record_type exceeds experimental API limit")
        if _json_size(self.payload) > settings.max_payload_bytes:
            raise ValueError("payload exceeds experimental API byte limit")
        if _json_size(self.metadata) > settings.max_metadata_bytes:
            raise ValueError("metadata exceeds experimental API byte limit")
        return self

    def to_envelope(self) -> ExperimentalRecordEnvelope:
        return ExperimentalRecordEnvelope(
            record_id=self.record_id,
            process_id=self.process_id,
            record_type=self.record_type,
            payload=self.payload,
            source_ref=self.source_ref,
            provisional=self.provisional,
            metadata=self.metadata,
        )


class ExperimentalRecordResponse(ExperimentalApiModel):
    record: ExperimentalRecordEnvelope


class ExperimentalRecordListResponse(ExperimentalApiModel):
    records: list[ExperimentalRecordEnvelope] = Field(default_factory=list)
    count: int = Field(ge=0)
    ordering: str = "UNSPECIFIED"


class ExperimentalApiError(ExperimentalApiModel):
    error_code: str
    message: str
    category: str
    phase: str
    retryable: bool = False


def _json_size(value: Any) -> int:
    try:
        return len(
            json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("value must be JSON serializable") from exc


experimental_api_settings = ExperimentalApiSettings()
