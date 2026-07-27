from __future__ import annotations

import json

from .inspection_comparison_sequence_comparison_register import (
    ExperimentalComparisonSequenceComparisonRegisterManifest,
    ExperimentalComparisonSequenceComparisonRegisterRequest,
    ExperimentalComparisonSequenceComparisonRegisterResult,
    ExperimentalComparisonSequenceComparisonRegisterSettings,
    digest_comparison_references,
    utc_now,
)


class ExperimentalComparisonSequenceComparisonRegisterError(ValueError):
    pass


class ExperimentalComparisonSequenceComparisonRegisterIdentityError(
    ExperimentalComparisonSequenceComparisonRegisterError
):
    pass


class ExperimentalComparisonSequenceComparisonRegisterDuplicateError(
    ExperimentalComparisonSequenceComparisonRegisterError
):
    pass


class ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
    ExperimentalComparisonSequenceComparisonRegisterError
):
    pass


class ExperimentalComparisonSequenceComparisonRegisterService:
    def __init__(
        self,
        settings: ExperimentalComparisonSequenceComparisonRegisterSettings | None = None,
    ) -> None:
        self.settings = (
            settings or ExperimentalComparisonSequenceComparisonRegisterSettings()
        )

    def create_register(
        self,
        request: ExperimentalComparisonSequenceComparisonRegisterRequest,
    ) -> ExperimentalComparisonSequenceComparisonRegisterResult:
        self._validate_request(request)

        try:
            references_digest = digest_comparison_references(
                request.comparison_references,
                request.digest_policy,
            )
        except ValueError as exc:
            raise ExperimentalComparisonSequenceComparisonRegisterError(str(exc)) from exc

        manifest = ExperimentalComparisonSequenceComparisonRegisterManifest(
            comparison_register_id=request.comparison_register_id,
            comparison_references=request.comparison_references,
            comparison_count=len(request.comparison_references),
            comparison_references_digest=references_digest,
            digest_policy=request.digest_policy,
            created_at=request.created_at or utc_now(),
            warnings=request.warnings,
            source_refs=request.source_refs,
            register_metadata=request.register_metadata,
        )
        return ExperimentalComparisonSequenceComparisonRegisterResult(manifest=manifest)

    def _validate_request(
        self,
        request: ExperimentalComparisonSequenceComparisonRegisterRequest,
    ) -> None:
        self._validate_identifier(
            request.comparison_register_id,
            "comparison_register_id",
        )

        if len(request.comparison_references) > self.settings.max_comparison_count:
            raise ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
                "comparison reference count exceeds configured maximum"
            )

        seen_ids: set[str] = set()
        for reference in request.comparison_references:
            self._validate_identifier(
                reference.sequence_comparison_id,
                "sequence_comparison_id",
            )
            self._validate_identifier(
                reference.left_comparison_sequence_id,
                "left_comparison_sequence_id",
            )
            self._validate_identifier(
                reference.right_comparison_sequence_id,
                "right_comparison_sequence_id",
            )
            if reference.sequence_comparison_id in seen_ids:
                raise ExperimentalComparisonSequenceComparisonRegisterDuplicateError(
                    "duplicate sequence_comparison_id: "
                    f"{reference.sequence_comparison_id}"
                )
            seen_ids.add(reference.sequence_comparison_id)

        if len(request.warnings) > self.settings.max_warning_count:
            raise ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
                "warning count exceeds configured maximum"
            )
        if len(request.source_refs) > self.settings.max_source_ref_count:
            raise ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
                "source reference count exceeds configured maximum"
            )

        for warning in request.warnings:
            self._validate_identifier(warning, "warning")
        for source_ref in request.source_refs:
            self._validate_identifier(source_ref, "source_ref")

        metadata_bytes = len(
            json.dumps(
                request.register_metadata,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        if metadata_bytes > self.settings.max_metadata_bytes:
            raise ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
                "register metadata exceeds configured byte maximum"
            )

    def _validate_identifier(self, value: str, field_name: str) -> None:
        if not value.strip():
            raise ExperimentalComparisonSequenceComparisonRegisterIdentityError(
                f"{field_name} must not be blank"
            )
        if len(value) > self.settings.max_identifier_length:
            raise ExperimentalComparisonSequenceComparisonRegisterResourceLimitError(
                f"{field_name} exceeds configured maximum length"
            )
