from __future__ import annotations

import pytest

from app.vnext.builders import (
    ReadabilityContextBuilder,
    SceneReadabilityRelationBuilder,
    StabilitySceneBuilder,
)
from app.vnext.models import LocalArticulation, SceneReadabilityRelation


def build_scene(*, process_id: str = "process_001", slice_ref: str = "slice_001"):
    articulation = LocalArticulation(
        articulation_id="articulation_001",
        process_id=process_id,
        slice_ref=slice_ref,
        representation={"state": "readable"},
    )
    return StabilitySceneBuilder().build(
        process_id=process_id,
        slice_ref=slice_ref,
        articulation=articulation,
        stability_scene_id="scene_001",
    )


def build_context(*, process_id: str = "process_001", slice_ref: str = "slice_001"):
    return ReadabilityContextBuilder().build(
        process_id=process_id,
        slice_ref=slice_ref,
        readability_context_id="context_001",
        readable_item_refs=["item_001"],
    )


def test_relation_references_scene_and_context_without_embedding_them() -> None:
    relation = SceneReadabilityRelationBuilder().build(
        scene=build_scene(),
        readability_context=build_context(),
        relation_type="READ_WITH_CONTEXT",
        scene_readability_relation_id="scene_context_relation_001",
    )

    assert relation.stability_scene_ref == "scene_001"
    assert relation.readability_context_ref == "context_001"
    assert relation.relation_type == "READ_WITH_CONTEXT"
    assert "articulation" not in SceneReadabilityRelation.model_fields
    assert "readable_item_refs" not in SceneReadabilityRelation.model_fields


def test_authoritative_is_explicit_and_not_inferred() -> None:
    relation = SceneReadabilityRelationBuilder().build(
        scene=build_scene(),
        readability_context=build_context(),
        relation_type="READ_WITH_CONTEXT",
    )

    assert relation.authoritative is False
    assert relation.provisional is True


def test_explicit_authoritative_value_is_preserved() -> None:
    relation = SceneReadabilityRelationBuilder().build(
        scene=build_scene(),
        readability_context=build_context(),
        relation_type="SELECTED_CONTEXT",
        authoritative=True,
        provisional=False,
    )

    assert relation.authoritative is True
    assert relation.provisional is False


def test_process_scope_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="process_id values must match"):
        SceneReadabilityRelationBuilder().build(
            scene=build_scene(),
            readability_context=build_context(process_id="process_other"),
            relation_type="READ_WITH_CONTEXT",
        )


def test_slice_scope_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="slice_ref values must match"):
        SceneReadabilityRelationBuilder().build(
            scene=build_scene(),
            readability_context=build_context(slice_ref="slice_other"),
            relation_type="READ_WITH_CONTEXT",
        )


def test_expected_references_are_validated() -> None:
    builder = SceneReadabilityRelationBuilder()

    with pytest.raises(ValueError, match="expected_scene_ref must match"):
        builder.build(
            scene=build_scene(),
            readability_context=build_context(),
            relation_type="READ_WITH_CONTEXT",
            expected_scene_ref="scene_other",
        )

    with pytest.raises(ValueError, match="expected_readability_context_ref must match"):
        builder.build(
            scene=build_scene(),
            readability_context=build_context(),
            relation_type="READ_WITH_CONTEXT",
            expected_readability_context_ref="context_other",
        )


def test_mutable_inputs_are_copied() -> None:
    source_refs = ["source_001"]
    evidence_refs = ["evidence_001"]
    metadata = {"selection": {"kind": "explicit"}}

    relation = SceneReadabilityRelationBuilder().build(
        scene=build_scene(),
        readability_context=build_context(),
        relation_type="READ_WITH_CONTEXT",
        source_refs=source_refs,
        evidence_refs=evidence_refs,
        metadata=metadata,
    )

    source_refs.append("source_002")
    evidence_refs.append("evidence_002")
    metadata["selection"]["kind"] = "changed"

    assert relation.source_refs == ["source_001"]
    assert relation.evidence_refs == ["evidence_001"]
    assert relation.metadata == {"selection": {"kind": "explicit"}}
