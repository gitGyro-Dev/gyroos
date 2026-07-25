from __future__ import annotations

import pytest

from app.vnext.builders import (
    ContinuityReadabilityContextBuilder,
    ContinuityRelationRecordBuilder,
)
from app.vnext.models import (
    ContinuityReadabilityContext,
    ContinuityRelationRecord,
)


def make_context() -> ContinuityReadabilityContext:
    return ContinuityReadabilityContextBuilder().build(
        process_id="process-1",
        source_slice_ref="slice-1",
        target_slice_ref="slice-2",
        orientation_ref="orientation-1",
        context_refs=["context-1"],
        readability_context_refs=["readability-context-1"],
        source_record_refs=["scene-1"],
        target_record_refs=["scene-2"],
        provisional=True,
        continuity_readability_context_id="continuity-context-1",
    )


def test_context_preserves_explicit_scope_without_evaluation() -> None:
    context = make_context()

    assert context.process_id == "process-1"
    assert context.source_slice_ref == "slice-1"
    assert context.target_slice_ref == "slice-2"
    assert context.orientation_ref == "orientation-1"
    assert context.context_refs == ["context-1"]
    assert context.readability_context_refs == ["readability-context-1"]
    assert context.source_record_refs == ["scene-1"]
    assert context.target_record_refs == ["scene-2"]
    assert "score" not in ContinuityReadabilityContext.model_fields
    assert "operator_response" not in ContinuityReadabilityContext.model_fields
    assert "identity_ref" not in ContinuityReadabilityContext.model_fields
    assert "trajectory_ref" not in ContinuityReadabilityContext.model_fields


def test_relation_preserves_explicit_statement() -> None:
    relation = ContinuityRelationRecordBuilder().build(
        continuity_context=make_context(),
        source_ref="scene-1",
        target_ref="scene-2",
        relation_type="READABLE_ACROSS",
        readable=True,
        continuity_state="LEGIBLE_RELATION",
        provisional=False,
        authoritative=True,
        source_refs=["source-1"],
        evidence_refs=["evidence-1"],
        continuity_relation_id="continuity-relation-1",
    )

    assert relation.continuity_relation_id == "continuity-relation-1"
    assert relation.process_id == "process-1"
    assert relation.continuity_readability_context_ref == "continuity-context-1"
    assert relation.source_ref == "scene-1"
    assert relation.target_ref == "scene-2"
    assert relation.relation_type == "READABLE_ACROSS"
    assert relation.readable is True
    assert relation.continuity_state == "LEGIBLE_RELATION"
    assert relation.provisional is False
    assert relation.authoritative is True


def test_relation_does_not_infer_continuity_or_authority() -> None:
    relation = ContinuityRelationRecordBuilder().build(
        continuity_context=make_context(),
        source_ref="record-a",
        target_ref="record-b",
        relation_type="UNRESOLVED_RELATION",
        readable=False,
    )

    assert relation.readable is False
    assert relation.continuity_state is None
    assert relation.provisional is True
    assert relation.authoritative is False
    assert "continuity_score" not in ContinuityRelationRecord.model_fields
    assert "operator_response" not in ContinuityRelationRecord.model_fields
    assert "identity_continuity" not in ContinuityRelationRecord.model_fields
    assert "trajectory_edge" not in ContinuityRelationRecord.model_fields


def test_expected_context_ref_is_validated() -> None:
    with pytest.raises(ValueError, match="expected_context_ref"):
        ContinuityRelationRecordBuilder().build(
            continuity_context=make_context(),
            source_ref="scene-1",
            target_ref="scene-2",
            relation_type="READABLE_ACROSS",
            readable=True,
            expected_context_ref="other-context",
        )


def test_expected_process_id_is_validated() -> None:
    with pytest.raises(ValueError, match="expected_process_id"):
        ContinuityRelationRecordBuilder().build(
            continuity_context=make_context(),
            source_ref="scene-1",
            target_ref="scene-2",
            relation_type="READABLE_ACROSS",
            readable=True,
            expected_process_id="other-process",
        )


def test_mutable_inputs_are_copied() -> None:
    context_refs = ["context-1"]
    readability_refs = ["readability-context-1"]
    source_record_refs = ["scene-1"]
    target_record_refs = ["scene-2"]
    context_metadata = {"review": {"tags": ["explicit"]}}

    context = ContinuityReadabilityContextBuilder().build(
        process_id="process-1",
        source_slice_ref="slice-1",
        target_slice_ref="slice-2",
        context_refs=context_refs,
        readability_context_refs=readability_refs,
        source_record_refs=source_record_refs,
        target_record_refs=target_record_refs,
        metadata=context_metadata,
    )

    source_refs = ["source-1"]
    evidence_refs = ["evidence-1"]
    relation_metadata = {"review": {"tags": ["statement"]}}
    relation = ContinuityRelationRecordBuilder().build(
        continuity_context=context,
        source_ref="scene-1",
        target_ref="scene-2",
        relation_type="READABLE_ACROSS",
        readable=True,
        source_refs=source_refs,
        evidence_refs=evidence_refs,
        metadata=relation_metadata,
    )

    context_refs.append("mutated")
    readability_refs.append("mutated")
    source_record_refs.append("mutated")
    target_record_refs.append("mutated")
    context_metadata["review"]["tags"].append("mutated")
    source_refs.append("mutated")
    evidence_refs.append("mutated")
    relation_metadata["review"]["tags"].append("mutated")

    assert context.context_refs == ["context-1"]
    assert context.readability_context_refs == ["readability-context-1"]
    assert context.source_record_refs == ["scene-1"]
    assert context.target_record_refs == ["scene-2"]
    assert context.metadata == {"review": {"tags": ["explicit"]}}
    assert relation.source_refs == ["source-1"]
    assert relation.evidence_refs == ["evidence-1"]
    assert relation.metadata == {"review": {"tags": ["statement"]}}
