from __future__ import annotations

from .builders import (
    ContinuityReadabilityContextBuilder,
    ContinuityRelationBundleBuilder,
    ContinuityRelationRecordBuilder,
)
from .models import (
    ContinuityReadabilityAssemblyRequest,
    ContinuityReadabilityAssemblyResult,
)


class ContinuityReadabilityAssemblyService:
    """Assemble explicit continuity readability records in memory only.

    The service does not calculate continuity, select authority, map an
    OperatorResponse, infer Identity continuity, build a Trajectory, persist
    records, or modify the current Runtime contract.
    """

    def __init__(self) -> None:
        self._context_builder = ContinuityReadabilityContextBuilder()
        self._relation_builder = ContinuityRelationRecordBuilder()
        self._bundle_builder = ContinuityRelationBundleBuilder()

    def assemble(
        self,
        request: ContinuityReadabilityAssemblyRequest,
    ) -> ContinuityReadabilityAssemblyResult:
        context_spec = request.context
        context = self._context_builder.build(
            process_id=request.process_id,
            source_slice_ref=context_spec.source_slice_ref,
            target_slice_ref=context_spec.target_slice_ref,
            orientation_ref=context_spec.orientation_ref,
            context_refs=context_spec.context_refs,
            readability_context_refs=context_spec.readability_context_refs,
            source_record_refs=context_spec.source_record_refs,
            target_record_refs=context_spec.target_record_refs,
            provisional=context_spec.provisional,
            metadata=context_spec.metadata,
            continuity_readability_context_id=(
                context_spec.continuity_readability_context_id
            ),
        )

        relations = []
        relation_ids: set[str] = set()
        for spec in request.relations:
            relation = self._relation_builder.build(
                continuity_context=context,
                source_ref=spec.source_ref,
                target_ref=spec.target_ref,
                relation_type=spec.relation_type,
                readable=spec.readable,
                continuity_state=spec.continuity_state,
                provisional=spec.provisional,
                authoritative=spec.authoritative,
                source_refs=spec.source_refs,
                evidence_refs=spec.evidence_refs,
                metadata=spec.metadata,
                continuity_relation_id=spec.continuity_relation_id,
                expected_context_ref=(
                    context.continuity_readability_context_id
                ),
                expected_process_id=request.process_id,
            )
            if relation.continuity_relation_id in relation_ids:
                raise ValueError(
                    "ContinuityRelationRecord IDs must be unique within one request"
                )
            relation_ids.add(relation.continuity_relation_id)
            relations.append(relation)

        bundle = self._bundle_builder.build(
            continuity_context=context,
            relations=relations,
            metadata=request.bundle_metadata,
            continuity_relation_bundle_id=(
                request.continuity_relation_bundle_id
            ),
        )

        return ContinuityReadabilityAssemblyResult(
            context=context,
            relations=relations,
            bundle=bundle,
        )
