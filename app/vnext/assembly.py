from __future__ import annotations

from .builders import (
    BoundaryEvaluationBuilder,
    DifferenceObjectBuilder,
    SemanticRealizationBundleBuilder,
    StabilityObservationBuilder,
    StabilitySceneBuilder,
)
from .models import SemanticAssemblyRequest, SemanticAssemblyResult


class SemanticAssemblyService:
    """Coordinate existing pure builders without adding evaluation semantics.

    The service does not infer Stability, extract Difference, evaluate Boundary,
    select OperatorResponse, persist records, or modify the current Runtime.
    """

    def __init__(
        self,
        *,
        scene_builder: StabilitySceneBuilder | None = None,
        observation_builder: StabilityObservationBuilder | None = None,
        difference_builder: DifferenceObjectBuilder | None = None,
        boundary_builder: BoundaryEvaluationBuilder | None = None,
        bundle_builder: SemanticRealizationBundleBuilder | None = None,
    ) -> None:
        self._scene_builder = scene_builder or StabilitySceneBuilder()
        self._observation_builder = observation_builder or StabilityObservationBuilder()
        self._difference_builder = difference_builder or DifferenceObjectBuilder()
        self._boundary_builder = boundary_builder or BoundaryEvaluationBuilder()
        self._bundle_builder = bundle_builder or SemanticRealizationBundleBuilder()

    def assemble(self, request: SemanticAssemblyRequest) -> SemanticAssemblyResult:
        scene = self._scene_builder.build(
            process_id=request.process_id,
            slice_ref=request.slice_ref,
            articulation=request.articulation,
            readable_relations=request.readable_relations,
            unresolved_local_items=request.unresolved_local_items,
            continuation_conditions=request.continuation_conditions,
            evidence_refs=request.scene_evidence_refs,
            metadata=request.scene_metadata,
            stability_scene_id=request.stability_scene_id,
        )

        observations = [
            self._observation_builder.build(
                scene=scene,
                score=spec.score,
                classification=spec.classification,
                confidence=spec.confidence,
                policy_ref=spec.policy_ref,
                evidence_refs=spec.evidence_refs,
                metadata=spec.metadata,
                stability_observation_id=spec.stability_observation_id,
                expected_scene_ref=scene.stability_scene_id,
            )
            for spec in request.observations
        ]

        differences = [
            self._difference_builder.build(
                process_id=request.process_id,
                slice_ref=request.slice_ref,
                representation_type=spec.representation_type,
                representation=spec.representation,
                orientation_ref=spec.orientation_ref,
                context_refs=spec.context_refs,
                defined=spec.defined,
                comparable=spec.comparable,
                evaluative=spec.evaluative,
                slice_relative=spec.slice_relative,
                source_refs=spec.source_refs,
                metadata=spec.metadata,
                difference_id=spec.difference_id,
            )
            for spec in request.differences
        ]

        difference_by_id = {item.difference_id: item for item in differences}
        boundary_evaluations = []
        for spec in request.boundary_evaluations:
            difference = difference_by_id.get(spec.difference_ref)
            if difference is None:
                raise ValueError(
                    "BoundaryEvaluationSpec must reference a DifferenceSpec assembled in the same request"
                )
            boundary_evaluations.append(
                self._boundary_builder.build(
                    difference=difference,
                    readability_state=spec.readability_state,
                    readable_as_distinction=spec.readable_as_distinction,
                    usable_distinction=spec.usable_distinction,
                    provisional=spec.provisional,
                    orientation_ref=spec.orientation_ref,
                    context_refs=spec.context_refs,
                    policy_ref=spec.policy_ref,
                    evidence_refs=spec.evidence_refs,
                    metadata=spec.metadata,
                    boundary_evaluation_id=spec.boundary_evaluation_id,
                    expected_difference_ref=difference.difference_id,
                )
            )

        bundle = self._bundle_builder.build(
            scene=scene,
            observations=observations,
            differences=differences,
            boundary_evaluations=boundary_evaluations,
            metadata=request.bundle_metadata,
            semantic_bundle_id=request.semantic_bundle_id,
        )

        return SemanticAssemblyResult(
            scene=scene,
            observations=observations,
            differences=differences,
            boundary_evaluations=boundary_evaluations,
            bundle=bundle,
        )
