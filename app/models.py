from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class SliceMode(str, Enum):
    SLICE = "SLICE"
    RESLICE = "RESLICE"


class SliceSourceType(str, Enum):
    RUNTIME_STRUCTURE = "RUNTIME_STRUCTURE"
    CONTEXT_EVIDENCE = "CONTEXT_EVIDENCE"
    BOUNDARY_EVIDENCE = "BOUNDARY_EVIDENCE"
    BOUNDARY_STATE_RECORD = "BOUNDARY_STATE_RECORD"
    VOID_EVIDENCE = "VOID_EVIDENCE"
    PROCESS_RESULT = "PROCESS_RESULT"


class StabilityStatus(str, Enum):
    STABLE = "STABLE"
    ADAPTIVE = "ADAPTIVE"
    UNSTABLE = "UNSTABLE"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    VOID_RELATED = "VOID_RELATED"
    UNKNOWN = "UNKNOWN"


class OperatorResponseType(str, Enum):
    CONTINUE = "CONTINUE"
    ADJUST = "ADJUST"
    RESLICE = "RESLICE"
    JUMP = "JUMP"
    DEFER = "DEFER"
    STOP = "STOP"


class RuntimeContinuityType(str, Enum):
    DIRECT_CONNECTION = "DIRECT_CONNECTION"
    ADJUSTED_CONNECTION = "ADJUSTED_CONNECTION"
    RESLICE_CONNECTION = "RESLICE_CONNECTION"
    JUMP_RECONNECTION = "JUMP_RECONNECTION"
    DEFERRED_PENDING_RELATION = "DEFERRED_PENDING_RELATION"
    STOPPED_FOR_CURRENT_SCOPE = "STOPPED_FOR_CURRENT_SCOPE"


class BoundaryStateType(str, Enum):
    NORMAL = "NORMAL"
    UNKNOWN = "UNKNOWN"
    VOID = "VOID"
    CONFLICTING = "CONFLICTING"


class StructureInput(CanonicalModel):
    structure_id: str
    current_mode: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorOrientation(CanonicalModel):
    orientation_id: str
    operator_ref: str | None = None
    intent: str | None = None
    focus: list[str] = Field(default_factory=list)
    criteria: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SlicePolicy(CanonicalModel):
    policy_id: str
    policy_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SliceRequest(CanonicalModel):
    mode: SliceMode
    source_type: SliceSourceType
    source_ref: str
    orientation: OperatorOrientation
    slice_policy: SlicePolicy
    context_refs: list[str] = Field(default_factory=list)
    boundary_refs: list[str] = Field(default_factory=list)
    boundary_state_refs: list[str] = Field(default_factory=list)
    void_refs: list[str] = Field(default_factory=list)
    parent_process_ref: str | None = None
    parent_slice_ref: str | None = None
    trajectory_ref: str | None = None
    requested_by_response_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_mode(self) -> "SliceRequest":
        if self.mode == SliceMode.RESLICE:
            if not self.parent_process_ref or not self.parent_slice_ref:
                raise ValueError("RESLICE requires parent_process_ref and parent_slice_ref")
            if not self.requested_by_response_ref:
                raise ValueError("RESLICE requires requested_by_response_ref")
        return self


class RuntimeLimits(CanonicalModel):
    max_slice_operations: int = Field(default=1, ge=1, le=1)


class LoopStepRequest(CanonicalModel):
    request_id: str
    loop_id: str
    idempotency_key: str | None = None
    structure: StructureInput
    slice_request: SliceRequest
    runtime_limits: RuntimeLimits = Field(default_factory=RuntimeLimits)
    expected_current_scope_ref: str | None = None
    previous_state_ref: str | None = None
    policy_ref: str | None = None
    client_trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SliceReadability(CanonicalModel):
    representation_readable: bool
    deviation_readable: bool
    boundary_readability: float | None = Field(default=None, ge=0.0, le=1.0)
    target_relation_readability: float | None = Field(default=None, ge=0.0, le=1.0)
    unreadable_aspects: list[str] = Field(default_factory=list)
    reason: str | None = None


