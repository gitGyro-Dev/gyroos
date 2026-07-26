from __future__ import annotations

from .builders import (
    ReadOnlyRuntimeProjectionBuilder,
    RuntimeProjectionReferenceBuilder,
    RuntimeSnapshotBuilder,
)
from .models import (
    ReadOnlyRuntimeProjectionRequest,
    ReadOnlyRuntimeProjectionResult,
)


class ReadOnlyRuntimeProjectionService:
    """Assemble one immutable projection from an existing Runtime result snapshot.

    The service does not execute Runtime, parse the opaque payload, resolve vNext
    record references, persist records, or influence OperatorResponse.
    """

    def __init__(self) -> None:
        self._snapshot_builder = RuntimeSnapshotBuilder()
        self._reference_builder = RuntimeProjectionReferenceBuilder()
        self._projection_builder = ReadOnlyRuntimeProjectionBuilder()

    def project(
        self,
        request: ReadOnlyRuntimeProjectionRequest,
    ) -> ReadOnlyRuntimeProjectionResult:
        snapshot = self._snapshot_builder.build(
            process_id=request.process_id,
            slice_ref=request.snapshot.slice_ref,
            runtime_contract=request.snapshot.runtime_contract,
            payload=request.snapshot.payload,
            metadata=request.snapshot.metadata,
            runtime_snapshot_id=request.snapshot.runtime_snapshot_id,
        )

        references = []
        reference_ids: set[str] = set()
        for spec in request.references:
            reference = self._reference_builder.build(
                snapshot=snapshot,
                record_ref=spec.record_ref,
                record_type=spec.record_type,
                relation_type=spec.relation_type,
                provisional=spec.provisional,
                evidence_refs=spec.evidence_refs,
                metadata=spec.metadata,
                projection_reference_id=spec.projection_reference_id,
                expected_snapshot_ref=snapshot.runtime_snapshot_id,
                expected_process_id=request.process_id,
            )
            if reference.projection_reference_id in reference_ids:
                raise ValueError(
                    "RuntimeProjectionReference IDs must be unique within one request"
                )
            reference_ids.add(reference.projection_reference_id)
            references.append(reference)

        projection = self._projection_builder.build(
            snapshot=snapshot,
            references=references,
            provisional=request.provisional,
            metadata=request.projection_metadata,
            runtime_projection_id=request.runtime_projection_id,
        )

        return ReadOnlyRuntimeProjectionResult(
            snapshot=snapshot,
            references=references,
            projection=projection,
        )
