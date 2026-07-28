from __future__ import annotations

import json

from .inspection_comparison_ledger_comparison_archive import (
    ExperimentalComparisonLedgerComparisonArchiveManifest,
    ExperimentalComparisonLedgerComparisonArchiveRequest,
    ExperimentalComparisonLedgerComparisonArchiveResult,
    ExperimentalComparisonLedgerComparisonArchiveSettings,
    compute_comparison_ledger_comparison_archive_digest,
)


class ExperimentalComparisonLedgerComparisonArchiveError(ValueError):
    pass


class ExperimentalComparisonLedgerComparisonArchiveDuplicateError(
    ExperimentalComparisonLedgerComparisonArchiveError
):
    pass


class ExperimentalComparisonLedgerComparisonArchiveResourceLimitError(
    ExperimentalComparisonLedgerComparisonArchiveError
):
    pass


class ExperimentalComparisonLedgerComparisonArchiveService:
    def __init__(
        self,
        settings: ExperimentalComparisonLedgerComparisonArchiveSettings | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonLedgerComparisonArchiveSettings()

    def create_archive(
        self,
        request: ExperimentalComparisonLedgerComparisonArchiveRequest,
    ) -> ExperimentalComparisonLedgerComparisonArchiveResult:
        self._validate_identifier(request.comparison_archive_id, "comparison_archive_id")
        self._validate_references(request)
        self._validate_strings(request.warnings, "warnings", self.settings.max_warnings)
        self._validate_strings(
            request.source_refs,
            "source_refs",
            self.settings.max_source_refs,
        )
        self._validate_metadata(request.metadata)

        digest = compute_comparison_ledger_comparison_archive_digest(
            request.ledger_comparisons,
            request.digest_policy,
        )
        manifest = ExperimentalComparisonLedgerComparisonArchiveManifest(
            comparison_archive_id=request.comparison_archive_id,
            ledger_comparisons=request.ledger_comparisons,
            reference_count=len(request.ledger_comparisons),
            archive_digest=digest,
            digest_policy=request.digest_policy,
            created_at=request.created_at,
            warnings=request.warnings,
            source_refs=request.source_refs,
            metadata=request.metadata,
        )
        return ExperimentalComparisonLedgerComparisonArchiveResult(manifest=manifest)

    def _validate_references(
        self,
        request: ExperimentalComparisonLedgerComparisonArchiveRequest,
    ) -> None:
        if len(request.ledger_comparisons) > self.settings.max_references:
            raise ExperimentalComparisonLedgerComparisonArchiveResourceLimitError(
                "ledger comparison reference count exceeded"
            )

        seen: set[str] = set()
        for reference in request.ledger_comparisons:
            self._validate_identifier(
                reference.ledger_comparison_id,
                "ledger_comparison_id",
            )
            self._validate_identifier(
                reference.left_comparison_ledger_id,
                "left_comparison_ledger_id",
            )
            self._validate_identifier(
                reference.right_comparison_ledger_id,
                "right_comparison_ledger_id",
            )
            if reference.ledger_comparison_id in seen:
                raise ExperimentalComparisonLedgerComparisonArchiveDuplicateError(
                    "duplicate ledger_comparison_id"
                )
            seen.add(reference.ledger_comparison_id)

    def _validate_identifier(self, value: str, label: str) -> None:
        if not value or len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonLedgerComparisonArchiveResourceLimitError(
                f"invalid or oversized {label}"
            )

    def _validate_strings(
        self,
        values: tuple[str, ...],
        label: str,
        maximum: int,
    ) -> None:
        if len(values) > maximum:
            raise ExperimentalComparisonLedgerComparisonArchiveResourceLimitError(
                f"{label} count exceeded"
            )
        for value in values:
            self._validate_identifier(value, label)

    def _validate_metadata(self, metadata: dict[str, object]) -> None:
        encoded = json.dumps(
            metadata,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(encoded) > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonLedgerComparisonArchiveResourceLimitError(
                "metadata byte limit exceeded"
            )
