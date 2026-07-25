from __future__ import annotations

import pytest

from app.vnext.builders import (
    BoundaryEvaluationBuilder,
    SemanticRealizationBundleBuilder,
    StabilityObservationBuilder,
    StabilitySceneBuilder,
)
from app.vnext.models import (
    BoundaryReadabilityState,
    DifferenceObject,
    DifferenceRepresentationType,
    LocalArticulation,
    SemanticRealizationBundle,
)


def build_scene():
    articulation = LocalArticulation(
        articulation_id="articulation_001",
        process_id="process_001",
        slice_ref="slice_001",
        representation={"state": "readable"},
    )
    return StabilitySceneBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=articulation,
        stability_scene_id="scene_001",
    )


def build_difference(
    *, process_id: str = "process_001", slice_ref: str = "slice_001"
) -> DifferenceObject:
    return DifferenceObject(
        difference_id="difference_001",
        process_id=process_id,
        slice_ref=slice_ref,
        representation_type=DifferenceRepresentationType.RELATION,
        representation={"relation": "different-readable-path"},
    )


def test_bundle_groups_existing_records_by_reference_only() -> None:
    scene = build_scene()
    observation = StabilityObservationBuilder().build(
        scene=scene,
        score=0.91,
        stability_observation_id="observation_001",
    )
    difference = build_difference()
    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference,
        readability_state=BoundaryReadabilityState.READABLE_DISTINCTION,
        readable_as_distinction=True,
        usable_distinction=False,
        boundary_evaluation_id="boundary_evaluation_001",
    )

    bundle = SemanticRealizationBundleBuilder().build(
        scene=scene,
        observations=[observation],
        differences=[difference],
        boundary_evaluations=[evaluation],
        semantic_bundle_id="semantic_bundle_001",
    )

    assert bundle.process_id == "process_001"
    assert bundle.slice_ref == "slice_001"
    assert bundle.stability_scene_ref == "scene_001"
    assert bundle.stability_observation_refs == ["observation_001"]
    assert bundle.difference_refs == ["difference_001"]
    assert bundle.boundary_evaluation_refs == ["boundary_evaluation_001"]
    assert "articulation" not in SemanticRealizationBundle.model_fields
    assert "differences" not in SemanticRealizationBundle.model_fields
    assert "boundary_evaluations" not in SemanticRealizationBundle.model_fields


def test_bundle_allows_empty_optional_reference_groups() -> None:
    bundle = SemanticRealizationBundleBuilder().build(scene=build_scene())

    assert bundle.stability_observation_refs == []
    assert bundle.difference_refs == []
    assert bundle.boundary_evaluation_refs == []


def test_bundle_rejects_observation_for_another_scene() -> None:
    observation = StabilityObservationBuilder().build(
        scene=build_scene().model_copy(update={"stability_scene_id": "scene_other"})
    )

    with pytest.raises(ValueError, match="must reference the bundled StabilityScene"):
        SemanticRealizationBundleBuilder().build(
            scene=build_scene(),
            observations=[observation],
        )


def test_bundle_rejects_difference_from_another_process() -> None:
    with pytest.raises(ValueError, match="process_id must match"):
        SemanticRealizationBundleBuilder().build(
            scene=build_scene(),
            differences=[build_difference(process_id="process_other")],
        )


def test_bundle_rejects_difference_from_another_slice() -> None:
    with pytest.raises(ValueError, match="slice_ref must match"):
        SemanticRealizationBundleBuilder().build(
            scene=build_scene(),
            differences=[build_difference(slice_ref="slice_other")],
        )


def test_bundle_rejects_boundary_evaluation_without_bundled_difference() -> None:
    difference = build_difference()
    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference,
        readability_state=BoundaryReadabilityState.CANDIDATE,
        readable_as_distinction=False,
        usable_distinction=False,
    )

    with pytest.raises(ValueError, match="DifferenceObject in the bundle"):
        SemanticRealizationBundleBuilder().build(
            scene=build_scene(),
            boundary_evaluations=[evaluation],
        )


def test_bundle_copies_nested_metadata() -> None:
    metadata = {"source": {"kind": "explicit"}}

    bundle = SemanticRealizationBundleBuilder().build(
        scene=build_scene(),
        metadata=metadata,
    )
    metadata["source"]["kind"] = "changed"

    assert bundle.metadata == {"source": {"kind": "explicit"}}
