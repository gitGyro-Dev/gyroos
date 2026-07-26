from __future__ import annotations

import pytest

from app.vnext.builders import (
    ReadOnlyRuntimeProjectionBuilder,
    RuntimeProjectionReferenceBuilder,
    RuntimeSnapshotBuilder,
)
from app.vnext.models import (
    ReadOnlyRuntimeProjection,
    ReadOnlyRuntimeProjectionRequest,
    RuntimeProjectionReferenceSpec,
    RuntimeSnapshotSpec,
)
from app.vnext.runtime_projection import ReadOnlyRuntimeProjectionService


def test_runtime_snapshot_preserves_opaque_payload_without_interpretation() -> None:
    payload = {
        "stability": 0.92,
        "operator_response": "Continue",
        "history": {"stability": [0.89, 0.90, 0.92]},
    }

    snapshot = RuntimeSnapshotBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        runtime_contract="loop-step-v1",
        payload=payload,
        runtime_snapshot_id="snapshot-1",
    )

    payload["history"]["stability"].append(0.1)

    assert snapshot.payload == {
        "stability": 0.92,
        "operator_response": "Continue",
        "history": {"stability": [0.89, 0.90, 0.92]},
    }


def test_projection_reference_keeps_explicit_relation_only() -> None:
    snapshot = RuntimeSnapshotBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        runtime_contract="loop-step-v1",
        payload={"operator_response": "Continue"},
        runtime_snapshot_id="snapshot-1",
    )

    reference = RuntimeProjectionReferenceBuilder().build(
        snapshot=snapshot,
        record_ref="scene-1",
        record_type="StabilityScene",
        relation_type="OBSERVED_WITH",
        provisional=False,
        projection_reference_id="reference-1",
    )

    assert reference.runtime_snapshot_ref == "snapshot-1"
    assert reference.record_ref == "scene-1"
    assert reference.record_type == "StabilityScene"
    assert reference.relation_type == "OBSERVED_WITH"
    assert reference.provisional is False


def test_projection_builder_stores_references_only() -> None:
    snapshot = RuntimeSnapshotBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        runtime_contract="loop-step-v1",
        payload={},
        runtime_snapshot_id="snapshot-1",
    )
    reference = RuntimeProjectionReferenceBuilder().build(
        snapshot=snapshot,
        record_ref="trajectory-1",
        record_type="TrajectoryGraph",
        relation_type="PROJECTS_TO",
        projection_reference_id="reference-1",
    )

    projection = ReadOnlyRuntimeProjectionBuilder().build(
        snapshot=snapshot,
        references=[reference],
        runtime_projection_id="projection-1",
    )

    assert projection.runtime_snapshot_ref == "snapshot-1"
    assert projection.projection_reference_refs == ["reference-1"]
    assert "runtime_payload" not in ReadOnlyRuntimeProjection.model_fields
    assert "records" not in ReadOnlyRuntimeProjection.model_fields
    assert "operator_response" not in ReadOnlyRuntimeProjection.model_fields


def test_projection_builder_rejects_external_snapshot_reference() -> None:
    snapshot = RuntimeSnapshotBuilder().build(
        process_id="process-1",
        slice_ref="slice-1",
        runtime_contract="loop-step-v1",
        payload={},
        runtime_snapshot_id="snapshot-1",
    )
    other_snapshot = RuntimeSnapshotBuilder().build(
        process_id="process-1",
        slice_ref="slice-2",
        runtime_contract="loop-step-v1",
        payload={},
        runtime_snapshot_id="snapshot-2",
    )
    reference = RuntimeProjectionReferenceBuilder().build(
        snapshot=other_snapshot,
        record_ref="scene-1",
        record_type="StabilityScene",
        relation_type="OBSERVED_WITH",
    )

    with pytest.raises(ValueError, match="projected RuntimeSnapshot"):
        ReadOnlyRuntimeProjectionBuilder().build(
            snapshot=snapshot,
            references=[reference],
        )


