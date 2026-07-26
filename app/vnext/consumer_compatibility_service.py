from __future__ import annotations

from .consumer_compatibility import (
    CompatibilityDisposition,
    ExperimentalCompatibilitySettings,
    ExperimentalConsumerCompatibilityRequest,
    ExperimentalConsumerCompatibilityResult,
)


class ExperimentalCompatibilityError(ValueError):
    """Base error for malformed compatibility inputs."""


class ExperimentalCompatibilityPolicy:
    """Declarative compatibility policy for inspection-only consumers."""

    def __init__(self, settings: ExperimentalCompatibilitySettings | None = None) -> None:
        self._settings = settings or ExperimentalCompatibilitySettings()

    def evaluate(
        self,
        request: ExperimentalConsumerCompatibilityRequest,
    ) -> ExperimentalConsumerCompatibilityResult:
        descriptor = request.descriptor
        try:
            source_version = descriptor.source_version()
            consumer_version = descriptor.consumer_version()
        except ValueError as exc:
            raise ExperimentalCompatibilityError(str(exc)) from exc

        warnings: list[str] = []
        rejection_reason: str | None = None

        if descriptor.source_api_namespace != self._settings.source_api_namespace:
            rejection_reason = "source_api_namespace_mismatch"
        elif source_version.major != self._settings.supported_source_major:
            rejection_reason = "unsupported_source_major_version"
        elif consumer_version.major != self._settings.supported_consumer_major:
            rejection_reason = "unsupported_consumer_major_version"
        elif source_version.major != consumer_version.major:
            rejection_reason = "source_consumer_major_version_mismatch"
        elif (
            request.expected_record_type is not None
            and descriptor.record_type != request.expected_record_type
        ):
            rejection_reason = "record_type_mismatch"

        if rejection_reason is not None:
            return ExperimentalConsumerCompatibilityResult(
                compatible_for_inspection=False,
                disposition=CompatibilityDisposition.INCOMPATIBLE,
                source_contract_version=descriptor.source_contract_version,
                consumer_contract_version=descriptor.consumer_contract_version,
                record_type=descriptor.record_type,
                warnings=[],
                rejection_reason=rejection_reason,
            )

        if source_version.minor != consumer_version.minor:
            warnings.append("minor_version_mismatch")
        if source_version.patch != consumer_version.patch:
            warnings.append("patch_version_mismatch")

        warnings = warnings[: self._settings.max_warning_count]
        disposition = (
            CompatibilityDisposition.COMPATIBLE_WITH_WARNING
            if warnings
            else CompatibilityDisposition.COMPATIBLE
        )
        return ExperimentalConsumerCompatibilityResult(
            compatible_for_inspection=True,
            disposition=disposition,
            source_contract_version=descriptor.source_contract_version,
            consumer_contract_version=descriptor.consumer_contract_version,
            record_type=descriptor.record_type,
            warnings=warnings,
            rejection_reason=None,
        )


class ExperimentalConsumerCompatibilityService:
    """Request-local service wrapper with no Runtime or persistence side effects."""

    def __init__(self, policy: ExperimentalCompatibilityPolicy | None = None) -> None:
        self._policy = policy or ExperimentalCompatibilityPolicy()

    def check(
        self,
        request: ExperimentalConsumerCompatibilityRequest,
    ) -> ExperimentalConsumerCompatibilityResult:
        return self._policy.evaluate(request)
