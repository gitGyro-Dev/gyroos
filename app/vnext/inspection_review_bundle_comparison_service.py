from __future__ import annotations

import json

from .inspection_review_bundle_comparison import (
    ExperimentalReviewBundleComparisonReport,
    ExperimentalReviewBundleComparisonRequest,
    ExperimentalReviewBundleComparisonResult,
    ExperimentalReviewBundleComparisonSettings,
    ExperimentalReviewBundleReference,
    experimental_review_bundle_comparison_settings,
    utc_now,
)


class ExperimentalReviewBundleComparisonError(ValueError):
    pass


class ExperimentalReviewBundleComparisonIdentityError(ExperimentalReviewBundleComparisonError):
    pass


class ExperimentalReviewBundleComparisonDuplicateError(ExperimentalReviewBundleComparisonError):
    pass


class ExperimentalReviewBundleComparisonResourceLimitError(ExperimentalReviewBundleComparisonError):
    pass


class ExperimentalReviewBundleComparisonService:
    def __init__(
        self,
        settings: ExperimentalReviewBundleComparisonSettings = experimental_review_bundle_comparison_settings,
    ) -> None:
        self.settings = settings

    def compare(
        self,
        request: ExperimentalReviewBundleComparisonRequest,
    ) -> ExperimentalReviewBundleComparisonResult:
        self._validate_request(request)

        left_ids = request.left_bundle.comparison_ids
        right_ids = request.right_bundle.comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_set)
        removed = tuple(item for item in left_ids if item not in right_set)
        retained = tuple(item for item in left_ids if item in right_set)

        left_digest = request.left_bundle.bundle_digest
        right_digest = request.right_bundle.bundle_digest
        digest_changed = (
            None
            if left_digest is None or right_digest is None
            else left_digest != right_digest
        )

        report = ExperimentalReviewBundleComparisonReport(
            bundle_comparison_id=request.bundle_comparison_id,
            left_review_bundle_id=request.left_bundle.review_bundle_id,
            right_review_bundle_id=request.right_bundle.review_bundle_id,
            added_comparison_ids=added,
            removed_comparison_ids=removed,
            retained_comparison_ids=retained,
            left_bundle_digest=left_digest,
            right_bundle_digest=right_digest,
            digest_changed=digest_changed,
            created_at=utc_now(),
            warnings=request.warnings,
            metadata=request.metadata,
        )
        return ExperimentalReviewBundleComparisonResult(report=report)

    def _validate_request(self, request: ExperimentalReviewBundleComparisonRequest) -> None:
        self._validate_identifier("bundle_comparison_id", request.bundle_comparison_id)
        self._validate_bundle_reference("left_bundle", request.left_bundle)
        self._validate_bundle_reference("right_bundle", request.right_bundle)

        if request.left_bundle.review_bundle_id == request.right_bundle.review_bundle_id:
            raise ExperimentalReviewBundleComparisonIdentityError(
                "left and right review bundle IDs must be distinct"
            )

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalReviewBundleComparisonResourceLimitError(
                "warning count exceeds configured limit"
            )

        metadata_bytes = len(
            json.dumps(
                request.metadata,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalReviewBundleComparisonResourceLimitError(
                "metadata exceeds configured byte limit"
            )

    def _validate_bundle_reference(
        self,
        side: str,
        reference: ExperimentalReviewBundleReference,
    ) -> None:
        self._validate_identifier(f"{side}.review_bundle_id", reference.review_bundle_id)

        comparison_ids = reference.comparison_ids
        if len(comparison_ids) > self.settings.max_comparison_reference_count:
            raise ExperimentalReviewBundleComparisonResourceLimitError(
                f"{side} comparison reference count exceeds configured limit"
            )
        if len(set(comparison_ids)) != len(comparison_ids):
            raise ExperimentalReviewBundleComparisonDuplicateError(
                f"{side} contains duplicate comparison IDs"
            )
        for comparison_id in comparison_ids:
            self._validate_identifier(f"{side}.comparison_id", comparison_id)

    def _validate_identifier(self, name: str, value: str) -> None:
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalReviewBundleComparisonResourceLimitError(
                f"{name} exceeds configured length limit"
            )
