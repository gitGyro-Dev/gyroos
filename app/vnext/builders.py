from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from .models import (
    ContinuationCondition,
    LocalArticulation,
    ReadableRelation,
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
