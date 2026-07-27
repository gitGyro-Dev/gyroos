from __future__ import annotations

import json

from .inspection_comparison_sequence_comparison import (
    ExperimentalComparisonSequenceComparisonReport,
    ExperimentalComparisonSequenceComparisonRequest,
    ExperimentalComparisonSequenceComparisonResult,
    ExperimentalComparisonSequenceComparisonSettings,
    utc_now,
)


class ExperimentalComparisonSequenceComparisonError(ValueError):
    pass


class ExperimentalComparisonSequenceComparisonIdentityError(
    ExperimentalComparisonSequenceComparisonError
):
    pass


class ExperimentalComparisonSequenceComparisonDuplicateError(
    ExperimentalComparisonSequenceComparisonError
):
    pass


class ExperimentalComparisonSequenceComparisonResourceLimitError(
    ExperimentalComparisonSequenceComparisonError
):
    pass


class ExperimentalComparisonSequenceComparisonService:
    def __init__(
        self,
        settings: ExperimentalComparisonSequenceComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonSequenceComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonSequenceComparisonRequest,
    ) -> ExperimentalComparisonSequenceComparisonResult:
        self._validate_request(request)

        left_ids = request.left_sequence.collection_comparison_ids
        right_ids = request.right_sequence.collection_comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_set)
        removed = tuple(item for item in left_ids if item not in right_set)
        retained = tuple(item for item in left_ids if item in right_set)

        left_digest = request.left_sequence.sequence_digest
        right_digest = request.right_sequence.sequence_digest
        digest_changed = (
            None
            if left_digest is None or right_digest is None
            else left_digest != right_digest
        )

        report = ExperimentalComparisonSequenceComparisonReport(
            sequence_comparison_id=request.sequence_comparison_id,
            left_comparison_sequence_id=request.left_sequence.comparison_sequence_id,
            right_comparison_sequence_id=request.right_sequence.comparison_sequence_id,
            added_collection_comparison_ids=added,
            removed_collection_comparison_ids=removed,
            retained_collection_comparison_ids=retained,
            left_sequence_digest=left_digest,
            right_sequence_digest=right_digest,
            digest_changed=digest_changed,
            created_at=request.created_at or utc_now(),
            warnings=request.warnings,
            comparison_metadata=request.comparison_metadata,
        )
        return ExperimentalComparisonSequenceComparisonResult(report=report)

    def _validate_request(
        self,
        request: ExperimentalComparisonSequenceComparisonRequest,
    ) -> None:
        self._validate_identifier(request.sequence_comparison_id, "sequence_comparison_id")
        self._validate_identifier(
            request.left_sequence.comparison_sequence_id,
            "left comparison_sequence_id",
        )
        self._validate_identifier(
            request.right_sequence.comparison_sequence_id,
            "right comparison_sequence_id",
        )

        if (
            request.left_sequence.comparison_sequence_id
            == request.right_sequence.comparison_sequence_id
        ):
            raise ExperimentalComparisonSequenceComparisonIdentityError(
                "left and right comparison sequence IDs must be distinct"
            )

        self._validate_side(
            request.left_sequence.collection_comparison_ids,
            "left collection_comparison_ids",
        )
        self._validate_side(
            request.right_sequence.collection_comparison_ids,
            "right collection_comparison_ids",
        )

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonSequenceComparisonResourceLimitError(
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
            raise ExperimentalComparisonSequenceComparisonResourceLimitError(
                "comparison metadata exceeds configured byte maximum"
            )

    def _validate_side(self, values: tuple[str, ...], field_name: str) -> None:
        if len(values) > self.settings.max_reference_count:
            raise ExperimentalComparisonSequenceComparisonResourceLimitError(
                f"{field_name} exceeds configured maximum"
            )

        seen: set[str] = set()
        for value in values:
            self._validate_identifier(value, field_name)
            if value in seen:
                raise ExperimentalComparisonSequenceComparisonDuplicateError(
                    f"duplicate collection-comparison reference in {field_name}: {value}"
                )
            seen.add(value)

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if not value.strip():
            raise ExperimentalComparisonSequenceComparisonIdentityError(
                f"{field_name} must not be blank"
            )
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSequenceComparisonResourceLimitError(
                f"{field_name} exceeds configured maximum length"
            )
