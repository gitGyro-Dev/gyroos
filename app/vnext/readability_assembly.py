from __future__ import annotations

from .builders import (
    IncorporationRecordBuilder,
    ReadabilityContextBuilder,
    ReadabilityRelationBundleBuilder,
    SceneReadabilityRelationBuilder,
)
from .models import (
    IncorporatedReadabilityAssemblyRequest,
    IncorporatedReadabilityAssemblyResult,
    ReadabilityContext,
)


class IncorporatedReadabilityAssemblyService:
    """Assemble explicit Incorporated Readability records in memory only.

    The service coordinates existing pure builders. It does not select a current
    context, infer authority, execute context updates, merge contexts, persist
    records, or modify the supplied StabilityScene.
    """

    def __init__(self) -> None:
        self._context_builder = ReadabilityContextBuilder()
        self._incorporation_builder = IncorporationRecordBuilder()
        self._scene_relation_builder = SceneReadabilityRelationBuilder()
        self._bundle_builder = ReadabilityRelationBundleBuilder()

    def assemble(
        self,
        request: IncorporatedReadabilityAssemblyRequest,
    ) -> IncorporatedReadabilityAssemblyResult:
        if request.scene.process_id != request.process_id:
            raise ValueError(
                "request process_id must match StabilityScene process_id"
            )
        if request.scene.slice_ref != request.slice_ref:
            raise ValueError(
                "request slice_ref must match StabilityScene slice_ref"
            )

        contexts: list[ReadabilityContext] = []
        context_by_id: dict[str, ReadabilityContext] = {}

        for spec in request.contexts:
            context = self._context_builder.build(
                process_id=request.process_id,
                slice_ref=request.slice_ref,
                readable_item_refs=spec.readable_item_refs,
                unresolved_item_refs=spec.unresolved_item_refs,
                excluded_item_refs=spec.excluded_item_refs,
                source_context_refs=spec.source_context_refs,
                provisional=spec.provisional,
                metadata=spec.metadata,
                readability_context_id=spec.readability_context_id,
            )
            if context.readability_context_id in context_by_id:
                raise ValueError(
                    "ReadabilityContext IDs must be unique within one request"
                )
            contexts.append(context)
            context_by_id[context.readability_context_id] = context

        incorporations = []
        for spec in request.incorporations:
            before_context = self._require_context(
                context_by_id,
                spec.before_context_ref,
                "before_context_ref",
            )
            after_context = self._require_context(
                context_by_id,
                spec.after_context_ref,
                "after_context_ref",
            )
            incorporations.append(
                self._incorporation_builder.build(
                    before_context=before_context,
                    after_context=after_context,
                    incorporated_item_refs=spec.incorporated_item_refs,
                    rejected_item_refs=spec.rejected_item_refs,
                    update_reason=spec.update_reason,
                    provisional=spec.provisional,
                    reversible=spec.reversible,
                    evidence_refs=spec.evidence_refs,
                    metadata=spec.metadata,
                    incorporation_record_id=spec.incorporation_record_id,
                    expected_before_context_ref=spec.before_context_ref,
                    expected_after_context_ref=spec.after_context_ref,
                )
            )

        scene_relations = []
        for spec in request.scene_relations:
            readability_context = self._require_context(
                context_by_id,
                spec.readability_context_ref,
                "readability_context_ref",
            )
            scene_relations.append(
                self._scene_relation_builder.build(
                    scene=request.scene,
                    readability_context=readability_context,
                    relation_type=spec.relation_type,
                    provisional=spec.provisional,
                    authoritative=spec.authoritative,
                    source_refs=spec.source_refs,
                    evidence_refs=spec.evidence_refs,
                    metadata=spec.metadata,
                    scene_readability_relation_id=(
                        spec.scene_readability_relation_id
                    ),
                    expected_scene_ref=request.scene.stability_scene_id,
                    expected_readability_context_ref=(
                        spec.readability_context_ref
                    ),
                )
            )

        bundle = self._bundle_builder.build(
            process_id=request.process_id,
            slice_ref=request.slice_ref,
            contexts=contexts,
            incorporation_records=incorporations,
            scene_relations=scene_relations,
            metadata=request.bundle_metadata,
            readability_relation_bundle_id=(
                request.readability_relation_bundle_id
            ),
        )

        return IncorporatedReadabilityAssemblyResult(
            scene=request.scene.model_copy(deep=True),
            contexts=contexts,
            incorporations=incorporations,
            scene_relations=scene_relations,
            bundle=bundle,
        )

    @staticmethod
    def _require_context(
        context_by_id: dict[str, ReadabilityContext],
        context_ref: str,
        field_name: str,
    ) -> ReadabilityContext:
        try:
            return context_by_id[context_ref]
        except KeyError as exc:
            raise ValueError(
                f"{field_name} must reference a ReadabilityContext in the same request"
            ) from exc
