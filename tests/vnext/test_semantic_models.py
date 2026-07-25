from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.vnext.models import (
    BoundaryEvaluation,
    BoundaryReadabilityState,
    ContinuationCondition,
    DifferenceObject,
    DifferenceRepresentationType,
    LocalArticulation,
    ReadableRelation,
    StabilityObservation,
    StabilityScene,
    UnresolvedLocalItem,
)


def make_articulation() -> LocalArticulation:
    return LocalArticulation(
        articulation_id="articulation_001",
        process_id="process_001",
        slice_ref="slice_001",
        representation={"state": "readable", "value": "local result"},
        source_refs=["structure_001"],
    )


def test_stability_scene_exists_without_scalar_score() -> None:
    scene = StabilityScene(
        stability_scene_id="scene_001",
        process_id="process_001",
        slice_ref="slice_001",
        articulation=make_articulation(),
        readable_relations=[
            ReadableRelation(
                relation_id="relation_001",
                source_ref="articulation_001",
                target_ref="target_001",
                relation_type="CONTINUATION_CANDIDATE",
            )
        ],
        unresolved_local_items=[
            UnresolvedLocalItem(
                unresolved_item_id="unresolved_001",
                description="A local relation is not yet readable.",
            )
        ],
        continuation_conditions=[
            ContinuationCondition(
                condition_id="condition_001",
                description="The target relation remains readable.",
                satisfied=None,
            )
        ],
    )

    payload = scene.model_dump(mode="json")
    assert "score" not in payload
    assert payload["articulation"]["articulation_id"] == "articulation_001"
    assert len(payload["readable_relations"]) == 1
    assert len(payload["unresolved_local_items"]) == 1
    assert len(payload["continuation_conditions"]) == 1


def test_stability_observation_references_but_does_not_replace_scene() -> None:
    observation = StabilityObservation(
        stability_observation_id="observation_001",
        stability_scene_ref="scene_001",
        score=0.92,
        classification="STABLE",
        confidence=0.84,
        policy_ref="policy_001",
    )

    assert observation.stability_scene_ref == "scene_001"
    assert observation.score == 0.92
    assert not hasattr(observation, "articulation")


def test_difference_object_supports_non_numeric_relation_representation() -> None:
    difference = DifferenceObject(
        difference_id="difference_001",
        process_id="process_001",
        slice_ref="slice_001",
        orientation_ref="orientation_001",
        context_refs=["context_001"],
        representation_type=DifferenceRepresentationType.RELATION,
        representation={
            "source_relation": "member-of",
            "target_relation": "excluded-from",
            "ordering": "incomparable",
        },
        defined=True,
        comparable=False,
        evaluative=False,
    )

    assert difference.representation_type == DifferenceRepresentationType.RELATION
    assert difference.representation["ordering"] == "incomparable"
    assert difference.evaluative is False


def test_defined_difference_requires_representation() -> None:
    with pytest.raises(ValidationError, match="requires representation"):
        DifferenceObject(
            difference_id="difference_missing",
            process_id="process_001",
            slice_ref="slice_001",
            representation_type=DifferenceRepresentationType.SYMBOLIC,
            representation=None,
            defined=True,
        )


def test_boundary_evaluation_references_difference_separately() -> None:
    evaluation = BoundaryEvaluation(
        boundary_evaluation_id="boundary_eval_001",
        process_id="process_001",
        slice_ref="slice_001",
        difference_ref="difference_001",
        orientation_ref="orientation_001",
        context_refs=["context_001"],
        readability_state=BoundaryReadabilityState.USABLE_BOUNDARY,
        readable_as_distinction=True,
        usable_distinction=True,
        provisional=True,
        policy_ref="boundary_policy_001",
    )

    assert evaluation.difference_ref == "difference_001"
    assert evaluation.readable_as_distinction is True
    assert evaluation.usable_distinction is True
    assert evaluation.provisional is True


def test_usable_boundary_requires_readable_distinction() -> None:
    with pytest.raises(ValidationError, match="requires readable_as_distinction"):
        BoundaryEvaluation(
            boundary_evaluation_id="boundary_eval_invalid",
            process_id="process_001",
            slice_ref="slice_001",
            difference_ref="difference_001",
            readability_state=BoundaryReadabilityState.USABLE_BOUNDARY,
            readable_as_distinction=False,
            usable_distinction=True,
        )


def test_usable_boundary_state_requires_usable_distinction() -> None:
    with pytest.raises(ValidationError, match="requires usable_distinction"):
        BoundaryEvaluation(
            boundary_evaluation_id="boundary_eval_state_invalid",
            process_id="process_001",
            slice_ref="slice_001",
            difference_ref="difference_001",
            readability_state=BoundaryReadabilityState.USABLE_BOUNDARY,
            readable_as_distinction=True,
            usable_distinction=False,
        )
