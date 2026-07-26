from __future__ import annotations

import json

from .inspection_review_bundle_comparison_set import (
    ExperimentalReviewBundleComparisonSetManifest,
    ExperimentalReviewBundleComparisonSetRequest,
    ExperimentalReviewBundleComparisonSetResult,
    ExperimentalReviewBundleComparisonSetSettings,
    digest_comparison_references,
    utc_now,
)


class ExperimentalReviewBundleComparisonSetError(ValueError):
    pass


class ExperimentalReviewBundleComparisonSetIdentityError(
    ExperimentalReviewBundleComparisonSetError
):
    pass


class ExperimentalReviewBundleComparisonSetDuplicateError(
    ExperimentalReviewBundleComparisonSetError
):
    pass


class ExperimentalReviewBundleComparisonSetResourceLimitError(
    ExperimentalReviewBundleComparisonSetError
):
    pass


class ExperimentalReviewBundleComparisonSetService:
    def __init__(
        self,
        settings: ExperimentalReviewBundleComparisonSetSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalReviewBundleComparisonSetSettings()

    def create_set(
        self,
        request: ExperimentalReviewBundleComparisonSetRequest,
    ) -> ExperimentalReviewBundleComparisonSetResult:
        self._validate_identity(request)
        self._validate_references(request)
        self._validate_resources(request)

        try:
            digest = digest_comparison_references(
                request.comparison_references,
                request.digest_policy,
            )
        except ValueError as exc:
            raise ExperimentalReviewBundleComparisonSetError(str(exc)) from exc

        manifest = ExperimentalReviewBundleComparisonSetManifest(
            comparison_set_id=request.comparison_set_id,
            comparison_references=request.comparison_references,
            comparison_count=len(request.comparison_references),
            comparison_references_digest=digest,
            digest_algorithm=request.digest_policy.algorithm,
            canonicalization=request.digest_policy.canonicalization,
            created_at=utc_now(),
            warnings=request.warnings,
            source_refs=request.source_refs,
            metadata=dict(request.metadata),
        )
        return ExperimentalReviewBundleComparisonSetResult(
            comparison_set_created=True,
            comparison_set=manifest,
        )

    def _validate_identity(
        self,
        request: ExperimentalReviewBundleComparisonSetRequest,
    ) -> None:
        if not request.comparison_set_id.strip():
            raise ExperimentalReviewBundleComparisonSetIdentityError(
                "comparison_set_id must not be blank"
            )

    def _validate_references(
        self,
        request: ExperimentalReviewBundleComparisonSetRequest,
    ) -> None:
        references = request.comparison_references
        if not references:
            raise ExperimentalReviewBundleComparisonSetIdentityError(
                "comparison_references must not be empty"
            )

        identifiers = [reference.bundle_comparison_id for reference in references]
        if len(identifiers) != len(set(identifiers)):
            raise ExperimentalReviewBundleComparisonSetDuplicateError(
                "duplicate bundle_comparison_id"
            )

    def _validate_resources(
        self,
        request: ExperimentalReviewBundleComparisonSetRequest,
    ) -> None:
        settings = self.settings
        if len(request.comparison_references) > settings.max_comparison_count:
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "comparison reference count exceeds configured limit"
            )
        if len(request.warnings) > settings.max_warning_count:
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "warning count exceeds configured limit"
            )
        if len(request.source_refs) > settings.max_source_ref_count:
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "source reference count exceeds configured limit"
            )

        identifiers = [request.comparison_set_id]
        for reference in request.comparison_references:
            identifiers.extend(
                [
                    reference.bundle_comparison_id,
                    reference.left_review_bundle_id,
                    reference.right_review_bundle_id,
                ]
            )
        identifiers.extend(request.source_refs)
        if any(len(value) > settings.max_identifier_length for value in identifiers):
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "identifier exceeds configured length limit"
            )

        try:
            metadata_bytes = len(
                json.dumps(
                    request.metadata,
                    ensure_ascii=False,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
        except (TypeError, ValueError) as exc:
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "metadata is not canonical JSON compatible"
            ) from exc

        if metadata_bytes > settings.max_metadata_bytes:
            raise ExperimentalReviewBundleComparisonSetResourceLimitError(
                "metadata exceeds configured byte limit"
            )
