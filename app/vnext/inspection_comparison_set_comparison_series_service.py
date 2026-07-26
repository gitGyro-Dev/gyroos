from __future__ import annotations

import json

from .inspection_comparison_set_comparison_series import (
    ExperimentalComparisonSetComparisonSeriesDigestPolicy,
    ExperimentalComparisonSetComparisonSeriesManifest,
    ExperimentalComparisonSetComparisonSeriesRequest,
    ExperimentalComparisonSetComparisonSeriesResult,
    ExperimentalComparisonSetComparisonSeriesSettings,
    compute_series_digest,
    utc_now,
)


class ExperimentalComparisonSetComparisonSeriesError(ValueError):
    pass


class ExperimentalComparisonSetComparisonSeriesIdentityError(
    ExperimentalComparisonSetComparisonSeriesError
):
    pass


class ExperimentalComparisonSetComparisonSeriesDuplicateError(
    ExperimentalComparisonSetComparisonSeriesError
):
    pass


class ExperimentalComparisonSetComparisonSeriesResourceLimitError(
    ExperimentalComparisonSetComparisonSeriesError
):
    pass


class ExperimentalComparisonSetComparisonSeriesService:
    def __init__(
        self,
        settings: ExperimentalComparisonSetComparisonSeriesSettings | None = None,
        digest_policy: ExperimentalComparisonSetComparisonSeriesDigestPolicy | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonSetComparisonSeriesSettings()
        self.digest_policy = (
            digest_policy or ExperimentalComparisonSetComparisonSeriesDigestPolicy()
        )

    def create_series(
        self,
        request: ExperimentalComparisonSetComparisonSeriesRequest,
    ) -> ExperimentalComparisonSetComparisonSeriesResult:
        self._validate_request(request)

        references = request.set_comparison_references
        manifest = ExperimentalComparisonSetComparisonSeriesManifest(
            comparison_series_id=request.comparison_series_id,
            set_comparison_references=references,
            reference_count=len(references),
            series_digest=compute_series_digest(references),
            digest_policy=self.digest_policy,
            created_at=utc_now(),
            warnings=request.warnings,
            source_refs=request.source_refs,
            series_metadata=request.series_metadata,
        )
        return ExperimentalComparisonSetComparisonSeriesResult(manifest=manifest)

    def _validate_request(
        self,
        request: ExperimentalComparisonSetComparisonSeriesRequest,
    ) -> None:
        if not request.set_comparison_references:
            raise ExperimentalComparisonSetComparisonSeriesIdentityError(
                "set_comparison_references must not be empty"
            )

        self._validate_identifier(request.comparison_series_id, "comparison_series_id")

        if len(request.set_comparison_references) > self.settings.max_references:
            raise ExperimentalComparisonSetComparisonSeriesResourceLimitError(
                "set-comparison reference count exceeded"
            )

        seen_ids: set[str] = set()
        for reference in request.set_comparison_references:
            self._validate_identifier(
                reference.set_comparison_id,
                "set_comparison_id",
            )
            self._validate_identifier(
                reference.left_comparison_set_id,
                "left_comparison_set_id",
            )
            self._validate_identifier(
                reference.right_comparison_set_id,
                "right_comparison_set_id",
            )
            if reference.set_comparison_id in seen_ids:
                raise ExperimentalComparisonSetComparisonSeriesDuplicateError(
                    f"duplicate set_comparison_id: {reference.set_comparison_id}"
                )
            seen_ids.add(reference.set_comparison_id)

        if len(request.warnings) > self.settings.max_warnings:
            raise ExperimentalComparisonSetComparisonSeriesResourceLimitError(
                "warning count exceeded"
            )
        if len(request.source_refs) > self.settings.max_source_refs:
            raise ExperimentalComparisonSetComparisonSeriesResourceLimitError(
                "source reference count exceeded"
            )

        metadata_size = len(
            json.dumps(
                request.series_metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if metadata_size > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonSetComparisonSeriesResourceLimitError(
                "series metadata byte limit exceeded"
            )

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSetComparisonSeriesResourceLimitError(
                f"{field_name} length exceeded"
            )
