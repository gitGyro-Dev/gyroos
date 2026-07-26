from __future__ import annotations

import json

from .inspection_comparison_review_bundle import (
    ExperimentalComparisonReviewBundle,
    ExperimentalComparisonReviewBundleDigestPolicy,
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleResult,
    ExperimentalComparisonReviewBundleSettings,
    experimental_comparison_review_bundle_settings,
    utc_now,
)


class ExperimentalComparisonReviewBundleError(ValueError):
    pass


class ExperimentalComparisonReviewBundleIdentityError(ExperimentalComparisonReviewBundleError):
    pass


class ExperimentalComparisonReviewBundleDuplicateError(ExperimentalComparisonReviewBundleError):
    pass


class ExperimentalComparisonReviewBundleResourceLimitError(ExperimentalComparisonReviewBundleError):
    pass


class ExperimentalComparisonReviewBundleService:
    def __init__(
        self,
        *,
        settings: ExperimentalComparisonReviewBundleSettings = experimental_comparison_review_bundle_settings,
        digest_policy: ExperimentalComparisonReviewBundleDigestPolicy | None = None,
    ) -> None:
        self.settings = settings
        self.digest_policy = digest_policy or ExperimentalComparisonReviewBundleDigestPolicy()

    def create_bundle(
        self,
        request: ExperimentalComparisonReviewBundleRequest,
    ) -> ExperimentalComparisonReviewBundleResult:
        self._validate_request(request)

        serialized_references = [
            reference.model_dump(mode="json")
            for reference in request.comparison_references
        ]
        digest = self.digest_policy.digest(serialized_references)

        bundle = ExperimentalComparisonReviewBundle(
            review_bundle_id=request.review_bundle_id,
            comparison_references=request.comparison_references,
            ordered_reference_digest=digest,
            digest_algorithm=self.digest_policy.algorithm,
            canonicalization=self.digest_policy.canonicalization,
            created_at=utc_now(),
            warnings=request.warnings,
            source_refs=request.source_refs,
            metadata=dict(request.metadata),
        )
        return ExperimentalComparisonReviewBundleResult(
            review_bundle_created=True,
            bundle=bundle,
        )

    def _validate_request(
        self,
        request: ExperimentalComparisonReviewBundleRequest,
    ) -> None:
        if not request.comparison_references:
            raise ExperimentalComparisonReviewBundleIdentityError(
                "comparison_references must not be empty"
            )
        if len(request.comparison_references) > self.settings.max_comparison_count:
            raise ExperimentalComparisonReviewBundleResourceLimitError(
                "comparison reference count exceeded"
            )

        comparison_ids = [
            reference.comparison_id for reference in request.comparison_references
        ]
        if len(comparison_ids) != len(set(comparison_ids)):
            raise ExperimentalComparisonReviewBundleDuplicateError(
                "duplicate comparison reference"
            )

        identifiers = [request.review_bundle_id]
        for reference in request.comparison_references:
            identifiers.extend(
                (
                    reference.comparison_id,
                    reference.left_manifest_id,
                    reference.right_manifest_id,
                )
            )
        if any(len(identifier) > self.settings.max_identifier_length for identifier in identifiers):
            raise ExperimentalComparisonReviewBundleResourceLimitError(
                "identifier length exceeded"
            )

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonReviewBundleResourceLimitError(
                "warning count exceeded"
            )
        if len(request.source_refs) > self.settings.max_source_ref_count:
            raise ExperimentalComparisonReviewBundleResourceLimitError(
                "source reference count exceeded"
            )

        metadata_bytes = len(
            json.dumps(
                request.metadata,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonReviewBundleResourceLimitError(
                "metadata byte limit exceeded"
            )
