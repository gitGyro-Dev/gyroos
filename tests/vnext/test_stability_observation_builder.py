from __future__ import annotations

import pytest

from app.vnext.builders import StabilityObservationBuilder, StabilitySceneBuilder
from app.vnext.models import LocalArticulation, StabilityObservation


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


def test_observation_references_scene_without_replacing_it() -> None:
    scene = build_scene()

    observation = StabilityObservationBuilder().build(
        scene=scene,
        score=0.92,
        classification="STABLE",
        confidence=0.84,
        policy_ref="policy_001",
        stability_observation_id="observation_001",
    )

    assert observation.stability_scene_ref == "scene_001"
    assert observation.score == 0.92
    assert observation.classification == "STABLE"
    assert observation.confidence == 0.84
    assert observation.policy_ref == "policy_001"
    assert "articulation" not in StabilityObservation.model_fields


def test_observation_does_not_require_score_or_classification() -> None:
    observation = StabilityObservationBuilder().build(scene=build_scene())

    assert observation.score is None
    assert observation.classification is None
    assert observation.confidence is None


def test_observation_does_not_infer_from_scene_content() -> None:
    scene = build_scene()
    scene.articulation.representation["stability"] = 0.99

    observation = StabilityObservationBuilder().build(scene=scene)

    assert observation.score is None
    assert observation.classification is None


def test_expected_scene_reference_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="expected_scene_ref must match"):
        StabilityObservationBuilder().build(
            scene=build_scene(),
            expected_scene_ref="scene_other",
        )


def test_mutable_observation_inputs_are_copied() -> None:
    evidence_refs = ["evidence_001"]
    metadata = {"source": {"kind": "explicit"}}

    observation = StabilityObservationBuilder().build(
        scene=build_scene(),
        evidence_refs=evidence_refs,
        metadata=metadata,
    )

    evidence_refs.append("evidence_002")
    metadata["source"]["kind"] = "changed"

    assert observation.evidence_refs == ["evidence_001"]
    assert observation.metadata == {"source": {"kind": "explicit"}}
