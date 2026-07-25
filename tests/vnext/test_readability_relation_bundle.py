from __future__ import annotations

import pytest

from app.vnext.builders import (
    IncorporationRecordBuilder,
    ReadabilityContextBuilder,
    ReadabilityRelationBundleBuilder,
    SceneReadabilityRelationBuilder,
    StabilitySceneBuilder,
)
from app.vnext.models import LocalArticulation, ReadabilityRelationBundle


def make_scene(*, process_id: str = "process-1", slice_ref: str = "slice-1"):
    articulation = LocalArticulation(
        articulation_id="articulation-1",
        process_id=process_id,
        slice_ref=slice_ref,
        representation={"state": "local"},
    )
    return StabilitySceneBuilder().build(
        process_id=process_id,
        slice_ref=slice_ref,
        articulation=articulation,
        stability_scene_id="scene-1",
    )


def make_context(
    context_id: str,
    *,
    process_id: str = "process-1",
    slice_ref: str = "slice-1",
):
    return ReadabilityContextBuilder().build(
        process_id=process_id,
        slice_ref=slice_ref,
        readable_item_refs=[f"item-{context_id}"],
        readability_context_id=context_id,
    )


def test_bundle_stores_references_only() -> None:
    before = make_context("context-before")
    after = make_context("context-after")
    record = IncorporationRecordBuilder().build(
        before_context=before,
        after_context=after,
        incorporated_item_refs=["item-new"],
        update_reason="explicit update",
        incorporation_record_id="incorporation-1",
    )
    relation = SceneReadabilityRelationBuilder().build(
        scene=make_scene(),
        readability_context=after,
        relation_type="READABLE_UNDER",
        authoritative=True,
        scene_readability_relation_id="scene-relation-1",
    )

    bundle = ReadabilityRelationBundleBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        readability_contexts=[before, after],
        incorporation_records=[record],
        scene_readability_relations=[relation],
        readability_relation_bundle_id="readability-bundle-1",
    )

    assert bundle.readability_context_refs == ["context-before", "context-after"]
    assert bundle.incorporation_record_refs == ["incorporation-1"]
    assert bundle.scene_readability_relation_refs == ["scene-relation-1"]
    assert "readability_contexts" not in ReadabilityRelationBundle.model_fields
    assert "current_context_ref" not in ReadabilityRelationBundle.model_fields
    assert "authoritative_relation_ref" not in ReadabilityRelationBundle.model_fields


def test_empty_bundle_is_allowed() -> None:
    bundle = ReadabilityRelationBundleBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
    )

    assert bundle.readability_context_refs == []
    assert bundle.incorporation_record_refs == []
    assert bundle.scene_readability_relation_refs == []


def test_context_scope_mismatch_is_rejected() -> None:
    context = make_context("context-1", process_id="other-process")

    with pytest.raises(ValueError, match="ReadabilityContext process_id"):
        ReadabilityRelationBundleBuilder().build(
            process_id="process-1",
            slice_ref="slice-1",
            readability_contexts=[context],
        )


def test_incorporation_record_requires_bundled_contexts() -> None:
    before = make_context("context-before")
    after = make_context("context-after")
    record = IncorporationRecordBuilder().build(
        before_context=before,
        after_context=after,
        update_reason="explicit update",
    )

    with pytest.raises(ValueError, match="after_context_ref"):
        ReadabilityRelationBundleBuilder().build(
            process_id="process-1",
            slice_ref="slice-1",
            readability_contexts=[before],
            incorporation_records=[record],
        )


def test_scene_relation_requires_bundled_context() -> None:
    context = make_context("context-1")
    relation = SceneReadabilityRelationBuilder().build(
        scene=make_scene(),
        readability_context=context,
        relation_type="READABLE_UNDER",
    )

    with pytest.raises(ValueError, match="bundled ReadabilityContext"):
        ReadabilityRelationBundleBuilder().build(
            process_id="process-1",
            slice_ref="slice-1",
            scene_readability_relations=[relation],
        )


def test_bundle_does_not_select_current_or_authoritative_records() -> None:
    first = make_context("context-first")
    second = make_context("context-second")
    relation = SceneReadabilityRelationBuilder().build(
        scene=make_scene(),
        readability_context=second,
        relation_type="READABLE_UNDER",
        authoritative=True,
    )

    bundle = ReadabilityRelationBundleBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        readability_contexts=[first, second],
        scene_readability_relations=[relation],
    )

    assert bundle.readability_context_refs == ["context-first", "context-second"]
    assert "current_context_ref" not in ReadabilityRelationBundle.model_fields
    assert "authoritative_relation_ref" not in ReadabilityRelationBundle.model_fields


def test_nested_metadata_is_copied() -> None:
    metadata = {"review": {"tags": ["explicit"]}}

    bundle = ReadabilityRelationBundleBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        metadata=metadata,
    )
    metadata["review"]["tags"].append("mutated")

    assert bundle.metadata == {"review": {"tags": ["explicit"]}}