class BoundaryEvidence(CanonicalModel):
    boundary_evidence_id: str
    slice_id: str
    process_id: str
    relation_ref: str
    distinction_type: str
    boundary_readability: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BoundaryStateRecord(CanonicalModel):
    boundary_state_record_id: str
    slice_id: str
    process_id: str
    boundary_ref: str
    relation_ref: str
    state_type: BoundaryStateType
    boundary_state_confidence: float = Field(ge=0.0, le=1.0)
    classification_reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextEvidence(CanonicalModel):
    context_evidence_id: str
    slice_id: str
    process_id: str
    relation_ref: str
    source_type: str
    content: dict[str, Any]
    context_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoidEvidence(CanonicalModel):
    void_evidence_id: str
    slice_id: str
    process_id: str
    boundary_ref: str
    relation_ref: str
    reason: str
    target_relation_readability: float = Field(ge=0.0, le=1.0)
    connectability: float = Field(ge=0.0, le=1.0)
    supporting_evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SliceDone(CanonicalModel):
    slice_id: str
    process_id: str
    structure_ref: str
    representation: dict[str, Any]
    deviation: dict[str, Any]
    readability: SliceReadability
    boundary_evidence: list[BoundaryEvidence] = Field(default_factory=list)
    boundary_state_records: list[BoundaryStateRecord] = Field(default_factory=list)
    context_evidence: list[ContextEvidence] = Field(default_factory=list)
    void_evidence: list[VoidEvidence] = Field(default_factory=list)
    boundary_refs: list[str] = Field(default_factory=list)
    boundary_state_refs: list[str] = Field(default_factory=list)
    context_refs: list[str] = Field(default_factory=list)
    void_refs: list[str] = Field(default_factory=list)
    orientation_ref: str
    slice_policy_ref: str
    trajectory_ref: str | None = None
    parent_process_ref: str | None = None
    parent_slice_ref: str | None = None
    source_type: SliceSourceType
    source_ref: str
    completed_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityResult(CanonicalModel):
    stability_result_id: str
    process_id: str
    slice_id: str
    value: float | None = Field(default=None, ge=0.0, le=1.0)
    status: StabilityStatus
    continuability: bool | None = None
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    evaluation_policy_ref: str | None = None
    evaluated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorResponse(CanonicalModel):
    operator_response_id: str
    process_id: str
    slice_id: str
    stability_result_ref: str
    response_type: OperatorResponseType
    reason: str
    response_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    considered_evidence_refs: list[str] = Field(default_factory=list)
    decisive_evidence_refs: list[str] = Field(default_factory=list)
    next_request: SliceRequest | None = None
    selected_by_policy_ref: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeContinuityResult(CanonicalModel):
    continuity_result_id: str
    process_id: str
    operator_response_ref: str
    continuity_type: RuntimeContinuityType
    connected: bool
    pending: bool
    terminated_for_current_scope: bool
    source_ref: str
    target_ref: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeferredRelationRecord(CanonicalModel):
    deferred_relation_record_id: str
    process_id: str
    operator_response_ref: str
    continuity_result_ref: str
    relation_ref: str
    pending: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrajectoryEdge(CanonicalModel):
    trajectory_edge_id: str
    process_id: str
    operator_response_ref: str
    continuity_result_ref: str
    edge_type: RuntimeContinuityType
    relation_ref: str
    source_ref: str
    target_ref: str | None = None
    parent_process_ref: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LoopStepResult(CanonicalModel):
    process_id: str
    request_id: str
    loop_id: str
    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    continuity: RuntimeContinuityResult
    deferred_relation_record: DeferredRelationRecord | None = None
    trajectory_edges: list[TrajectoryEdge] = Field(default_factory=list)
    created_record_refs: list[str] = Field(default_factory=list)
    replayed: bool = False
    completed_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CurrentScopeState(CanonicalModel):
    loop_id: str
    current_process_id: str
    process: LoopStepResult


class ProcessHistoryItem(CanonicalModel):
    process_id: str
    request_id: str
    loop_id: str
    completed_at: datetime
    stability_status: StabilityStatus
    stability_value: float | None = None
    operator_response: OperatorResponseType
    continuity_type: RuntimeContinuityType


class ProcessHistoryPage(CanonicalModel):
    loop_id: str
    items: list[ProcessHistoryItem] = Field(default_factory=list)
    limit: int = Field(ge=1, le=100)
    next_cursor: str | None = None


class TrajectoryEdgePage(CanonicalModel):
    trajectory_ref: str
    items: list[TrajectoryEdge] = Field(default_factory=list)
    limit: int = Field(ge=1, le=100)
    next_cursor: str | None = None


MemoryRecord = (
    LoopStepResult
    | SliceDone
    | StabilityResult
    | OperatorResponse
    | RuntimeContinuityResult
    | BoundaryEvidence
    | BoundaryStateRecord
    | ContextEvidence
    | VoidEvidence
    | DeferredRelationRecord
    | TrajectoryEdge
)


class MemoryRecordEnvelope(CanonicalModel):
    record_id: str
    record_type: str
    record: MemoryRecord


class ApiError(CanonicalModel):
    error_id: str
    error_code: str
    message: str
    category: str
    phase: str
    field_path: str | None = None
    related_refs: list[str] = Field(default_factory=list)
    request_id: str | None = None
    loop_id: str | None = None
    retryable: bool = False
    occurred_at: datetime = Field(default_factory=utc_now)
