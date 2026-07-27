from __future__ import annotations

import json

from .inspection_comparison_collection_comparison import (
    ExperimentalComparisonCollectionComparisonReport,
    ExperimentalComparisonCollectionComparisonRequest,
    ExperimentalComparisonCollectionComparisonResult,
    ExperimentalComparisonCollectionComparisonSettings,
    utc_now,
)


class ExperimentalComparisonCollectionComparisonError(ValueError):
    pass


class ExperimentalComparisonCollectionComparisonIdentityError(
    ExperimentalComparisonCollectionComparisonError
):
    pass


class ExperimentalComparisonCollectionComparisonDuplicateError(
    ExperimentalComparisonCollectionComparisonError
):
    pass


class ExperimentalComparisonCollectionComparisonResourceLimitError(
    ExperimentalComparisonCollectionComparisonError
):
    pass


class ExperimentalComparisonCollectionComparisonService:
    def __init__(
        self,
        settings: ExperimentalComparisonCollectionComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonCollectionComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonCollectionComparisonRequest,
    ) -> ExperimentalComparisonCollectionComparisonResult:
        self._validate_request(request)

        left_ids = request.left_collection.series_comparison_ids
        right_ids = request.right_collection.series_comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_set)
        removed = tuple(item for item in left_ids if item not in right_set)
        retained = tuple(item for item in left_ids if item in right_set)

        left_digest = request.left_collection.collection_digest
        right_digest = request.right_collection.collection_digest
        digest_changed = (
            None
            if left_digest is None or right_digest is None
            else left_digest != right_digest
        )

        report = ExperimentalComparisonCollectionComparisonReport(
            collection_comparison_id=request.collection_comparison_id,
            left_comparison_collection_id=(
                request.left_collection.comparison_collection_id
            ),
            right_comparison_collection_id=(
                request.right_collection.comparison_collection_id
            ),
            added_series_comparison_ids=added,
            removed_series_comparison_ids=removed,
            retained_series_comparison_ids=retained,
            left_collection_digest=left_digest,
            right_collection_digest=right_digest,
            digest_changed=digest_changed,
            created_at=request.created_at or utc_now(),
            warnings=request.warnings,
            comparison_metadata=request.comparison_metadata,
        )
        return ExperimentalComparisonCollectionComparisonResult(report=report)

    def _validate_request(
        self,
        request: ExperimentalComparisonCollectionComparisonRequest,
    ) -> None:
        self._validate_identifier(
            request.collection_comparison_id,
            "collection_comparison_id",
        )

        left = request.left_collection
        right = request.right_collection
        self._validate_identifier(
            left.comparison_collection_id,
            "left comparison_collection_id",
        )
        self._validate_identifier(
            right.comparison_collection_id,
            "right comparison_collection_id",
        )

        if left.comparison_collection_id == right.comparison_collection_id:
            raise ExperimentalComparisonCollectionComparisonIdentityError(
                "left and right comparison_collection_id must be distinct"
            )

        self._validate_side(left.series_comparison_ids, "left")
        self._validate_side(right.series_comparison_ids, "right")

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonCollectionComparisonResourceLimitError(
                "warning count exceeds configured maximum"
            )
        for warning in request.warnings:
            self._validate_identifier(warning, "warning")

        metadata_bytes = len(
            json.dumps(
                request.comparison_metadata,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonCollectionComparisonResourceLimitError(
                "comparison metadata exceeds configured byte maximum"
            )

    def _validate_side(self, values: tuple[str, ...], side: str) -> None:
        if len(values) > self.settings.max_reference_count:
            raise ExperimentalComparisonCollectionComparisonResourceLimitError(
                f"{side} reference count exceeds configured maximum"
            )

        seen: set[str] = set()
        for value in values:
            self._validate_identifier(value, f"{side} series_comparison_id")
            if value in seen:
                raise ExperimentalComparisonCollectionComparisonDuplicateError(
                    f"duplicate {side} series_comparison_id: {value}"
                )
            seen.add(value)

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if not value.strip():
            raise ExperimentalComparisonCollectionComparisonIdentityError(
                f"{field_name} must not be blank"
            )
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonCollectionComparisonResourceLimitError(
                f"{field_name} exceeds configured maximum length"
            )
