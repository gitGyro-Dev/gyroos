from __future__ import annotations

import pytest

from app.vnext.builders import IncorporationRecordBuilder, ReadabilityContextBuilder
from app.vnext.models import IncorporationRecord, ReadabilityContext


def build_context(
    context_id: str,
    *,
    process_id: str = "process_001",
    slice_ref: str = "slice_001",
    readable_item_refs: list[str] | None = None,
) -> ReadabilityContext:
    return ReadabilityContextBuilder().build(
        readability_context_id=context_id,
        process_id=process_id,
        slice_ref=slice_ref,
        readable_item_refs=readable_item_refs,
    )


def test_readability_context_records_explicit_current_readability_only() -> None:
    context = ReadabilityContextBuilder().build(
        readability_context_id="context_before",
        process_id="process_001",
        slice_ref="slice_001",
        readable_item_refs=["relation_001"],
        unresolved_item_refs=["unresolved_001"],
        excluded_item_refs=["candidate_001"],
        source_context_refs=["context_seed"],
        provisional=True,
        metadata={"source": "explicit"},
    )

    assert context.readable_item_refs == ["relation_001"]
    assert context.unresolved_item_refs == ["unresolved_001"]
    assert context.excluded_item_refs == ["candidate_001"]
    assert context.source_context_refs == ["context_seed"]
    assert "history" not in ReadabilityContext.model_fields
    assert "events" not in ReadabilityContext.model_fields
    assert "learned_state" not in ReadabilityContext.model_fields


def test_incorporation_record_references_distinct_before_and_after_contexts() -> None:
    before = build_context("context_before", readable_item_refs=["relation_001"])
    after = build_context(
        "context_after",
        readable_item_refs=["relation_001", "relation_002"],
    )

    record = IncorporationRecordBuilder().build(
        incorporation_record_id="incorporation_001",
        before_context=before,
        after_context=after,
        incorporated_item_refs=["relation_002"],
        rejected_item_refs=["candidate_003"],
        update_reason="Explicit review accepted relation_002.",
        provisional=True,
        reversible=True,
        evidence_refs=["evidence_001"],
        metadata={"review": {"kind": "manual"}},
    )

    assert record.before_context_ref == "context_before"
    assert record.after_context_ref == "context_after"
    assert record.incorporated_item_refs == ["relation_002"]
    assert record.rejected_item_refs == ["candidate_003"]
    assert record.update_reason == "Explicit review accepted relation_002."
    assert "rollback_applied" not in IncorporationRecord.model_fields
    assert "learning_result" not in IncorporationRecord.model_fields


def test_builder_does_not_infer_context_difference() -> None:
    before = build_context("context_before", readable_item_refs=["relation_001"])
    after = build_context(
        "context_after",
        readable_item_refs=["relation_001", "relation_002"],
    )

    record = IncorporationRecordBuilder().build(
        before_context=before,
        after_context=after,
        incorporated_item_refs=[],
        rejected_item_refs=[],
        update_reason="No incorporation decision was supplied.",
    )

    assert record.incorporated_item_refs == []
    assert record.rejected_item_refs == []


def test_same_item_cannot_be_incorporated_and_rejected() -> None:
    before = build_context("context_before")
    after = build_context("context_after")

    with pytest.raises(ValueError, match="both incorporated and rejected"):
        IncorporationRecordBuilder().build(
            before_context=before,
            after_context=after,
            incorporated_item_refs=["item_001"],
            rejected_item_refs=["item_001"],
            update_reason="Conflicting explicit input.",
        )


def test_before_and_after_context_references_must_be_distinct() -> None:
    context = build_context("context_same")

    with pytest.raises(ValueError, match="must be distinct"):
        IncorporationRecordBuilder().build(
            before_context=context,
            after_context=context,
            update_reason="Invalid self-reference.",
        )


def test_context_scope_mismatch_is_rejected() -> None:
    before = build_context("context_before")
    after_process = build_context("context_after", process_id="process_other")
    after_slice = build_context("context_after_2", slice_ref="slice_other")

    with pytest.raises(ValueError, match="process_id values must match"):
        IncorporationRecordBuilder().build(
            before_context=before,
            after_context=after_process,
            update_reason="Invalid process scope.",
        )

    with pytest.raises(ValueError, match="slice_ref values must match"):
        IncorporationRecordBuilder().build(
            before_context=before,
            after_context=after_slice,
            update_reason="Invalid slice scope.",
        )


def test_expected_context_reference_mismatch_is_rejected() -> None:
    before = build_context("context_before")
    after = build_context("context_after")

    with pytest.raises(ValueError, match="expected_before_context_ref"):
        IncorporationRecordBuilder().build(
            before_context=before,
            after_context=after,
            expected_before_context_ref="context_other",
            update_reason="Reference check.",
        )

    with pytest.raises(ValueError, match="expected_after_context_ref"):
        IncorporationRecordBuilder().build(
            before_context=before,
            after_context=after,
            expected_after_context_ref="context_other",
            update_reason="Reference check.",
        )


def test_mutable_inputs_are_copied() -> None:
    readable = ["relation_001"]
    metadata = {"source": {"kind": "explicit"}}

    context = ReadabilityContextBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        readable_item_refs=readable,
        metadata=metadata,
    )

    readable.append("relation_002")
    metadata["source"]["kind"] = "changed"

    assert context.readable_item_refs == ["relation_001"]
    assert context.metadata == {"source": {"kind": "explicit"}}

    before = build_context("context_before")
    after = build_context("context_after")
    incorporated = ["item_001"]
    record_metadata = {"review": {"kind": "explicit"}}

    record = IncorporationRecordBuilder().build(
        before_context=before,
        after_context=after,
        incorporated_item_refs=incorporated,
        update_reason="Explicit update.",
        metadata=record_metadata,
    )

    incorporated.append("item_002")
    record_metadata["review"]["kind"] = "changed"

    assert record.incorporated_item_refs == ["item_001"]
    assert record.metadata == {"review": {"kind": "explicit"}}