def test_service_assembles_snapshot_references_and_projection() -> None:
    request = ReadOnlyRuntimeProjectionRequest(
        process_id="process-1",
        snapshot=RuntimeSnapshotSpec(
            slice_ref="slice-1",
            runtime_contract="loop-step-v1",
            payload={
                "stability": 0.92,
                "operator_response": "Continue",
            },
            runtime_snapshot_id="snapshot-1",
        ),
        references=[
            RuntimeProjectionReferenceSpec(
                record_ref="scene-1",
                record_type="StabilityScene",
                relation_type="OBSERVED_WITH",
                projection_reference_id="reference-1",
            ),
            RuntimeProjectionReferenceSpec(
                record_ref="trajectory-1",
                record_type="TrajectoryGraph",
                relation_type="PROJECTS_TO",
                projection_reference_id="reference-2",
            ),
        ],
        provisional=False,
        runtime_projection_id="projection-1",
    )

    result = ReadOnlyRuntimeProjectionService().project(request)

    assert result.snapshot.runtime_snapshot_id == "snapshot-1"
    assert [item.projection_reference_id for item in result.references] == [
        "reference-1",
        "reference-2",
    ]
    assert result.projection.runtime_projection_id == "projection-1"
    assert result.projection.projection_reference_refs == [
        "reference-1",
        "reference-2",
    ]
    assert result.projection.provisional is False


def test_service_allows_projection_without_record_references() -> None:
    result = ReadOnlyRuntimeProjectionService().project(
        ReadOnlyRuntimeProjectionRequest(
            process_id="process-1",
            snapshot=RuntimeSnapshotSpec(
                slice_ref="slice-1",
                runtime_contract="loop-step-v1",
                payload={},
            ),
        )
    )

    assert result.references == []
    assert result.projection.projection_reference_refs == []


def test_service_rejects_duplicate_projection_reference_ids() -> None:
    request = ReadOnlyRuntimeProjectionRequest(
        process_id="process-1",
        snapshot=RuntimeSnapshotSpec(
            slice_ref="slice-1",
            runtime_contract="loop-step-v1",
            payload={},
        ),
        references=[
            RuntimeProjectionReferenceSpec(
                record_ref="scene-1",
                record_type="StabilityScene",
                relation_type="OBSERVED_WITH",
                projection_reference_id="reference-duplicate",
            ),
            RuntimeProjectionReferenceSpec(
                record_ref="graph-1",
                record_type="TrajectoryGraph",
                relation_type="PROJECTS_TO",
                projection_reference_id="reference-duplicate",
            ),
        ],
    )

    with pytest.raises(ValueError, match="unique within one request"):
        ReadOnlyRuntimeProjectionService().project(request)


def test_service_does_not_infer_runtime_or_vnext_semantics() -> None:
    result = ReadOnlyRuntimeProjectionService().project(
        ReadOnlyRuntimeProjectionRequest(
            process_id="process-1",
            snapshot=RuntimeSnapshotSpec(
                slice_ref="slice-1",
                runtime_contract="loop-step-v1",
                payload={
                    "stability": 0.92,
                    "operator_response": "Continue",
                    "history": ["Continue"],
                },
            ),
        )
    )

    assert result.references == []
    assert "stability_scene_ref" not in result.projection.model_fields
    assert "trajectory_graph_ref" not in result.projection.model_fields
    assert "next_action" not in result.projection.model_fields


def test_service_copies_nested_request_inputs() -> None:
    payload = {"history": {"responses": ["Continue"]}}
    metadata = {"source": {"labels": ["runtime"]}}

    request = ReadOnlyRuntimeProjectionRequest(
        process_id="process-1",
        snapshot=RuntimeSnapshotSpec(
            slice_ref="slice-1",
            runtime_contract="loop-step-v1",
            payload=payload,
            metadata=metadata,
        ),
        projection_metadata=metadata,
    )

    result = ReadOnlyRuntimeProjectionService().project(request)
    payload["history"]["responses"].append("Stop")
    metadata["source"]["labels"].append("mutated")

    assert result.snapshot.payload == {"history": {"responses": ["Continue"]}}
    assert result.snapshot.metadata == {"source": {"labels": ["runtime"]}}
    assert result.projection.metadata == {"source": {"labels": ["runtime"]}}
