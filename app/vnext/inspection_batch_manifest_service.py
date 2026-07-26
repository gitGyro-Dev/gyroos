from __future__ import annotations

import json
from copy import deepcopy

from .inspection_batch_manifest import (
    ExperimentalInspectionBatchDigestPolicy,
    ExperimentalInspectionBatchManifest,
    ExperimentalInspectionBatchRequest,
    ExperimentalInspectionBatchResult,
    ExperimentalInspectionBatchSettings,
    ExperimentalInspectionReceiptReference,
    utc_now,
)


class ExperimentalInspectionBatchError(ValueError):
    """Base error for bounded inspection batch manifest assembly."""


class ExperimentalInspectionBatchIdentityError(ExperimentalInspectionBatchError):
    """Raised when manifest or receipt reference identity is invalid."""


class ExperimentalInspectionBatchDuplicateError(ExperimentalInspectionBatchError):
    """Raised when duplicate receipt references are supplied."""


class ExperimentalInspectionBatchResourceLimitError(ExperimentalInspectionBatchError):
    """Raised when bounded manifest resource limits are exceeded."""


class ExperimentalInspectionBatchService:
    """Assemble one request-local manifest from explicit receipt references only."""

    def __init__(
        self,
        settings: ExperimentalInspectionBatchSettings | None = None,
        digest_policy: ExperimentalInspectionBatchDigestPolicy | None = None,
    ) -> None:
        self._settings = settings or ExperimentalInspectionBatchSettings()
        self._digest_policy = digest_policy or ExperimentalInspectionBatchDigestPolicy()

    def create_manifest(
        self,
        request: ExperimentalInspectionBatchRequest,
    ) -> ExperimentalInspectionBatchResult:
        self._validate_request(request)

        copied_references = tuple(
            ExperimentalInspectionReceiptReference.model_validate(
                reference.model_dump(mode="python")
            )
            for reference in request.receipt_references
        )
        digest_input = [
            reference.model_dump(mode="json") for reference in copied_references
        ]
        manifest = ExperimentalInspectionBatchManifest(
            manifest_id=request.manifest_id,
            receipt_references=copied_references,
            receipt_reference_digest=self._digest_policy.digest(digest_input),
            digest_algorithm=self._digest_policy.algorithm,
            canonicalization=self._digest_policy.canonicalization,
            created_at=utc_now(),
            warnings=tuple(request.warnings),
            source_refs=tuple(request.source_refs),
            metadata=deepcopy(request.manifest_metadata),
        )
        return ExperimentalInspectionBatchResult(
            batch_manifest_created=True,
            manifest=manifest,
        )

    def _validate_request(self, request: ExperimentalInspectionBatchRequest) -> None:
        settings = self._settings
        if not request.receipt_references:
            raise ExperimentalInspectionBatchIdentityError(
                "at least one receipt reference is required"
            )
        if len(request.receipt_references) > settings.max_receipt_count:
            raise ExperimentalInspectionBatchResourceLimitError(
                "receipt reference count exceeds manifest limit"
            )
        receipt_ids = [reference.receipt_id for reference in request.receipt_references]
        if len(set(receipt_ids)) != len(receipt_ids):
            raise ExperimentalInspectionBatchDuplicateError(
                "receipt references must use unique receipt_id values"
            )
        if len(request.warnings) > settings.max_warning_count:
            raise ExperimentalInspectionBatchResourceLimitError(
                "warning count exceeds manifest limit"
            )
        if len(request.source_refs) > settings.max_source_ref_count:
            raise ExperimentalInspectionBatchResourceLimitError(
                "source reference count exceeds manifest limit"
            )
        metadata_size = len(
            json.dumps(
                request.manifest_metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if metadata_size > settings.max_metadata_bytes:
            raise ExperimentalInspectionBatchResourceLimitError(
                "manifest metadata exceeds byte limit"
            )
        for reference in request.receipt_references:
            self._validate_reference(reference)

    def _validate_reference(
        self,
        reference: ExperimentalInspectionReceiptReference,
    ) -> None:
        settings = self._settings
        limits = (
            ("receipt_id", reference.receipt_id, settings.max_receipt_id_length),
            ("source_record_id", reference.source_record_id, settings.max_record_id_length),
            ("source_process_id", reference.source_process_id, settings.max_process_id_length),
            ("source_record_type", reference.source_record_type, settings.max_record_type_length),
            (
                "source_contract_version",
                reference.source_contract_version,
                settings.max_version_length,
            ),
            (
                "consumer_contract_version",
                reference.consumer_contract_version,
                settings.max_version_length,
            ),
        )
        for name, value, maximum in limits:
            if len(value) > maximum:
                raise ExperimentalInspectionBatchResourceLimitError(
                    f"{name} exceeds manifest limit"
                )
