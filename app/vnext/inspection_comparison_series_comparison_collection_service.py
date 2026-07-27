from __future__ import annotations

import json

from .inspection_comparison_series_comparison_collection import (
    ExperimentalComparisonSeriesComparisonCollectionManifest,
    ExperimentalComparisonSeriesComparisonCollectionRequest,
    ExperimentalComparisonSeriesComparisonCollectionResult,
    ExperimentalComparisonSeriesComparisonCollectionSettings,
    digest_comparison_references,
    utc_now,
)


class ExperimentalComparisonSeriesComparisonCollectionError(ValueError):
    pass


class ExperimentalComparisonSeriesComparisonCollectionIdentityError(
    ExperimentalComparisonSeriesComparisonCollectionError
):
    pass


class ExperimentalComparisonSeriesComparisonCollectionDuplicateError(
    ExperimentalComparisonSeriesComparisonCollectionError
):
    pass


class ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
    ExperimentalComparisonSeriesComparisonCollectionError
):
    pass


class ExperimentalComparisonSeriesComparisonCollectionService:
    def __init__(
        self,
        settings: ExperimentalComparisonSeriesComparisonCollectionSettings | None = None,
    ) -> None:
        self.settings = (
            settings or ExperimentalComparisonSeriesComparisonCollectionSettings()
        )

    def create_collection(
        self,
        request: ExperimentalComparisonSeriesComparisonCollectionRequest,
    ) -> ExperimentalComparisonSeriesComparisonCollectionResult:
        self._validate_request(request)

        try:
            references_digest = digest_comparison_references(
                request.comparison_references,
                request.digest_policy,
            )
        except ValueError as exc:
            raise ExperimentalComparisonSeriesComparisonCollectionError(str(exc)) from exc

        manifest = ExperimentalComparisonSeriesComparisonCollectionManifest(
            comparison_collection_id=request.comparison_collection_id,
            comparison_references=request.comparison_references,
            comparison_count=len(request.comparison_references),
            comparison_references_digest=references_digest,
            digest_policy=request.digest_policy,
            created_at=request.created_at or utc_now(),
            warnings=request.warnings,
            source_refs=request.source_refs,
            collection_metadata=request.collection_metadata,
        )
        return ExperimentalComparisonSeriesComparisonCollectionResult(manifest=manifest)

    def _validate_request(
        self,
        request: ExperimentalComparisonSeriesComparisonCollectionRequest,
    ) -> None:
        self._validate_identifier(
            request.comparison_collection_id,
            "comparison_collection_id",
        )

        if len(request.comparison_references) > self.settings.max_comparison_count:
            raise ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
                "comparison reference count exceeds configured maximum"
            )

        seen_ids: set[str] = set()
        for reference in request.comparison_references:
            self._validate_identifier(
                reference.series_comparison_id,
                "series_comparison_id",
            )
            self._validate_identifier(
                reference.left_comparison_series_id,
                "left_comparison_series_id",
            )
            self._validate_identifier(
                reference.right_comparison_series_id,
                "right_comparison_series_id",
            )
            if reference.series_comparison_id in seen_ids:
                raise ExperimentalComparisonSeriesComparisonCollectionDuplicateError(
                    "duplicate series_comparison_id: "
                    f"{reference.series_comparison_id}"
                )
            seen_ids.add(reference.series_comparison_id)

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
                "warning count exceeds configured maximum"
            )
        if len(request.source_refs) > self.settings.max_source_ref_count:
            raise ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
                "source reference count exceeds configured maximum"
            )

        for warning in request.warnings:
            self._validate_identifier(warning, "warning")
        for source_ref in request.source_refs:
            self._validate_identifier(source_ref, "source_ref")

        metadata_bytes = len(
            json.dumps(
                request.collection_metadata,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
                "collection metadata exceeds configured byte maximum"
            )

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if not value.strip():
            raise ExperimentalComparisonSeriesComparisonCollectionIdentityError(
                f"{field_name} must not be blank"
            )
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSeriesComparisonCollectionResourceLimitError(
                f"{field_name} exceeds configured maximum length"
            )
