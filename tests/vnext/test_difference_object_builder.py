from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.vnext.builders import DifferenceObjectBuilder
from app.vnext.models import DifferenceRepresentationType


def test_builder_constructs_difference_from_explicit_representation() -> None:
    difference = DifferenceObjectBuilder().build(
        difference_id="difference_001",
        process_id="process_001",
        slice_ref="slice_001",
        orientation_ref="orientation_001",
        context_refs=["context_001"],
        representation_type=DifferenceRepresentationType.RELATION,
        representation={"left": "state_a", "right": "state_b", "relation": "changed"},
        defined=True,
        comparable=False,
        evaluative=False,
        slice_relative=True,
        source_refs=["articulation_001"],
        metadata={"source": "explicit"},
    )

    assert difference.difference_id == "difference_001"
    assert difference.process_id == "process_001"
    assert difference.slice_ref == "slice_001"
    assert difference.orientation_ref == "orientation_001"
    assert difference.context_refs == ["context_001"]
    assert difference.representation_type == "RELATION"
    assert difference.representation == {
        "left": "state_a",
        "right": "state_b",
        "relation": "changed",
    }
    assert difference.comparable is False
    assert difference.evaluative is False
    assert difference.source_refs == ["articulation_001"]


def test_builder_allows_undefined_difference_without_representation() -> None:
    difference = DifferenceObjectBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        representation_type=DifferenceRepresentationType.DOMAIN_DEFINED,
        representation=None,
        defined=False,
    )

    assert difference.defined is False
    assert difference.representation is None


def test_builder_preserves_model_validation_for_defined_difference() -> None:
    with pytest.raises(ValidationError, match="requires representation"):
        DifferenceObjectBuilder().build(
            process_id="process_001",
            slice_ref="slice_001",
            representation_type=DifferenceRepresentationType.DOMAIN_DEFINED,
            representation=None,
            defined=True,
        )


def test_builder_does_not_convert_relation_to_numeric_value() -> None:
    representation = {
        "relation_type": "NON_METRIC_DIFFERENCE",
        "members": ["a", "b"],
    }

    difference = DifferenceObjectBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        representation_type=DifferenceRepresentationType.RELATION,
        representation=representation,
    )

    assert difference.representation == representation
    assert not isinstance(difference.representation, (int, float))


def test_builder_deep_copies_mutable_inputs() -> None:
    representation = {"relation": {"kind": "explicit"}}
    context_refs = ["context_001"]
    source_refs = ["source_001"]
    metadata = {"source": {"kind": "explicit"}}

    difference = DifferenceObjectBuilder().build(
        process_id="process_001",
        slice_ref="slice_001",
        representation_type=DifferenceRepresentationType.RELATION,
        representation=representation,
        context_refs=context_refs,
        source_refs=source_refs,
        metadata=metadata,
    )

    representation["relation"]["kind"] = "changed"
    context_refs.append("context_002")
    source_refs.append("source_002")
    metadata["source"]["kind"] = "changed"

    assert difference.representation == {"relation": {"kind": "explicit"}}
    assert difference.context_refs == ["context_001"]
    assert difference.source_refs == ["source_001"]
    assert difference.metadata == {"source": {"kind": "explicit"}}
