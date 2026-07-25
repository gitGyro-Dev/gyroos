from __future__ import annotations

import pytest

from app.vnext.builders import (
    ContinuityReadabilityContextBuilder,
    ContinuityRelationBundleBuilder,
    ContinuityRelationRecordBuilder,
)
from app.vnext.continuity_readability_assembly import (
    ContinuityReadabilityAssemblyService,
)
from app.vnext.models import (
    ContinuityReadabilityAssemblyRequest,
    ContinuityReadabilityContextSpec,
    ContinuityRelationBundle,
    ContinuityRelationSpec,
)


def test_bundle_stores_references_only() -> None:
    context = ContinuityReadabilityContextBuilder().build(
        process_id="process-1",
        source_slice_ref="slice-1",
        target_slice_ref="slice-2",
        continuity_readability_context_id="continuity-context-1",
    )
    relation = ContinuityRelationRecordBuilder().build(
        continuity_context=context,
        source_ref="record-1",
        target_ref="record-2",
        relation_type="READABLE_ACROSS",
        readable=True,
        continuity_relation_id="continuity-relation-1",
    )

    bundle = ContinuityRelationBundleBuilder().build(
        continuity_context=context,
        relations=[relation],
        continuity_relation_bundle_id="continuity-bundle-1",
    )

    assert bundle.continuity_readability_context_ref == "continuity-context-1"
    assert bundle.continuity_relation_refs == ["continuity-relation-1"]
    assert "relations" not in ContinuityRelationBundle.model_fields
    assert "current_relation_ref" not in ContinuityRelationBundle.model_fields
    assert "authoritative_relation_ref" not in ContinuityRelationBundle.model_fields


def test_bundle_rejects_external_context_relation() -> None:
    bundled_context = ContinuityReadabilityContextBuilder().build(
        process_id="process-1",
        source_slice_ref="slice-1",
        target_slice_ref="slice-2",
    )
    external_context = ContinuityReadabilityContextBuilder().build(
        process_id="process-1",
        source_slice_ref="slice-1",
        target_slice_ref="slice-2",
    )
    relation = ContinuityRelationRecordBuilder().build(
        continuity_context=external_context,
        source_ref="record-1",
        target_ref="record-2",
        relation_type="READABLE_ACROSS",
        readable=True,
    )

    with pytest.raises(ValueError, match="bundled ContinuityReadabilityContext"):
        ContinuityRelationBundleBuilder().build(
            continuity_context=bundled_context,
            relations=[relation],
        )


def test_assembles_explicit_continuity_records() -> None:
    request = ContinuityReadabilityAssemblyRequest(
        process_id="process-1",
        context=ContinuityReadabilityContextSpec(
            source_slice_ref="slice-1",
            target_slice_ref="slice-2",
            orientation_ref="orientation-1",
            context_refs=["context-1"],
            readability_context_refs=["readability-context-1"],
            source_record_refs=["record-1"],
            target_record_refs=["record-2"],
            continuity_readability_context_id="continuity-context-1",
        ),
        relations=[
            ContinuityRelationSpec(
                source_ref="record-1",
                target_ref="record-2",
                relation_type="READABLE_ACROSS",
                readable=True,
                continuity_state="RELATED",
                authoritative=True,
                continuity_relation_id="continuity-relation-1",
            )
        ],
        continuity_relation_bundle_id="continuity-bundle-1",
    )

    result = ContinuityReadabilityAssemblyService().assemble(request)

    assert result.context.continuity_readability_context_id == "continuity-context-1"
    assert result.context.source_slice_ref == "slice-1"
    assert result.context.target_slice_ref == "slice-2"
    assert result.relations[0].continuity_state == "RELATED"
    assert result.relations[0].authoritative is True
    assert result.bundle.continuity_relation_refs == ["continuity-relation-1"]


def test_optional_relations_may_be_empty() -> None:
    request = ContinuityReadabilityAssemblyRequest(
        process_id="process-1",
        context=ContinuityReadabilityContextSpec(
            source_slice_ref="slice-1",
            target_slice_ref="slice-2",
        ),
    )

    result = ContinuityReadabilityAssemblyService().assemble(request)

    assert result.relations == []
    assert result.bundle.continuity_relation_refs == []


def test_does_not_infer_authority_or_continuity_success() -> None:
    request = ContinuityReadabilityAssemblyRequest(
        process_id="process-1",
        context=ContinuityReadabilityContextSpec(
            source_slice_ref="slice-1",
            target_slice_ref="slice-2",
        ),
        relations=[
            ContinuityRelationSpec(
                source_ref="record-1",
                target_ref="record-2",
                relation_type="UNKNOWN_RELATION",
                readable=False,
            )
        ],
    )

    result = ContinuityReadabilityAssemblyService().assemble(request)

    assert result.relations[0].authoritative is False
    assert result.relations[0].continuity_state is None
    assert "continuity_score" not in type(result.relations[0]).model_fields
    assert "operator_response" not in type(result.relations[0]).model_fields
    assert "trajectory_edge" not in type(result.relations[0]).model_fields


def test_duplicate_relation_ids_are_rejected() -> None:
    request = ContinuityReadabilityAssemblyRequest(
        process_id="process-1",
        context=ContinuityReadabilityContextSpec(
            source_slice_ref="slice-1",
            target_slice_ref="slice-2",
        ),
        relations=[
            ContinuityRelationSpec(
                source_ref="record-1",
                target_ref="record-2",
                relation_type="A",
                readable=True,
                continuity_relation_id="duplicate",
            ),
            ContinuityRelationSpec(
                source_ref="record-2",
                target_ref="record-3",
                relation_type="B",
                readable=True,
                continuity_relation_id="duplicate",
            ),
        ],
    )

    with pytest.raises(ValueError, match="IDs must be unique"):
        ContinuityReadabilityAssemblyService().assemble(request)


def test_nested_inputs_are_copied() -> None:
    metadata = {"review": {"tags": ["explicit"]}}
    context_refs = ["context-1"]
    request = ContinuityReadabilityAssemblyRequest(
        process_id="process-1",
        context=ContinuityReadabilityContextSpec(
            source_slice_ref="slice-1",
            target_slice_ref="slice-2",
            context_refs=context_refs,
            metadata=metadata,
        ),
    )

    result = ContinuityReadabilityAssemblyService().assemble(request)
    metadata["review"]["tags"].append("mutated")
    context_refs.append("context-2")

    assert result.context.metadata == {"review": {"tags": ["explicit"]}}
    assert result.context.context_refs == ["context-1"]
