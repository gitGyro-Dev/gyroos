from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from .models import (
    BoundaryEvaluation,
    BoundaryReadabilityState,
    ContinuationCondition,
    DifferenceObject,
    DifferenceRepresentationType,
    IncorporationRecord,
    LocalArticulation,
    ReadabilityContext,
    ReadabilityRelationBundle,
    ReadableRelation,
    SceneReadabilityRelation,
    SemanticRealizationBundle,
    StabilityObservation,
    StabilityScene,
    UnresolvedLocalItem,
)


def new_vnext_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class StabilitySceneBuilder:
    """Construct a StabilityScene from explicit typed inputs only.

    The builder does not infer relations, resolve unresolved items, evaluate
    continuation conditions, calculate Stability, or create observations.
    """

    def build(
        self,
        *,
        process_id: str,
        slice_ref: str,
        articulation: LocalArticulation,
        readable_relations: list[ReadableRelation] | None = None,
        unresolved_local_items: list[UnresolvedLocalItem] | None = None,
        continuation_conditions: list[ContinuationCondition] | None = None,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        stability_scene_id: str | None = None,
    ) -> StabilityScene:
        if articulation.process_id != process_id:
            raise ValueError("articulation process_id must match StabilityScene process_id")
        if articulation.slice_ref != slice_ref:
            raise ValueError("articulation slice_ref must match StabilityScene slice_ref")

        return StabilityScene(
            stability_scene_id=stability_scene_id or new_vnext_id("stability_scene"),
            process_id=process_id,
            slice_ref=slice_ref,
            articulation=articulation.model_copy(deep=True),
            readable_relations=[
                item.model_copy(deep=True) for item in (readable_relations or [])
            ],
            unresolved_local_items=[
                item.model_copy(deep=True) for item in (unresolved_local_items or [])
            ],
            continuation_conditions=[
                item.model_copy(deep=True) for item in (continuation_conditions or [])
            ],
            evidence_refs=list(evidence_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class StabilityObservationBuilder:
    """Construct an observation that references but never replaces a scene.

    The builder accepts explicit observation values only. It does not inspect
    scene content, calculate a score, assign a classification, or evaluate
    continuation conditions.
    """

    def build(
        self,
        *,
        scene: StabilityScene,
        score: float | None = None,
        classification: str | None = None,
        confidence: float | None = None,
        policy_ref: str | None = None,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        stability_observation_id: str | None = None,
        expected_scene_ref: str | None = None,
    ) -> StabilityObservation:
        if (
            expected_scene_ref is not None
            and expected_scene_ref != scene.stability_scene_id
        ):
            raise ValueError(
                "expected_scene_ref must match StabilityScene stability_scene_id"
            )

        return StabilityObservation(
            stability_observation_id=(
                stability_observation_id or new_vnext_id("stability_observation")
            ),
            stability_scene_ref=scene.stability_scene_id,
            score=score,
            classification=classification,
            confidence=confidence,
            policy_ref=policy_ref,
            evidence_refs=list(evidence_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class DifferenceObjectBuilder:
    """Construct a DifferenceObject from explicit representation input only.

    The builder does not extract, compare, normalize, score, or evaluate
    Difference. It preserves the caller-supplied representation and scope.
    """

    def build(
        self,
        *,
        process_id: str,
        slice_ref: str,
        representation_type: DifferenceRepresentationType,
        representation: object,
        orientation_ref: str | None = None,
        context_refs: list[str] | None = None,
        defined: bool = True,
        comparable: bool | None = None,
        evaluative: bool = False,
        slice_relative: bool = True,
        source_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        difference_id: str | None = None,
    ) -> DifferenceObject:
        return DifferenceObject(
            difference_id=difference_id or new_vnext_id("difference"),
            process_id=process_id,
            slice_ref=slice_ref,
            orientation_ref=orientation_ref,
            context_refs=list(context_refs or []),
            representation_type=representation_type,
            representation=deepcopy(representation),
            defined=defined,
            comparable=comparable,
            evaluative=evaluative,
            slice_relative=slice_relative,
            source_refs=list(source_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class BoundaryEvaluationBuilder:
    """Construct a BoundaryEvaluation from explicit evaluation values only.

    The builder does not inspect or compare Difference representation, apply a
    threshold, select a policy, or infer whether a Boundary exists.
    """

    def build(
        self,
        *,
        difference: DifferenceObject,
        readability_state: BoundaryReadabilityState,
        readable_as_distinction: bool,
        usable_distinction: bool,
        provisional: bool = True,
        orientation_ref: str | None = None,
        context_refs: list[str] | None = None,
        policy_ref: str | None = None,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        boundary_evaluation_id: str | None = None,
        expected_difference_ref: str | None = None,
    ) -> BoundaryEvaluation:
        if (
            expected_difference_ref is not None
            and expected_difference_ref != difference.difference_id
        ):
            raise ValueError(
                "expected_difference_ref must match DifferenceObject difference_id"
            )

        return BoundaryEvaluation(
            boundary_evaluation_id=(
                boundary_evaluation_id or new_vnext_id("boundary_evaluation")
            ),
            process_id=difference.process_id,
            slice_ref=difference.slice_ref,
            difference_ref=difference.difference_id,
            orientation_ref=(
                orientation_ref
                if orientation_ref is not None
                else difference.orientation_ref
            ),
            context_refs=(
                list(context_refs)
                if context_refs is not None
                else list(difference.context_refs)
            ),
            readability_state=readability_state,
            readable_as_distinction=readable_as_distinction,
            usable_distinction=usable_distinction,
            provisional=provisional,
            policy_ref=policy_ref,
            evidence_refs=list(evidence_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class SemanticRealizationBundleBuilder:
    """Group existing vNext records by reference without evaluating them.

    The builder validates common process/slice scope and reference ownership.
    It does not copy complete records into the bundle, order evaluations,
    select a preferred observation, or create persistence semantics.
    """

    def build(
        self,
        *,
        scene: StabilityScene,
        observations: list[StabilityObservation] | None = None,
        differences: list[DifferenceObject] | None = None,
        boundary_evaluations: list[BoundaryEvaluation] | None = None,
        metadata: dict[str, object] | None = None,
        semantic_bundle_id: str | None = None,
    ) -> SemanticRealizationBundle:
        observation_items = observations or []
        difference_items = differences or []
        boundary_items = boundary_evaluations or []

        for observation in observation_items:
            if observation.stability_scene_ref != scene.stability_scene_id:
                raise ValueError(
                    "StabilityObservation must reference the bundled StabilityScene"
                )

        difference_ids: set[str] = set()
        for difference in difference_items:
            if difference.process_id != scene.process_id:
                raise ValueError(
                    "DifferenceObject process_id must match StabilityScene process_id"
                )
            if difference.slice_ref != scene.slice_ref:
                raise ValueError(
                    "DifferenceObject slice_ref must match StabilityScene slice_ref"
                )
            difference_ids.add(difference.difference_id)

        for evaluation in boundary_items:
            if evaluation.process_id != scene.process_id:
                raise ValueError(
                    "BoundaryEvaluation process_id must match StabilityScene process_id"
                )
            if evaluation.slice_ref != scene.slice_ref:
                raise ValueError(
                    "BoundaryEvaluation slice_ref must match StabilityScene slice_ref"
                )
            if evaluation.difference_ref not in difference_ids:
                raise ValueError(
                    "BoundaryEvaluation must reference a DifferenceObject in the bundle"
                )

        return SemanticRealizationBundle(
            semantic_bundle_id=(
                semantic_bundle_id or new_vnext_id("semantic_bundle")
            ),
            process_id=scene.process_id,
            slice_ref=scene.slice_ref,
            stability_scene_ref=scene.stability_scene_id,
            stability_observation_refs=[
                item.stability_observation_id for item in observation_items
            ],
            difference_refs=[item.difference_id for item in difference_items],
            boundary_evaluation_refs=[
                item.boundary_evaluation_id for item in boundary_items
            ],
            metadata=deepcopy(metadata or {}),
        )


class ReadabilityContextBuilder:
    """Construct an explicit readability context without deriving readability."""

    def build(
        self,
        *,
        process_id: str,
        slice_ref: str,
        readable_item_refs: list[str] | None = None,
        unresolved_item_refs: list[str] | None = None,
        excluded_item_refs: list[str] | None = None,
        source_context_refs: list[str] | None = None,
        provisional: bool = True,
        metadata: dict[str, object] | None = None,
        readability_context_id: str | None = None,
    ) -> ReadabilityContext:
        return ReadabilityContext(
            readability_context_id=(
                readability_context_id or new_vnext_id("readability_context")
            ),
            process_id=process_id,
            slice_ref=slice_ref,
            readable_item_refs=list(readable_item_refs or []),
            unresolved_item_refs=list(unresolved_item_refs or []),
            excluded_item_refs=list(excluded_item_refs or []),
            source_context_refs=list(source_context_refs or []),
            provisional=provisional,
            metadata=deepcopy(metadata or {}),
        )


class IncorporationRecordBuilder:
    """Record an explicit readability-context update without executing it."""

    def build(
        self,
        *,
        before_context: ReadabilityContext,
        after_context: ReadabilityContext,
        incorporated_item_refs: list[str] | None = None,
        rejected_item_refs: list[str] | None = None,
        update_reason: str,
        provisional: bool = True,
        reversible: bool = True,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        incorporation_record_id: str | None = None,
        expected_before_context_ref: str | None = None,
        expected_after_context_ref: str | None = None,
    ) -> IncorporationRecord:
        if before_context.process_id != after_context.process_id:
            raise ValueError(
                "before and after ReadabilityContext process_id values must match"
            )
        if before_context.slice_ref != after_context.slice_ref:
            raise ValueError(
                "before and after ReadabilityContext slice_ref values must match"
            )
        if before_context.readability_context_id == after_context.readability_context_id:
            raise ValueError(
                "before and after ReadabilityContext references must be distinct"
            )
        if (
            expected_before_context_ref is not None
            and expected_before_context_ref != before_context.readability_context_id
        ):
            raise ValueError(
                "expected_before_context_ref must match before ReadabilityContext"
            )
        if (
            expected_after_context_ref is not None
            and expected_after_context_ref != after_context.readability_context_id
        ):
            raise ValueError(
                "expected_after_context_ref must match after ReadabilityContext"
            )

        return IncorporationRecord(
            incorporation_record_id=(
                incorporation_record_id or new_vnext_id("incorporation_record")
            ),
            process_id=before_context.process_id,
            slice_ref=before_context.slice_ref,
            before_context_ref=before_context.readability_context_id,
            after_context_ref=after_context.readability_context_id,
            incorporated_item_refs=list(incorporated_item_refs or []),
            rejected_item_refs=list(rejected_item_refs or []),
            update_reason=update_reason,
            provisional=provisional,
            reversible=reversible,
            evidence_refs=list(evidence_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class SceneReadabilityRelationBuilder:
    """Relate one StabilityScene to one ReadabilityContext by explicit reference only.

    The builder does not derive the context from the scene, update either record,
    or infer whether the relation is authoritative.
    """

    def build(
        self,
        *,
        scene: StabilityScene,
        readability_context: ReadabilityContext,
        relation_type: str,
        provisional: bool = True,
        authoritative: bool = False,
        source_refs: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, object] | None = None,
        scene_readability_relation_id: str | None = None,
        expected_scene_ref: str | None = None,
        expected_readability_context_ref: str | None = None,
    ) -> SceneReadabilityRelation:
        if scene.process_id != readability_context.process_id:
            raise ValueError(
                "StabilityScene and ReadabilityContext process_id values must match"
            )
        if scene.slice_ref != readability_context.slice_ref:
            raise ValueError(
                "StabilityScene and ReadabilityContext slice_ref values must match"
            )
        if (
            expected_scene_ref is not None
            and expected_scene_ref != scene.stability_scene_id
        ):
            raise ValueError(
                "expected_scene_ref must match StabilityScene stability_scene_id"
            )
        if (
            expected_readability_context_ref is not None
            and expected_readability_context_ref
            != readability_context.readability_context_id
        ):
            raise ValueError(
                "expected_readability_context_ref must match ReadabilityContext"
            )

        return SceneReadabilityRelation(
            scene_readability_relation_id=(
                scene_readability_relation_id
                or new_vnext_id("scene_readability_relation")
            ),
            process_id=scene.process_id,
            slice_ref=scene.slice_ref,
            stability_scene_ref=scene.stability_scene_id,
            readability_context_ref=readability_context.readability_context_id,
            relation_type=relation_type,
            provisional=provisional,
            authoritative=authoritative,
            source_refs=list(source_refs or []),
            evidence_refs=list(evidence_refs or []),
            metadata=deepcopy(metadata or {}),
        )


class ReadabilityRelationBundleBuilder:
    """Group Incorporated Readability records by reference without selecting them."""

    def build(
        self,
        *,
        process_id: str,
        slice_ref: str,
        readability_contexts: list[ReadabilityContext] | None = None,
        incorporation_records: list[IncorporationRecord] | None = None,
        scene_readability_relations: list[SceneReadabilityRelation] | None = None,
        metadata: dict[str, object] | None = None,
        readability_relation_bundle_id: str | None = None,
    ) -> ReadabilityRelationBundle:
        context_items = readability_contexts or []
        incorporation_items = incorporation_records or []
        relation_items = scene_readability_relations or []

        context_ids: set[str] = set()
        for context in context_items:
            if context.process_id != process_id:
                raise ValueError(
                    "ReadabilityContext process_id must match bundle process_id"
                )
            if context.slice_ref != slice_ref:
                raise ValueError(
                    "ReadabilityContext slice_ref must match bundle slice_ref"
                )
            context_ids.add(context.readability_context_id)

        for record in incorporation_items:
            if record.process_id != process_id:
                raise ValueError(
                    "IncorporationRecord process_id must match bundle process_id"
                )
            if record.slice_ref != slice_ref:
                raise ValueError(
                    "IncorporationRecord slice_ref must match bundle slice_ref"
                )
            if record.before_context_ref not in context_ids:
                raise ValueError(
                    "IncorporationRecord before_context_ref must reference a bundled ReadabilityContext"
                )
            if record.after_context_ref not in context_ids:
                raise ValueError(
                    "IncorporationRecord after_context_ref must reference a bundled ReadabilityContext"
                )

        for relation in relation_items:
            if relation.process_id != process_id:
                raise ValueError(
                    "SceneReadabilityRelation process_id must match bundle process_id"
                )
            if relation.slice_ref != slice_ref:
                raise ValueError(
                    "SceneReadabilityRelation slice_ref must match bundle slice_ref"
                )
            if relation.readability_context_ref not in context_ids:
                raise ValueError(
                    "SceneReadabilityRelation must reference a bundled ReadabilityContext"
                )

        return ReadabilityRelationBundle(
            readability_relation_bundle_id=(
                readability_relation_bundle_id
                or new_vnext_id("readability_relation_bundle")
            ),
            process_id=process_id,
            slice_ref=slice_ref,
            readability_context_refs=[
                item.readability_context_id for item in context_items
            ],
            incorporation_record_refs=[
                item.incorporation_record_id for item in incorporation_items
            ],
            scene_readability_relation_refs=[
                item.scene_readability_relation_id for item in relation_items
            ],
            metadata=deepcopy(metadata or {}),
        )
