from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExperimentalCompatibilityModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


@dataclass(frozen=True, slots=True)
class ExperimentalCompatibilitySettings:
    source_api_namespace: str = "/vnext/experimental"
    supported_source_major: int = 1
    supported_consumer_major: int = 1
    warn_on_minor_mismatch: bool = True
    max_namespace_length: int = 128
    max_version_length: int = 32
    max_record_type_length: int = 128
    max_warning_count: int = 16

    def __post_init__(self) -> None:
        if not self.source_api_namespace.strip():
            raise ValueError("source_api_namespace must not be empty")
        for name, value in (
            ("supported_source_major", self.supported_source_major),
            ("supported_consumer_major", self.supported_consumer_major),
            ("max_namespace_length", self.max_namespace_length),
            ("max_version_length", self.max_version_length),
            ("max_record_type_length", self.max_record_type_length),
            ("max_warning_count", self.max_warning_count),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")


class CompatibilityDisposition(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    COMPATIBLE_WITH_WARNING = "COMPATIBLE_WITH_WARNING"
    INCOMPATIBLE = "INCOMPATIBLE"


class SemanticVersion(ExperimentalCompatibilityModel):
    major: int = Field(ge=0)
    minor: int = Field(ge=0)
    patch: int = Field(ge=0)

    @classmethod
    def parse(cls, raw: str) -> "SemanticVersion":
        parts = raw.strip().split(".")
        if len(parts) != 3 or any(not part.isdigit() for part in parts):
            raise ValueError("version must use numeric major.minor.patch format")
        return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))

    def label(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class ExperimentalContractDescriptor(ExperimentalCompatibilityModel):
    source_api_namespace: str
    source_contract_version: str
    consumer_contract_version: str
    record_type: str

    @field_validator(
        "source_api_namespace",
        "source_contract_version",
        "consumer_contract_version",
        "record_type",
    )
    @classmethod
    def reject_blank_labels(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("contract labels must not be empty")
        return normalized

    def source_version(self) -> SemanticVersion:
        return SemanticVersion.parse(self.source_contract_version)

    def consumer_version(self) -> SemanticVersion:
        return SemanticVersion.parse(self.consumer_contract_version)


class ExperimentalConsumerCompatibilityRequest(ExperimentalCompatibilityModel):
    descriptor: ExperimentalContractDescriptor
    expected_record_type: str | None = None


class ExperimentalConsumerCompatibilityResult(ExperimentalCompatibilityModel):
    compatible_for_inspection: bool
    disposition: CompatibilityDisposition
    source_contract_version: str
    consumer_contract_version: str
    record_type: str
    warnings: list[str] = Field(default_factory=list)
    rejection_reason: str | None = None


experimental_compatibility_settings = ExperimentalCompatibilitySettings()
