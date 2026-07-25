from __future__ import annotations

import pytest

from app.vnext.builders import StabilitySceneBuilder
from app.vnext.models import (
    ContinuationCondition,
    LocalArticulation,
    ReadableRelation,
    UnresolvedLocalItem,
)


def articulation() -> LocalArticulation:
    return LocalArticulation(
        articulation_id="articulation_001",
        process_id="process_001",
        slice_ref="slice_001",
        representation={"state": "readable"},
        source_refs=["structure_001"],
    )


def test_builder_constructs_scene_from_explicit_inputs_only() -> None:
    relation = ReadableRelation(
        relation_id="relation_001",
        source_ref="articulation_001",
        target_ref="target_001",
        relation_type="LOCAL_READABILITY",
        evidence_refs=["evidence_001"],
    )
    unresolved = UnresolvedLocalItem(
        unresolved_item_id="unresolved_001",
        description="A local relation is not yet readable.",
        related_refs=["target_002"],
    )
    condition = ContinuationCondition(
        condition_id="condition_001",
        description="The readable relation remains available.",
        satisfied=None,
        evidence_refs=["evidence_001"],
    )

    scene = StabilitySceneBuilder().build(
        stability_scene_id="scene_001",
        process_id="process_001",
        slice_ref="slice_001",
        articulation=articulation(),
        readable_relations=[relation],
        unresolved_local_items=[unresolved],
        continuation_conditions=[condition],
        evidence_refs=["evidence_001"],
        metadata={"source": "explicit-test-input"},
    )

    assert scene.stability_scene_id == "scene_001"
    assert scene.articulation.articulation_id == "articulation_001"
    assert scene.readable_relations == [relation]
    assert scene.unresolved_local_items == [unresolved]
    assert scene.continuation_conditions == [condition]
    assert scene.evidence_refs == ["evidence_001"]
    assert scene.metadata == {"source": "explicit-test-input"}
    assert "score" not in scene.model_fields
    assert "classification" not in scene.model_fields


def test_builder_allows_scene_without_relations_or_conditions() -> None:
    scene = StabilitySceneBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=articulation(),
    )

    assert scene.readable_relations == []
    assert scene.unresolved_local_items == []
    assert scene.continuation_conditions == []
    assert scene.evidence_refs == []


def test_builder_rejects_articulation_from_another_process() -> None:
    wrong = articulation().model_copy(update={"process_id": "process_other"})

    with pytest.raises(ValueError, match="process_id must match"):
        StabilitySceneBuilder().build(
            process_id="process_001",
            slice_ref="slice_001",
            articulation=wrong,
        )


def test_builder_rejects_articulation_from_another_slice() -> None:
    wrong = articulation().model_copy(update={"slice_ref": "slice_other"})

    with pytest.raises(ValueError, match="slice_ref must match"):
        StabilitySceneBuilder().build(
            process_id="process_001",
            slice_ref="slice_001",
            articulation=wrong,
        )


def test_builder_copies_mutable_inputs() -> None:
    relation = ReadableRelation(
        relation_id="relation_001",
        source_ref="articulation_001",
        relation_type="LOCAL_READABILITY",
        metadata={"version": 1},
    )
    evidence_refs = ["evidence_001"]
    metadata = {"source": "before"}

    scene = StabilitySceneBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=articulation(),
        readable_relations=[relation],
        evidence_refs=evidence_refs,
        metadata=metadata,
    )

    relation.metadata["version"] = 2
    evidence_refs.append("evidence_002")
    metadata["source"] = "after"

    assert scene.readable_relations[0].metadata == {"version": 1}
    assert scene.evidence_refs == ["evidence_001"]
    assert scene.metadata == {"source": "before"}
