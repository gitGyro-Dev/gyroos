from __future__ import annotations

import json

from .inspection_comparison_series_comparison import (
    ExperimentalComparisonSeriesComparisonReport,
    ExperimentalComparisonSeriesComparisonRequest,
    ExperimentalComparisonSeriesComparisonResult,
    ExperimentalComparisonSeriesComparisonSettings,
    utc_now,
)


class ExperimentalComparisonSeriesComparisonError(ValueError):
    pass


class ExperimentalComparisonSeriesComparisonIdentityError(
    ExperimentalComparisonSeriesComparisonError
):
    pass


class ExperimentalComparisonSeriesComparisonDuplicateError(
    ExperimentalComparisonSeriesComparisonError
):
    pass


class ExperimentalComparisonSeriesComparisonResourceLimitError(
    ExperimentalComparisonSeriesComparisonError
):
    pass


class ExperimentalComparisonSeriesComparisonService:
    def __init__(
        self,
        settings: ExperimentalComparisonSeriesComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonSeriesComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonSeriesComparisonRequest,
    ) -> ExperimentalComparisonSeriesComparisonResult:
        self._validate_request(request)

        left_ids = request.left_series.set_comparison_ids
        right_ids = request.right_series.set_comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(identifier for identifier in right_ids if identifier not in left_set)
        removed = tuple(identifier for identifier in left_ids if identifier not in right_set)
        retained = tuple(identifier for identifier in left_ids if identifier in right_set)

        left_digest = request.left_series.series_digest
        right_digest = request.right_series.series_digest
        digest_changed = (
            None
            if left_digest is None or right_digest is None
            else left_digest != right_digest
        )

        report = ExperimentalComparisonSeriesComparisonReport(
            series_comparison_id=request.series_comparison_id,
            left_comparison_series_id=request.left_series.comparison_series_id,
            right_comparison_series_id=request.right_series.comparison_series_id,
            added_set_comparison_ids=added,
            removed_set_comparison_ids=removed,
            retained_set_comparison_ids=retained,
            left_series_digest=left_digest,
            right_series_digest=right_digest,
            digest_changed=digest_changed,
            created_at=utc_now(),
            warnings=request.warnings,
            comparison_metadata=request.comparison_metadata,
        )
        return ExperimentalComparisonSeriesComparisonResult(report=report)

    def _validate_request(
        self,
        request: ExperimentalComparisonSeriesComparisonRequest,
    ) -> None:
        if request.left_series.comparison_series_id == request.right_series.comparison_series_id:
            raise ExperimentalComparisonSeriesComparisonIdentityError(
                "left and right comparison series IDs must be distinct"
            )

        self._validate_identifier(request.series_comparison_id, "series_comparison_id")
        self._validate_side(request.left_series, "left_series")
        self._validate_side(request.right_series, "right_series")

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonSeriesComparisonResourceLimitError(
                "warning count exceeds configured limit"
            )

        metadata_bytes = len(
            json.dumps(
                request.comparison_metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonSeriesComparisonResourceLimitError(
                "comparison metadata exceeds configured byte limit"
            )

    def _validate_side(self, reference, side_name: str) -> None:
        self._validate_identifier(reference.comparison_series_id, f"{side_name}.comparison_series_id")

        identifiers = reference.set_comparison_ids
        if len(identifiers) > self.settings.max_reference_count_per_side:
            raise ExperimentalComparisonSeriesComparisonResourceLimitError(
                f"{side_name} reference count exceeds configured limit"
            )
        if len(set(identifiers)) != len(identifiers):
            raise ExperimentalComparisonSeriesComparisonDuplicateError(
                f"{side_name} contains duplicate set-comparison IDs"
            )
        for identifier in identifiers:
            self._validate_identifier(identifier, f"{side_name}.set_comparison_id")

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if len(value.encode("utf-8")) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSeriesComparisonResourceLimitError(
                f"{field_name} exceeds configured identifier length"
            )
