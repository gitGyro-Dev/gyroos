from __future__ import annotations

import json

from .inspection_comparison_ledger_comparison import (
    ExperimentalComparisonLedgerComparisonReport,
    ExperimentalComparisonLedgerComparisonRequest,
    ExperimentalComparisonLedgerComparisonResult,
    ExperimentalComparisonLedgerComparisonSettings,
    ExperimentalComparisonLedgerReference,
)


class ExperimentalComparisonLedgerComparisonError(ValueError):
    pass


class ExperimentalComparisonLedgerComparisonIdentityError(
    ExperimentalComparisonLedgerComparisonError
):
    pass


class ExperimentalComparisonLedgerComparisonDuplicateError(
    ExperimentalComparisonLedgerComparisonError
):
    pass


class ExperimentalComparisonLedgerComparisonResourceLimitError(
    ExperimentalComparisonLedgerComparisonError
):
    pass


class ExperimentalComparisonLedgerComparisonService:
    def __init__(
        self,
        settings: ExperimentalComparisonLedgerComparisonSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonLedgerComparisonSettings()

    def compare(
        self,
        request: ExperimentalComparisonLedgerComparisonRequest,
    ) -> ExperimentalComparisonLedgerComparisonResult:
        self._validate_identifier(request.ledger_comparison_id, "ledger_comparison_id")
        self._validate_reference(request.left, "left")
        self._validate_reference(request.right, "right")

        if request.left.comparison_ledger_id == request.right.comparison_ledger_id:
            raise ExperimentalComparisonLedgerComparisonIdentityError(
                "left and right comparison ledger IDs must be distinct"
            )

        if len(request.warnings) > self.settings.max_warnings:
            raise ExperimentalComparisonLedgerComparisonResourceLimitError(
                "warning count exceeded"
            )

        metadata_bytes = len(
            json.dumps(
                request.metadata,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonLedgerComparisonResourceLimitError(
                "metadata byte limit exceeded"
            )

        left_ids = request.left.register_comparison_ids
        right_ids = request.right.register_comparison_ids
        left_set = set(left_ids)
        right_set = set(right_ids)

        added = tuple(item for item in right_ids if item not in left_set)
        removed = tuple(item for item in left_ids if item not in right_set)
        retained = tuple(item for item in left_ids if item in right_set)

        digest_changed: bool | None
        if request.left.ledger_digest is None or request.right.ledger_digest is None:
            digest_changed = None
        else:
            digest_changed = request.left.ledger_digest != request.right.ledger_digest

        report = ExperimentalComparisonLedgerComparisonReport(
            ledger_comparison_id=request.ledger_comparison_id,
            left_comparison_ledger_id=request.left.comparison_ledger_id,
            right_comparison_ledger_id=request.right.comparison_ledger_id,
            added_register_comparison_ids=added,
            removed_register_comparison_ids=removed,
            retained_register_comparison_ids=retained,
            left_ledger_digest=request.left.ledger_digest,
            right_ledger_digest=request.right.ledger_digest,
            digest_changed=digest_changed,
            created_at=request.created_at,
            warnings=request.warnings,
            metadata=dict(request.metadata),
        )
        return ExperimentalComparisonLedgerComparisonResult(report=report)

    def _validate_reference(
        self,
        reference: ExperimentalComparisonLedgerReference,
        side: str,
    ) -> None:
        self._validate_identifier(reference.comparison_ledger_id, f"{side}.comparison_ledger_id")

        if len(reference.register_comparison_ids) > self.settings.max_references_per_side:
            raise ExperimentalComparisonLedgerComparisonResourceLimitError(
                f"{side} reference count exceeded"
            )

        seen: set[str] = set()
        for register_comparison_id in reference.register_comparison_ids:
            self._validate_identifier(
                register_comparison_id,
                f"{side}.register_comparison_id",
            )
            if register_comparison_id in seen:
                raise ExperimentalComparisonLedgerComparisonDuplicateError(
                    f"duplicate register-comparison reference on {side}: "
                    f"{register_comparison_id}"
                )
            seen.add(register_comparison_id)

    def _validate_identifier(self, value: str, field: str) -> None:
        if not value or len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonLedgerComparisonIdentityError(
                f"invalid {field}"
            )
