from __future__ import annotations

import json

from .consumer_compatibility import CompatibilityDisposition
from .inspection_receipt import (
    ExperimentalDigestPolicy,
    ExperimentalInspectionReceipt,
    ExperimentalInspectionReceiptRequest,
    ExperimentalInspectionReceiptResult,
    ExperimentalInspectionReceiptSettings,
)


class ExperimentalInspectionReceiptError(ValueError):
    """Base error for request-local inspection receipt assembly."""


class ExperimentalReceiptIdentityError(ExperimentalInspectionReceiptError):
    """Raised when source identity and contract descriptors are inconsistent."""


class ExperimentalReceiptCompatibilityError(ExperimentalInspectionReceiptError):
    """Raised when compatibility result and receipt policy are inconsistent."""


class ExperimentalReceiptResourceLimitError(ExperimentalInspectionReceiptError):
    """Raised when bounded receipt resources exceed configured limits."""


class ExperimentalInspectionReceiptService:
    """Assemble one immutable request-local inspection receipt."""

    def __init__(
        self,
        settings: ExperimentalInspectionReceiptSettings | None = None,
        digest_policy: ExperimentalDigestPolicy | None = None,
    ) -> None:
        self._settings = settings or ExperimentalInspectionReceiptSettings()
        self._digest_policy = digest_policy or ExperimentalDigestPolicy()

    def create_receipt(
        self,
        request: ExperimentalInspectionReceiptRequest,
    ) -> ExperimentalInspectionReceiptResult:
        self._validate_identity(request)
        self._validate_compatibility(request)
        self._validate_resources(request)

        payload_digest = None
        if self._digest_policy.include_payload_digest and request.payload is not None:
            payload_digest = self._digest_policy.digest(request.payload)

        metadata_digest = None
        if self._digest_policy.include_metadata_digest:
            metadata_digest = self._digest_policy.digest(request.source_metadata)

        warnings = tuple(
            list(request.compatibility_result.warnings) + list(request.warnings)
        )[: self._settings.max_warning_count]

        receipt = ExperimentalInspectionReceipt(
            receipt_id=request.receipt_id,
            source_record_id=request.source_record_id,
            source_process_id=request.source_process_id,
            source_record_type=request.source_record_type,
            source_contract=request.source_contract,
            consumer_contract=request.consumer_contract,
            compatibility_result=request.compatibility_result,
            payload_digest=payload_digest,
            metadata_digest=metadata_digest,
            digest_algorithm=self._digest_policy.algorithm,
            canonicalization=self._digest_policy.canonicalization,
            source_refs=tuple(request.source_refs),
            warnings=warnings,
            receipt_metadata=dict(request.receipt_metadata),
            inspected_at=request.inspected_at,
        )
        return ExperimentalInspectionReceiptResult(
            receipt_created=True,
            receipt=receipt,
        )

    def _validate_identity(self, request: ExperimentalInspectionReceiptRequest) -> None:
        if request.source_contract.record_type != request.source_record_type:
            raise ExperimentalReceiptIdentityError(
                "source_contract record_type must match source_record_type"
            )
        if request.consumer_contract.record_type != request.source_record_type:
            raise ExperimentalReceiptIdentityError(
                "consumer_contract record_type must match source_record_type"
            )

    def _validate_compatibility(
        self,
        request: ExperimentalInspectionReceiptRequest,
    ) -> None:
        result = request.compatibility_result
        if (
            result.disposition == CompatibilityDisposition.COMPATIBLE
            and not result.compatible_for_inspection
        ):
            raise ExperimentalReceiptCompatibilityError(
                "compatible disposition requires compatible_for_inspection=true"
            )
        if (
            result.disposition == CompatibilityDisposition.INCOMPATIBLE
            and result.compatible_for_inspection
        ):
            raise ExperimentalReceiptCompatibilityError(
                "incompatible disposition requires compatible_for_inspection=false"
            )
        if (
            not result.compatible_for_inspection
            and not self._settings.allow_incompatible_attempt_receipts
        ):
            raise ExperimentalReceiptCompatibilityError(
                "incompatible inspection attempts are not permitted by receipt policy"
            )

    def _validate_resources(self, request: ExperimentalInspectionReceiptRequest) -> None:
        if not request.receipt_id or len(request.receipt_id) > self._settings.max_receipt_id_length:
            raise ExperimentalReceiptResourceLimitError("receipt_id exceeds receipt limit")
        if len(request.source_refs) > self._settings.max_source_ref_count:
            raise ExperimentalReceiptResourceLimitError("source_refs exceed receipt limit")
        if len(request.warnings) > self._settings.max_warning_count:
            raise ExperimentalReceiptResourceLimitError("warnings exceed receipt limit")
        metadata_size = len(
            json.dumps(
                request.receipt_metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if metadata_size > self._settings.max_metadata_bytes:
            raise ExperimentalReceiptResourceLimitError(
                "receipt_metadata exceeds receipt limit"
            )
