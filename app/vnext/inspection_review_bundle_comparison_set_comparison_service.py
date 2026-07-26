from __future__ import annotations

import json

from .inspection_review_bundle_comparison_set_comparison import (
    ExperimentalComparisonSetComparisonReport,
    ExperimentalComparisonSetComparisonRequest,
    ExperimentalComparisonSetComparisonResult,
    ExperimentalComparisonSetComparisonSettings,
    ExperimentalComparisonSetReference,
    utc_now,
)


class ExperimentalComparisonSetComparisonError(ValueError):
    pass


class ExperimentalComparisonSetComparisonIdentityError(
    ExperimentalComparisonSetComparisonError
):
    pass


class ExperimentalComparisonSetComparisonDuplicateError(
    ExperimentalComparisonSetComparisonError
):
    pass


class ExperimentalComparisonSetComparisonResourceLimitError(
    ExperimentalComparisonSetComparisonError
):
    pass


class ExperimentalComparisonSetComparisonService:
    def __init__(
        self,
        *,
        settings: ExperimentalComparisonSetComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonSetComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonSetComparisonRequest,
    ) -> ExperimentalComparisonSetComparisonResult:
        self._validate_identifier(request.set_comparison_id, "set_comparison_id")
        self._validate_side(request.left_set, "left_set")
        self._validate_side(request.right_set, "right_set")

        if request.left_set.comparison_set_id == request.right_set.comparison_set_id:
            raise ExperimentalComparisonSetComparisonIdentityError(
                "left and right comparison_set_id must be distinct"
            )

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonSetComparisonResourceLimitError(
                "warning count exceeds configured limit"
            )

        metadata_bytes = len(
            json.dumps(
                request.comparison_metadata,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonSetComparisonResourceLimitError(
                "comparison metadata exceeds configured byte limit"
            )

        left_ids = request.left_set.bundle_comparison_ids
        right_ids = request.right_set.bundle_comparison_ids
        left_members = set(left_ids)
        right_members = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_members)
        removed = tuple(item for item in left_ids if item not in right_members)
        retained = tuple(item for item in left_ids if item in right_members)

        digest_changed: bool | None
        if request.left_set.set_digest is None or request.right_set.set_digest is None:
            digest_changed = None
        else:
            digest_changed = request.left_set.set_digest != request.right_set.set_digest

        report = ExperimentalComparisonSetComparisonReport(
            set_comparison_id=request.set_comparison_id,
            left_comparison_set_id=request.left_set.comparison_set_id,
            right_comparison_set_id=request.right_set.comparison_set_id,
            added_bundle_comparison_ids=added,
            removed_bundle_comparison_ids=removed,
            retained_bundle_comparison_ids=retained,
            left_set_digest=request.left_set.set_digest,
            right_set_digest=request.right_set.set_digest,
            digest_changed=digest_changed,
            created_at=utc_now(),
            warnings=request.warnings,
            comparison_metadata=dict(request.comparison_metadata),
        )
        return ExperimentalComparisonSetComparisonResult(
            comparison_report_created=True,
            report=report,
        )

    def _validate_side(
        self,
        reference: ExperimentalComparisonSetReference,
        side_name: str,
    ) -> None:
        self._validate_identifier(reference.comparison_set_id, f"{side_name}.comparison_set_id")

        if len(reference.bundle_comparison_ids) > self.settings.max_bundle_comparison_count_per_side:
            raise ExperimentalComparisonSetComparisonResourceLimitError(
                f"{side_name} bundle comparison count exceeds configured limit"
            )

        seen: set[str] = set()
        for bundle_comparison_id in reference.bundle_comparison_ids:
            self._validate_identifier(
                bundle_comparison_id,
                f"{side_name}.bundle_comparison_id",
            )
            if bundle_comparison_id in seen:
                raise ExperimentalComparisonSetComparisonDuplicateError(
                    f"duplicate bundle comparison reference on {side_name}: {bundle_comparison_id}"
                )
            seen.add(bundle_comparison_id)

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if not value:
            raise ExperimentalComparisonSetComparisonIdentityError(
                f"{field_name} must not be empty"
            )
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSetComparisonResourceLimitError(
                f"{field_name} exceeds configured length limit"
            )
