from __future__ import annotations

import json

from .inspection_manifest_comparison import (
    ExperimentalManifestComparisonReport,
    ExperimentalManifestComparisonRequest,
    ExperimentalManifestComparisonResult,
    ExperimentalManifestComparisonSettings,
)


class ExperimentalManifestComparisonError(ValueError):
    """Base error for bounded request-local manifest comparison."""


class ExperimentalManifestComparisonIdentityError(ExperimentalManifestComparisonError):
    """Raised when manifest or comparison identity constraints are violated."""


class ExperimentalManifestComparisonDuplicateError(ExperimentalManifestComparisonError):
    """Raised when a manifest reference contains duplicate receipt IDs."""


class ExperimentalManifestComparisonResourceLimitError(ExperimentalManifestComparisonError):
    """Raised when bounded comparison resource limits are exceeded."""


class ExperimentalManifestComparisonService:
    """Compare two explicit manifest references without retrieval or semantic inference."""

    def __init__(
        self,
        settings: ExperimentalManifestComparisonSettings | None = None,
    ) -> None:
        self._settings = settings or ExperimentalManifestComparisonSettings()

    def compare(
        self,
        request: ExperimentalManifestComparisonRequest,
    ) -> ExperimentalManifestComparisonResult:
        self._validate_request(request)

        left_ids = request.left.receipt_ids
        right_ids = request.right.receipt_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(receipt_id for receipt_id in right_ids if receipt_id not in left_set)
        removed = tuple(receipt_id for receipt_id in left_ids if receipt_id not in right_set)
        retained = tuple(receipt_id for receipt_id in left_ids if receipt_id in right_set)

        if request.left.manifest_digest is None or request.right.manifest_digest is None:
            digest_changed: bool | None = None
        else:
            digest_changed = request.left.manifest_digest != request.right.manifest_digest

        report = ExperimentalManifestComparisonReport(
            comparison_id=request.comparison_id,
            left_manifest_id=request.left.manifest_id,
            right_manifest_id=request.right.manifest_id,
            added_receipt_ids=added,
            removed_receipt_ids=removed,
            retained_receipt_ids=retained,
            left_manifest_digest=request.left.manifest_digest,
            right_manifest_digest=request.right.manifest_digest,
            digest_changed=digest_changed,
            warnings=request.warnings,
            metadata=dict(request.metadata),
        )
        return ExperimentalManifestComparisonResult(
            comparison_report_created=True,
            report=report,
        )

    def _validate_request(self, request: ExperimentalManifestComparisonRequest) -> None:
        settings = self._settings

        if request.left.manifest_id == request.right.manifest_id:
            raise ExperimentalManifestComparisonIdentityError(
                "left and right manifest IDs must be distinct"
            )

        if len(request.comparison_id) > settings.max_comparison_id_length:
            raise ExperimentalManifestComparisonResourceLimitError(
                "comparison_id exceeds comparison limit"
            )

        for side_name, reference in (("left", request.left), ("right", request.right)):
            if len(reference.manifest_id) > settings.max_manifest_id_length:
                raise ExperimentalManifestComparisonResourceLimitError(
                    f"{side_name} manifest_id exceeds comparison limit"
                )
            if len(reference.receipt_ids) > settings.max_receipt_count_per_manifest:
                raise ExperimentalManifestComparisonResourceLimitError(
                    f"{side_name} receipt count exceeds comparison limit"
                )
            if len(set(reference.receipt_ids)) != len(reference.receipt_ids):
                raise ExperimentalManifestComparisonDuplicateError(
                    f"{side_name} receipt_ids must be unique"
                )
            if (
                reference.manifest_digest is not None
                and len(reference.manifest_digest) > settings.max_digest_length
            ):
                raise ExperimentalManifestComparisonResourceLimitError(
                    f"{side_name} manifest_digest exceeds comparison limit"
                )

        if len(request.warnings) > settings.max_warning_count:
            raise ExperimentalManifestComparisonResourceLimitError(
                "warning count exceeds comparison limit"
            )

        metadata_bytes = len(
            json.dumps(
                request.metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if metadata_bytes > settings.max_metadata_bytes:
            raise ExperimentalManifestComparisonResourceLimitError(
                "metadata exceeds comparison limit"
            )
