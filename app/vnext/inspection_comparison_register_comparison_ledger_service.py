from __future__ import annotations

from .inspection_comparison_register_comparison_ledger import (
    ExperimentalComparisonRegisterComparisonLedgerDigestPolicy,
    ExperimentalComparisonRegisterComparisonLedgerManifest,
    ExperimentalComparisonRegisterComparisonLedgerRequest,
    ExperimentalComparisonRegisterComparisonLedgerResult,
    ExperimentalComparisonRegisterComparisonLedgerSettings,
    ExperimentalComparisonRegisterComparisonReference,
    utc_now,
)
from .inspection_validation import canonical_json_utf8_size


class ExperimentalComparisonRegisterComparisonLedgerError(ValueError):
    pass


class ExperimentalComparisonRegisterComparisonLedgerDuplicateError(
    ExperimentalComparisonRegisterComparisonLedgerError
):
    pass


class ExperimentalComparisonRegisterComparisonLedgerResourceLimitError(
    ExperimentalComparisonRegisterComparisonLedgerError
):
    pass


class ExperimentalComparisonRegisterComparisonLedgerService:
    def __init__(
        self,
        settings: ExperimentalComparisonRegisterComparisonLedgerSettings | None = None,
        digest_policy: ExperimentalComparisonRegisterComparisonLedgerDigestPolicy | None = None,
    ) -> None:
        self.settings = settings or ExperimentalComparisonRegisterComparisonLedgerSettings()
        self.digest_policy = (
            digest_policy or ExperimentalComparisonRegisterComparisonLedgerDigestPolicy()
        )

    def create_ledger(
        self,
        request: ExperimentalComparisonRegisterComparisonLedgerRequest,
    ) -> ExperimentalComparisonRegisterComparisonLedgerResult:
        self._validate_identifier(request.comparison_ledger_id, "comparison_ledger_id")
        self._validate_reference_count(request.comparison_references)
        self._validate_unique_references(request.comparison_references)

        for reference in request.comparison_references:
            self._validate_reference(reference)

        self._validate_text_values(request.warnings, "warnings", self.settings.max_warning_count)
        self._validate_text_values(
            request.source_refs,
            "source_refs",
            self.settings.max_source_ref_count,
        )
        self._validate_metadata(request.ledger_metadata)

        references = tuple(request.comparison_references)
        manifest = ExperimentalComparisonRegisterComparisonLedgerManifest(
            comparison_ledger_id=request.comparison_ledger_id,
            comparison_references=references,
            comparison_count=len(references),
            digest_algorithm=self.digest_policy.algorithm,
            digest_canonicalization=self.digest_policy.canonicalization,
            ledger_digest=self.digest_policy.digest(references),
            created_at=utc_now(),
            warnings=tuple(request.warnings),
            source_refs=tuple(request.source_refs),
            ledger_metadata=dict(request.ledger_metadata),
        )
        return ExperimentalComparisonRegisterComparisonLedgerResult(manifest=manifest)

    def _validate_reference_count(
        self,
        references: tuple[ExperimentalComparisonRegisterComparisonReference, ...],
    ) -> None:
        if len(references) > self.settings.max_comparison_references:
            raise ExperimentalComparisonRegisterComparisonLedgerResourceLimitError(
                "comparison reference count exceeds configured maximum"
            )

    def _validate_unique_references(
        self,
        references: tuple[ExperimentalComparisonRegisterComparisonReference, ...],
    ) -> None:
        identifiers = [reference.register_comparison_id for reference in references]
        if len(identifiers) != len(set(identifiers)):
            raise ExperimentalComparisonRegisterComparisonLedgerDuplicateError(
                "duplicate register_comparison_id is not allowed"
            )

    def _validate_reference(
        self,
        reference: ExperimentalComparisonRegisterComparisonReference,
    ) -> None:
        self._validate_identifier(reference.register_comparison_id, "register_comparison_id")
        self._validate_identifier(
            reference.left_comparison_register_id,
            "left_comparison_register_id",
        )
        self._validate_identifier(
            reference.right_comparison_register_id,
            "right_comparison_register_id",
        )

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if len(value.encode("utf-8")) > self.settings.max_identifier_length:
            raise ExperimentalComparisonRegisterComparisonLedgerResourceLimitError(
                f"{field_name} exceeds configured identifier limit"
            )

    def _validate_text_values(
        self,
        values: tuple[str, ...],
        field_name: str,
        maximum_count: int,
    ) -> None:
        if len(values) > maximum_count:
            raise ExperimentalComparisonRegisterComparisonLedgerResourceLimitError(
                f"{field_name} count exceeds configured maximum"
            )
        for value in values:
            self._validate_identifier(value, field_name)

    def _validate_metadata(self, metadata: dict[str, object]) -> None:
        if canonical_json_utf8_size(metadata) > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonRegisterComparisonLedgerResourceLimitError(
                "ledger_metadata exceeds configured byte limit"
            )
