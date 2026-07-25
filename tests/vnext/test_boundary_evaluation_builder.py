from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.vnext.builders import BoundaryEvaluationBuilder
from app.vnext.models import (
    BoundaryReadabilityState,
    DifferenceObject,
    DifferenceRepresentationType,
)


def difference() -> DifferenceObject:
    return DifferenceObject(
        difference_id="difference_001",
        process_id="process_001",
        slice_ref="slice_001",
        orientation_ref="orientation_001",
        context_refs=["context_001"],
        representation_type=DifferenceRepresentationType.RELATION,
        representation={"source": "state_a", "target": "state_b"},
        defined=True,
        comparable=False,
        evaluative=False,
        source_refs=["structure_001", "articulation_001"],
    )


def test_builder_references_difference_and_preserves_explicit_evaluation() -> None:
    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference(),
        boundary_evaluation_id="boundary_evaluation_001",
        readability_state=BoundaryReadabilityState.READABLE_DISTINCTION,
        readable_as_distinction=True,
        usable_distinction=False,
        provisional=True,
        policy_ref="boundary_policy_001",
        evidence_refs=["evidence_001"],
    )

    assert evaluation.boundary_evaluation_id == "boundary_evaluation_001"
    assert evaluation.process_id == "process_001"
    assert evaluation.slice_ref == "slice_001"
    assert evaluation.difference_ref == "difference_001"
    assert evaluation.orientation_ref == "orientation_001"
    assert evaluation.context_refs == ["context_001"]
    assert evaluation.readability_state == "READABLE_DISTINCTION"
    assert evaluation.readable_as_distinction is True
    assert evaluation.usable_distinction is False
    assert evaluation.provisional is True
    assert evaluation.policy_ref == "boundary_policy_001"
    assert evaluation.evidence_refs == ["evidence_001"]


def test_builder_does_not_infer_from_difference_representation() -> None:
    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference(),
        readability_state=BoundaryReadabilityState.CANDIDATE,
        readable_as_distinction=False,
        usable_distinction=False,
    )

    assert evaluation.readability_state == "CANDIDATE"
    assert evaluation.readable_as_distinction is False
    assert evaluation.usable_distinction is False


def test_explicit_orientation_and_context_may_override_difference_defaults() -> None:
    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference(),
        readability_state=BoundaryReadabilityState.UNREADABLE,
        readable_as_distinction=False,
        usable_distinction=False,
        orientation_ref="orientation_review",
        context_refs=["context_review"],
    )

    assert evaluation.orientation_ref == "orientation_review"
    assert evaluation.context_refs == ["context_review"]


def test_expected_difference_reference_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="expected_difference_ref must match"):
        BoundaryEvaluationBuilder().build(
            difference=difference(),
            expected_difference_ref="difference_other",
            readability_state=BoundaryReadabilityState.CANDIDATE,
            readable_as_distinction=False,
            usable_distinction=False,
        )


def test_builder_preserves_boundary_model_consistency_validation() -> None:
    with pytest.raises(ValidationError, match="usable Boundary distinction requires"):
        BoundaryEvaluationBuilder().build(
            difference=difference(),
            readability_state=BoundaryReadabilityState.USABLE_BOUNDARY,
            readable_as_distinction=False,
            usable_distinction=True,
        )


def test_mutable_boundary_evaluation_inputs_are_copied() -> None:
    context_refs = ["context_001"]
    evidence_refs = ["evidence_001"]
    metadata = {"source": {"kind": "explicit"}}

    evaluation = BoundaryEvaluationBuilder().build(
        difference=difference(),
        readability_state=BoundaryReadabilityState.READABLE_DISTINCTION,
        readable_as_distinction=True,
        usable_distinction=False,
        context_refs=context_refs,
        evidence_refs=evidence_refs,
        metadata=metadata,
    )

    context_refs.append("context_002")
    evidence_refs.append("evidence_002")
    metadata["source"]["kind"] = "changed"

    assert evaluation.context_refs == ["context_001"]
    assert evaluation.evidence_refs == ["evidence_001"]
    assert evaluation.metadata == {"source": {"kind": "explicit"}}
