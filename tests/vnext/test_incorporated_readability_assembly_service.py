import pytest

from app.vnext.models import (
    IncorporatedReadabilityAssemblyRequest,
    IncorporationSpec,
    LocalArticulation,
    ReadabilityContextSpec,
    SceneReadabilityRelationSpec,
    StabilityScene,
)
from app.vnext.readability_assembly import IncorporatedReadabilityAssemblyService


def make_scene(*, process_id: str = "process-1", slice_ref: str = "slice-1") -> StabilityScene:
    return StabilityScene(
        stability_scene_id="scene-1",
        process_id=process_id,
        slice_ref=slice_ref,
        articulation=LocalArticulation(
            articulation_id="articulation-1",
            process_id=process_id,
            slice_ref=slice_ref,
            representation={"state": "locally-readable"},
        ),
    )


def test_assembles_explicit_incorporated_readability_records() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(),
        contexts=[
            ReadabilityContextSpec(
                readability_context_id="context-before",
                readable_item_refs=["item-a"],
            ),
            ReadabilityContextSpec(
                readability_context_id="context-after",
                readable_item_refs=["item-a", "item-b"],
            ),
        ],
        incorporations=[
            IncorporationSpec(
                incorporation_record_id="incorporation-1",
                before_context_ref="context-before",
                after_context_ref="context-after",
                incorporated_item_refs=["item-b"],
                update_reason="explicit-review",
            )
        ],
        scene_relations=[
            SceneReadabilityRelationSpec(
                scene_readability_relation_id="scene-relation-1",
                readability_context_ref="context-after",
                relation_type="AVAILABLE_FOR_SCENE",
                authoritative=False,
            )
        ],
        readability_relation_bundle_id="readability-bundle-1",
    )

    result = IncorporatedReadabilityAssemblyService().assemble(request)

    assert [item.readability_context_id for item in result.contexts] == [
        "context-before",
        "context-after",
    ]
    assert result.incorporations[0].before_context_ref == "context-before"
    assert result.incorporations[0].after_context_ref == "context-after"
    assert result.scene_relations[0].stability_scene_ref == "scene-1"
    assert result.scene_relations[0].readability_context_ref == "context-after"
    assert result.bundle.readability_context_refs == [
        "context-before",
        "context-after",
    ]
    assert result.bundle.incorporation_record_refs == ["incorporation-1"]
    assert result.bundle.scene_readability_relation_refs == ["scene-relation-1"]


def test_optional_record_groups_may_be_empty() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(),
    )

    result = IncorporatedReadabilityAssemblyService().assemble(request)

    assert result.contexts == []
    assert result.incorporations == []
    assert result.scene_relations == []
    assert result.bundle.readability_context_refs == []


def test_does_not_infer_current_or_authoritative_context() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(),
        contexts=[
            ReadabilityContextSpec(readability_context_id="context-old"),
            ReadabilityContextSpec(readability_context_id="context-new"),
        ],
        scene_relations=[
            SceneReadabilityRelationSpec(
                readability_context_ref="context-old",
                relation_type="AVAILABLE",
            ),
            SceneReadabilityRelationSpec(
                readability_context_ref="context-new",
                relation_type="AVAILABLE",
            ),
        ],
    )

    result = IncorporatedReadabilityAssemblyService().assemble(request)

    assert all(not relation.authoritative for relation in result.scene_relations)
    assert "current_context_ref" not in result.bundle.model_fields
    assert "authoritative_context_ref" not in result.bundle.model_fields


def test_rejects_context_reference_outside_request() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(),
        contexts=[ReadabilityContextSpec(readability_context_id="context-1")],
        incorporations=[
            IncorporationSpec(
                before_context_ref="context-1",
                after_context_ref="missing-context",
                update_reason="explicit-review",
            )
        ],
    )

    with pytest.raises(ValueError, match="same request"):
        IncorporatedReadabilityAssemblyService().assemble(request)


def test_rejects_duplicate_context_ids() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(),
        contexts=[
            ReadabilityContextSpec(readability_context_id="context-1"),
            ReadabilityContextSpec(readability_context_id="context-1"),
        ],
    )

    with pytest.raises(ValueError, match="unique"):
        IncorporatedReadabilityAssemblyService().assemble(request)


def test_rejects_scene_scope_mismatch() -> None:
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=make_scene(process_id="other-process"),
    )

    with pytest.raises(ValueError, match="process_id"):
        IncorporatedReadabilityAssemblyService().assemble(request)


def test_copies_nested_request_inputs() -> None:
    context_metadata = {"nested": {"items": ["original"]}}
    bundle_metadata = {"nested": {"items": ["bundle-original"]}}
    scene = make_scene()
    request = IncorporatedReadabilityAssemblyRequest(
        process_id="process-1",
        slice_ref="slice-1",
        scene=scene,
        contexts=[
            ReadabilityContextSpec(
                readability_context_id="context-1",
                metadata=context_metadata,
            )
        ],
        bundle_metadata=bundle_metadata,
    )

    result = IncorporatedReadabilityAssemblyService().assemble(request)
    context_metadata["nested"]["items"].append("mutated")
    bundle_metadata["nested"]["items"].append("mutated")
    scene.metadata["changed"] = True

    assert result.contexts[0].metadata == {"nested": {"items": ["original"]}}
    assert result.bundle.metadata == {
        "nested": {"items": ["bundle-original"]}
    }
    assert "changed" not in result.scene.metadata
