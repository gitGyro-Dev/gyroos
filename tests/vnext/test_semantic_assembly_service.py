from __future__ import annotations

import pytest

from app.vnext.assembly import SemanticAssemblyService
from app.vnext.models import (
    BoundaryEvaluationSpec,
    BoundaryReadabilityState,
    DifferenceRepresentationType,
    DifferenceSpec,
    LocalArticulation,
    SemanticAssemblyRequest,
    StabilityObservationSpec,
)


def request_with_all_records() -> SemanticAssemblyRequest:
    return SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={"state": "readable"},
        ),
        stability_scene_id="scene_001",
        observations=[
            StabilityObservationSpec(
                stability_observation_id="observation_001",
                score=0.92,
                classification="STABLE",
            )
        ],
        differences=[
            DifferenceSpec(
                difference_id="difference_001",
                representation_type=DifferenceRepresentationType.RELATION,
                representation={"from": "a", "to": "b", "relation": "changed"},
                orientation_ref="orientation_001",
                context_refs=["context_001"],
            )
        ],
        boundary_evaluations=[
            BoundaryEvaluationSpec(
                boundary_evaluation_id="boundary_eval_001",
                difference_ref="difference_001",
                readability_state=BoundaryReadabilityState.READABLE_DISTINCTION,
                readable_as_distinction=True,
                usable_distinction=False,
            )
        ],
        semantic_bundle_id="bundle_001",
    )


def test_service_assembles_existing_builders_into_one_reference_bundle() -> None:
    result = SemanticAssemblyService().assemble(request_with_all_records())

    assert result.scene.stability_scene_id == "scene_001"
    assert [item.stability_observation_id for item in result.observations] == [
        "observation_001"
    ]
    assert [item.difference_id for item in result.differences] == ["difference_001"]
    assert [item.boundary_evaluation_id for item in result.boundary_evaluations] == [
        "boundary_eval_001"
    ]
    assert result.bundle.semantic_bundle_id == "bundle_001"
    assert result.bundle.stability_scene_ref == "scene_001"
    assert result.bundle.stability_observation_refs == ["observation_001"]
    assert result.bundle.difference_refs == ["difference_001"]
    assert result.bundle.boundary_evaluation_refs == ["boundary_eval_001"]


def test_service_allows_explicit_scene_without_optional_records() -> None:
    request = SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={"state": "readable"},
        ),
    )

    result = SemanticAssemblyService().assemble(request)

    assert result.observations == []
    assert result.differences == []
    assert result.boundary_evaluations == []
    assert result.bundle.stability_observation_refs == []
    assert result.bundle.difference_refs == []
    assert result.bundle.boundary_evaluation_refs == []


def test_service_does_not_infer_stability_observation_from_scene_content() -> None:
    request = SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={"stability": 0.99},
        ),
        observations=[StabilityObservationSpec()],
    )

    result = SemanticAssemblyService().assemble(request)

    assert result.observations[0].score is None
    assert result.observations[0].classification is None


def test_service_preserves_explicit_undefined_difference() -> None:
    request = SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={},
        ),
        differences=[
            DifferenceSpec(
                difference_id="difference_undefined",
                representation_type=DifferenceRepresentationType.SYMBOLIC,
                representation=None,
                defined=False,
            )
        ],
    )

    result = SemanticAssemblyService().assemble(request)

    difference = result.differences[0]
    assert difference.defined is False
    assert difference.representation is None


def test_service_rejects_boundary_spec_outside_assembled_differences() -> None:
    request = SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={},
        ),
        boundary_evaluations=[
            BoundaryEvaluationSpec(
                difference_ref="difference_missing",
                readability_state=BoundaryReadabilityState.CANDIDATE,
                readable_as_distinction=False,
                usable_distinction=False,
            )
        ],
    )

    with pytest.raises(ValueError, match="assembled in the same request"):
        SemanticAssemblyService().assemble(request)


def test_service_copies_nested_request_inputs() -> None:
    representation = {"relation": {"kind": "explicit"}}
    difference_metadata = {"source": {"kind": "caller"}}
    bundle_metadata = {"assembly": {"version": 1}}
    request = SemanticAssemblyRequest(
        process_id="process_001",
        slice_ref="slice_001",
        articulation=LocalArticulation(
            articulation_id="articulation_001",
            process_id="process_001",
            slice_ref="slice_001",
            representation={},
        ),
        differences=[
            DifferenceSpec(
                difference_id="difference_001",
                representation_type=DifferenceRepresentationType.RELATION,
                representation=representation,
                metadata=difference_metadata,
            )
        ],
        bundle_metadata=bundle_metadata,
    )

    result = SemanticAssemblyService().assemble(request)

    representation["relation"]["kind"] = "changed"
    difference_metadata["source"]["kind"] = "changed"
    bundle_metadata["assembly"]["version"] = 2

    assert result.differences[0].representation == {
        "relation": {"kind": "explicit"}
    }
    assert result.differences[0].metadata == {"source": {"kind": "caller"}}
    assert result.bundle.metadata == {"assembly": {"version": 1}}
