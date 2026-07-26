from __future__ import annotations

from copy import deepcopy
from typing import Any

from .consumer_boundary import (
    ExperimentalConsumerReference,
    ExperimentalConsumerSnapshot,
    ExperimentalConsumptionRequest,
    ExperimentalConsumptionResult,
    ExperimentalConsumptionSettings,
    ExperimentalValidatedSnapshot,
)


class ExperimentalConsumptionError(ValueError):
    """Base error for read-only consumer boundary inspection."""


class ExperimentalRecordIdentityMismatchError(ExperimentalConsumptionError):
    pass


class ExperimentalProcessMismatchError(ExperimentalConsumptionError):
    pass


class ExperimentalRecordTypeMismatchError(ExperimentalConsumptionError):
    pass


class CallerSuppliedExperimentalEnvelopeAdapter:
    """Adapt one supplied experimental API envelope without typed reconstruction."""

    def adapt(self, envelope: dict[str, Any]) -> ExperimentalConsumerSnapshot:
        record = envelope.get("record", envelope)
        if not isinstance(record, dict):
            raise ExperimentalConsumptionError(
                "caller-supplied envelope must contain an object record"
            )
        return ExperimentalValidatedSnapshot.model_validate(deepcopy(record))


class ExperimentalRecordInspectionService:
    """Inspect one explicit record without consumer-specific semantic mapping."""

    def __init__(self, settings: ExperimentalConsumptionSettings | None = None) -> None:
        self._settings = settings or ExperimentalConsumptionSettings()

    def inspect(self, request: ExperimentalConsumptionRequest) -> ExperimentalConsumptionResult:
        reference: ExperimentalConsumerReference = request.reference
        snapshot = request.snapshot.model_copy(deep=True)

        if reference.record_id != snapshot.record_id:
            raise ExperimentalRecordIdentityMismatchError(
                "reference record_id must match supplied snapshot record_id"
            )
        if (
            reference.expected_process_id is not None
            and reference.expected_process_id != snapshot.process_id
        ):
            raise ExperimentalProcessMismatchError(
                "expected_process_id must match supplied snapshot process_id"
            )
        if (
            reference.expected_record_type is not None
            and reference.expected_record_type != snapshot.record_type
        ):
            raise ExperimentalRecordTypeMismatchError(
                "expected_record_type must match supplied snapshot record_type"
            )

        warnings: list[str] = []
        if snapshot.provisional:
            warnings.append("source_record_is_provisional")
        if not snapshot.payload:
            warnings.append("source_payload_is_empty")
        warnings = warnings[: self._settings.max_warning_count]

        copied_snapshot = ExperimentalConsumerSnapshot.model_validate(
            snapshot.model_dump(mode="python")
        )
        return ExperimentalConsumptionResult(
            record_id=copied_snapshot.record_id,
            process_id=copied_snapshot.process_id,
            record_type=copied_snapshot.record_type,
            accepted_for_inspection=True,
            warnings=list(warnings),
            snapshot=copied_snapshot,
        )
