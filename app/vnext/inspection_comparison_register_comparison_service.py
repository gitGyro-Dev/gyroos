from __future__ import annotations

import json

from .inspection_comparison_register_comparison import (
    ExperimentalComparisonRegisterComparisonReport,
    ExperimentalComparisonRegisterComparisonRequest,
    ExperimentalComparisonRegisterComparisonResult,
    ExperimentalComparisonRegisterComparisonSettings,
    ExperimentalComparisonRegisterReference,
)


class ExperimentalComparisonRegisterComparisonError(ValueError):
    pass


class ExperimentalComparisonRegisterComparisonIdentityError(
    ExperimentalComparisonRegisterComparisonError
):
    pass


class ExperimentalComparisonRegisterComparisonDuplicateError(
    ExperimentalComparisonRegisterComparisonError
):
    pass


class ExperimentalComparisonRegisterComparisonResourceLimitError(
    ExperimentalComparisonRegisterComparisonError
):
    pass


class ExperimentalComparisonRegisterComparisonService:
    def __init__(
        self,
        settings: ExperimentalComparisonRegisterComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonRegisterComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonRegisterComparisonRequest,
    ) -> ExperimentalComparisonRegisterComparisonResult:
        self._validate_identifier(request.register_comparison_id, "register_comparison_id")
        self._validate_distinct_registers(request)
        self._validate_side(request.left_register, "left_register")
        self._validate_side(request.right_register, "right_register")
        self._validate_warnings(request.warnings)
        self._validate_metadata(request.comparison_metadata)

        left_ids = request.left_register.sequence_comparison_ids
        right_ids = request.right_register.sequence_comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_set)
        removed = tuple(item for item in left_ids if item not in right_set)
        retained = tuple(item for item in left_ids if item in right_set)

        left_digest = request.left_register.register_digest
        right_digest = request.right_register.register_digest
        digest_changed = (
            None
            if left_digest is None or right_digest is None
            else left_digest != right_digest
        )

        report = ExperimentalComparisonRegisterComparisonReport(
            register_comparison_id=request.register_comparison_id,
            left_comparison_register_id=request.left_register.comparison_register_id,
            right_comparison_register_id=request.right_register.comparison_register_id,
            added_sequence_comparison_ids=added,
            removed_sequence_comparison_ids=removed,
            retained_sequence_comparison_ids=retained,
            left_register_digest=left_digest,
            right_register_digest=right_digest,
            digest_changed=digest_changed,
            warnings=request.warnings,
            comparison_metadata=dict(request.comparison_metadata),
        )
        return ExperimentalComparisonRegisterComparisonResult(report=report)

    def _validate_distinct_registers(
        self,
        request: ExperimentalComparisonRegisterComparisonRequest,
    ) -> None:
        if (
            request.left_register.comparison_register_id
            == request.right_register.comparison_register_id
        ):
            raise ExperimentalComparisonRegisterComparisonIdentityError(
                "left and right comparison registers must be distinct"
            )

    def _validate_side(
        self,
        reference: ExperimentalComparisonRegisterReference,
        label: str,
    ) -> None:
        self._validate_identifier(reference.comparison_register_id, f"{label}.comparison_register_id")
        ids = reference.sequence_comparison_ids
        if len(ids) > self.settings.max_sequence_comparison_references_per_side:
            raise ExperimentalComparisonRegisterComparisonResourceLimitError(
                f"{label}.sequence_comparison_ids exceeds configured reference limit"
            )
        if len(set(ids)) != len(ids):
            raise ExperimentalComparisonRegisterComparisonDuplicateError(
                f"{label}.sequence_comparison_ids contains duplicates"
            )
        for index, item in enumerate(ids):
            self._validate_identifier(item, f"{label}.sequence_comparison_ids[{index}]")

    def _validate_identifier(self, value: str, label: str) -> None:
        if not value or len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonRegisterComparisonIdentityError(
                f"{label} must be non-empty and within the configured identifier limit"
            )

    def _validate_warnings(self, warnings: tuple[str, ...]) -> None:
        if len(warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonRegisterComparisonResourceLimitError(
                "warnings exceeds configured count limit"
            )
        for index, warning in enumerate(warnings):
            self._validate_identifier(warning, f"warnings[{index}]")

    def _validate_metadata(self, metadata: dict[str, object]) -> None:
        encoded = json.dumps(
            metadata,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if len(encoded) > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonRegisterComparisonResourceLimitError(
                "comparison_metadata exceeds configured byte limit"
            )
