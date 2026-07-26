from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VNextModel(BaseModel):
    """Closed experimental model boundary for the vNext semantic PoC."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class DifferenceRepresentationType(str, Enum):
    SCALAR = "SCALAR"
    VECTOR = "VECTOR"
    TUPLE = "TUPLE"
    RELATION = "RELATION"
    CATEGORY = "CATEGORY"
    PARTIAL_ORDER = "PARTIAL_ORDER"
    SYMBOLIC = "SYMBOLIC"
    DISTRIBUTION = "DISTRIBUTION"
    FIELD = "FIELD"
    DOMAIN_DEFINED = "DOMAIN_DEFINED"


class BoundaryReadabilityState(str, Enum):
    UNREADABLE = "UNREADABLE"
    CANDIDATE = "CANDIDATE"
    READABLE_DISTINCTION = "READABLE_DISTINCTION"
    USABLE_BOUNDARY = "USABLE_BOUNDARY"


class LocalArticulation(VNextModel):
    articulation_id: str
    process_id: str
    slice_ref: str
    representation: dict[str, Any]
    readable: bool = True
    source_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadableRelation(VNextModel):
    relation_id: str
    source_ref: str
    target_ref: str | None = None
    relation_type: str
    readable: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnresolvedLocalItem(VNextModel):
    unresolved_item_id: str
    description: str
    reason: str | None = None
    related_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContinuationCondition(VNextModel):
    condition_id: str
    description: str
    satisfied: bool | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    policy_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityScene(VNextModel):
    """Runtime representation of K_n; not a scalar Stability score."""

    stability_scene_id: str
    process_id: str
    slice_ref: str
    articulation: LocalArticulation
    readable_relations: list[ReadableRelation] = Field(default_factory=list)
    unresolved_local_items: list[UnresolvedLocalItem] = Field(default_factory=list)
    continuation_conditions: list[ContinuationCondition] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityObservation(VNextModel):
    """Optional observation of a StabilityScene; it does not replace the scene."""

    stability_observation_id: str
    stability_scene_ref: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    classification: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DifferenceObject(VNextModel):
    """Slice-relative Difference without assuming distance, error, or scalar form."""

    difference_id: str
    process_id: str
    slice_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    representation_type: DifferenceRepresentationType
    representation: Any
    defined: bool = True
    comparable: bool | None = None
    evaluative: bool = False
    slice_relative: bool = True
    source_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_defined_representation(self) -> "DifferenceObject":
        if self.defined and self.representation is None:
            raise ValueError("defined DifferenceObject requires representation")
        return self


class BoundaryEvaluation(VNextModel):
    """Evaluation of whether Difference is readable and usable as a Boundary."""

    boundary_evaluation_id: str
    process_id: str
    slice_ref: str
    difference_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    readability_state: BoundaryReadabilityState
    readable_as_distinction: bool
    usable_distinction: bool
    provisional: bool = True
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_readability_consistency(self) -> "BoundaryEvaluation":
        if self.usable_distinction and not self.readable_as_distinction:
            raise ValueError(
                "usable Boundary distinction requires readable_as_distinction=true"
            )
        if (
            self.readability_state == BoundaryReadabilityState.USABLE_BOUNDARY
            and not self.usable_distinction
        ):
            raise ValueError(
                "USABLE_BOUNDARY state requires usable_distinction=true"
            )
        return self


class SemanticRealizationBundle(VNextModel):
    """Reference-only grouping of isolated vNext semantic records."""

    semantic_bundle_id: str
    process_id: str
    slice_ref: str
    stability_scene_ref: str
    stability_observation_refs: list[str] = Field(default_factory=list)
    difference_refs: list[str] = Field(default_factory=list)
    boundary_evaluation_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityObservationSpec(VNextModel):
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    classification: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    stability_observation_id: str | None = None


class DifferenceSpec(VNextModel):
    representation_type: DifferenceRepresentationType
    representation: Any
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    defined: bool = True
    comparable: bool | None = None
    evaluative: bool = False
    slice_relative: bool = True
    source_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    difference_id: str | None = None


class BoundaryEvaluationSpec(VNextModel):
    difference_ref: str
    readability_state: BoundaryReadabilityState
    readable_as_distinction: bool
    usable_distinction: bool
    provisional: bool = True
    orientation_ref: str | None = None
    context_refs: list[str] | None = None
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundary_evaluation_id: str | None = None


class SemanticAssemblyRequest(VNextModel):
    process_id: str
    slice_ref: str
    articulation: LocalArticulation
    readable_relations: list[ReadableRelation] = Field(default_factory=list)
    unresolved_local_items: list[UnresolvedLocalItem] = Field(default_factory=list)
    continuation_conditions: list[ContinuationCondition] = Field(default_factory=list)
    scene_evidence_refs: list[str] = Field(default_factory=list)
    scene_metadata: dict[str, Any] = Field(default_factory=dict)
    stability_scene_id: str | None = None
    observations: list[StabilityObservationSpec] = Field(default_factory=list)
    differences: list[DifferenceSpec] = Field(default_factory=list)
    boundary_evaluations: list[BoundaryEvaluationSpec] = Field(default_factory=list)
    bundle_metadata: dict[str, Any] = Field(default_factory=dict)
    semantic_bundle_id: str | None = None


class SemanticAssemblyResult(VNextModel):
    scene: StabilityScene
    observations: list[StabilityObservation] = Field(default_factory=list)
    differences: list[DifferenceObject] = Field(default_factory=list)
    boundary_evaluations: list[BoundaryEvaluation] = Field(default_factory=list)
    bundle: SemanticRealizationBundle


class ReadabilityContext(VNextModel):
    readability_context_id: str
    process_id: str
    slice_ref: str
    readable_item_refs: list[str] = Field(default_factory=list)
    unresolved_item_refs: list[str] = Field(default_factory=list)
    excluded_item_refs: list[str] = Field(default_factory=list)
    source_context_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncorporationRecord(VNextModel):
    incorporation_record_id: str
    process_id: str
    slice_ref: str
    before_context_ref: str
    after_context_ref: str
    incorporated_item_refs: list[str] = Field(default_factory=list)
    rejected_item_refs: list[str] = Field(default_factory=list)
    update_reason: str
    provisional: bool = True
    reversible: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_incorporation_content(self) -> "IncorporationRecord":
        overlap = set(self.incorporated_item_refs) & set(self.rejected_item_refs)
        if overlap:
            raise ValueError(
                "the same item cannot be both incorporated and rejected"
            )
        return self


class SceneReadabilityRelation(VNextModel):
    scene_readability_relation_id: str
    process_id: str
    slice_ref: str
    stability_scene_ref: str
    readability_context_ref: str
    relation_type: str
    provisional: bool = True
    authoritative: bool = False
    source_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadabilityRelationBundle(VNextModel):
    readability_relation_bundle_id: str
    process_id: str
    slice_ref: str
    readability_context_refs: list[str] = Field(default_factory=list)
    incorporation_record_refs: list[str] = Field(default_factory=list)
    scene_readability_relation_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadabilityContextSpec(VNextModel):
    readable_item_refs: list[str] = Field(default_factory=list)
    unresolved_item_refs: list[str] = Field(default_factory=list)
    excluded_item_refs: list[str] = Field(default_factory=list)
    source_context_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    readability_context_id: str | None = None


class IncorporationSpec(VNextModel):
    before_context_ref: str
    after_context_ref: str
    incorporated_item_refs: list[str] = Field(default_factory=list)
    rejected_item_refs: list[str] = Field(default_factory=list)
    update_reason: str
    provisional: bool = True
    reversible: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    incorporation_record_id: str | None = None


class SceneReadabilityRelationSpec(VNextModel):
    readability_context_ref: str
    relation_type: str
    provisional: bool = True
    authoritative: bool = False
    source_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    scene_readability_relation_id: str | None = None


class IncorporatedReadabilityAssemblyRequest(VNextModel):
    process_id: str
    slice_ref: str
    scene: StabilityScene
    contexts: list[ReadabilityContextSpec] = Field(default_factory=list)
    incorporations: list[IncorporationSpec] = Field(default_factory=list)
    scene_relations: list[SceneReadabilityRelationSpec] = Field(default_factory=list)
    bundle_metadata: dict[str, Any] = Field(default_factory=dict)
    readability_relation_bundle_id: str | None = None


class IncorporatedReadabilityAssemblyResult(VNextModel):
    scene: StabilityScene
    contexts: list[ReadabilityContext] = Field(default_factory=list)
    incorporations: list[IncorporationRecord] = Field(default_factory=list)
    scene_relations: list[SceneReadabilityRelation] = Field(default_factory=list)
    bundle: ReadabilityRelationBundle


class ContinuityReadabilityContext(VNextModel):
    continuity_readability_context_id: str
    process_id: str
    source_slice_ref: str
    target_slice_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    readability_context_refs: list[str] = Field(default_factory=list)
    source_record_refs: list[str] = Field(default_factory=list)
    target_record_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContinuityRelationRecord(VNextModel):
    continuity_relation_id: str
    process_id: str
    continuity_readability_context_ref: str
    source_ref: str
    target_ref: str
    relation_type: str
    readable: bool
    continuity_state: str | None = None
    provisional: bool = True
    authoritative: bool = False
    source_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContinuityRelationBundle(VNextModel):
    continuity_relation_bundle_id: str
    process_id: str
    continuity_readability_context_ref: str
    continuity_relation_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContinuityReadabilityContextSpec(VNextModel):
    source_slice_ref: str
    target_slice_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    readability_context_refs: list[str] = Field(default_factory=list)
    source_record_refs: list[str] = Field(default_factory=list)
    target_record_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    continuity_readability_context_id: str | None = None


class ContinuityRelationSpec(VNextModel):
    source_ref: str
    target_ref: str
    relation_type: str
    readable: bool
    continuity_state: str | None = None
    provisional: bool = True
    authoritative: bool = False
    source_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    continuity_relation_id: str | None = None


class ContinuityReadabilityAssemblyRequest(VNextModel):
    process_id: str
    context: ContinuityReadabilityContextSpec
    relations: list[ContinuityRelationSpec] = Field(default_factory=list)
    bundle_metadata: dict[str, Any] = Field(default_factory=dict)
    continuity_relation_bundle_id: str | None = None


class ContinuityReadabilityAssemblyResult(VNextModel):
    context: ContinuityReadabilityContext
    relations: list[ContinuityRelationRecord] = Field(default_factory=list)
    bundle: ContinuityRelationBundle


class TrajectoryNode(VNextModel):
    trajectory_node_id: str
    process_id: str
    record_ref: str
    record_type: str
    slice_ref: str | None = None
    node_role: str | None = None
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrajectoryEdge(VNextModel):
    trajectory_edge_id: str
    process_id: str
    source_node_ref: str
    target_node_ref: str
    edge_type: str
    relation_ref: str | None = None
    readable: bool = True
    provisional: bool = True
    authoritative: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrajectoryGraph(VNextModel):
    trajectory_graph_id: str
    process_id: str
    trajectory_node_refs: list[str] = Field(default_factory=list)
    trajectory_edge_refs: list[str] = Field(default_factory=list)
    root_node_refs: list[str] = Field(default_factory=list)
    terminal_node_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrajectoryNodeSpec(VNextModel):
    record_ref: str
    record_type: str
    slice_ref: str | None = None
    node_role: str | None = None
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    trajectory_node_id: str | None = None


class TrajectoryEdgeSpec(VNextModel):
    source_node_ref: str
    target_node_ref: str
    edge_type: str
    relation_ref: str | None = None
    readable: bool = True
    provisional: bool = True
    authoritative: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    trajectory_edge_id: str | None = None


class TrajectoryAssemblyRequest(VNextModel):
    """Explicit input specification for isolated Trajectory assembly only."""

    process_id: str
    nodes: list[TrajectoryNodeSpec] = Field(default_factory=list)
    edges: list[TrajectoryEdgeSpec] = Field(default_factory=list)
    root_node_refs: list[str] = Field(default_factory=list)
    terminal_node_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    graph_metadata: dict[str, Any] = Field(default_factory=dict)
    trajectory_graph_id: str | None = None


class TrajectoryAssemblyResult(VNextModel):
    """Complete in-memory output of one isolated Trajectory assembly operation."""

    nodes: list[TrajectoryNode] = Field(default_factory=list)
    edges: list[TrajectoryEdge] = Field(default_factory=list)
    graph: TrajectoryGraph


class RuntimeSnapshot(VNextModel):
    """Opaque read-only snapshot of one existing Runtime result payload."""

    runtime_snapshot_id: str
    process_id: str
    slice_ref: str
    runtime_contract: str
    payload: dict[str, Any]
    captured_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeProjectionReference(VNextModel):
    """Explicit reference relation between a Runtime snapshot and one vNext record."""

    projection_reference_id: str
    process_id: str
    runtime_snapshot_ref: str
    record_ref: str
    record_type: str
    relation_type: str
    provisional: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadOnlyRuntimeProjection(VNextModel):
    """Reference-only grouping for one Runtime snapshot projection."""

    runtime_projection_id: str
    process_id: str
    runtime_snapshot_ref: str
    projection_reference_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeSnapshotSpec(VNextModel):
    slice_ref: str
    runtime_contract: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    runtime_snapshot_id: str | None = None


class RuntimeProjectionReferenceSpec(VNextModel):
    record_ref: str
    record_type: str
    relation_type: str
    provisional: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    projection_reference_id: str | None = None


class ReadOnlyRuntimeProjectionRequest(VNextModel):
    """Explicit input specification for isolated read-only Runtime projection."""

    process_id: str
    snapshot: RuntimeSnapshotSpec
    references: list[RuntimeProjectionReferenceSpec] = Field(default_factory=list)
    provisional: bool = True
    projection_metadata: dict[str, Any] = Field(default_factory=dict)
    runtime_projection_id: str | None = None


class ReadOnlyRuntimeProjectionResult(VNextModel):
    """Complete in-memory output of one isolated Runtime projection operation."""

    snapshot: RuntimeSnapshot
    references: list[RuntimeProjectionReference] = Field(default_factory=list)
    projection: ReadOnlyRuntimeProjection


class ExperimentalRecordEnvelope(VNextModel):
    """Opaque experimental persistence envelope for one vNext record payload.

    The envelope does not establish canonical authority, reconstruct a typed
    record, select a current record, or define ordering semantics.
    """

    record_id: str
    process_id: str
    record_type: str
    payload: dict[str, Any]
    source_ref: str | None = None
    provisional: bool = True
    stored_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)
