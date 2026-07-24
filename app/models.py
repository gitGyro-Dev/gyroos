from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class SliceMode(str, Enum):
    SLICE = "SLICE"
    RESLICE = "RESLICE"


class SliceSourceType(str, Enum):
    RUNTIME_STRUCTURE = "RUNTIME_STRUCTURE"
    SLICE_DONE = "SLICE_DONE"
    CONTEXT_EVIDENCE = "CONTEXT_EVIDENCE"
    BOUNDARY_EVIDENCE = "BOUNDARY_EVIDENCE"
    BOUNDARY_STATE_RECORD = "BOUNDARY_STATE_RECORD"
    VOID_EVIDENCE = "VOID_EVIDENCE"
    TRAJECTORY_SEGMENT = "TRAJECTORY_SEGMENT"
    PRIOR_PROCESS_RESULT = "PRIOR_PROCESS_RESULT"
    RETAINED_RELATION = "RETAINED_RELATION"


class BoundaryStateType(str, Enum):
    NORMAL = "NORMAL"
    NON = "NON"
    UN = "UN"
    ABSENCE = "ABSENCE"
    BLANK = "BLANK"
    UNKNOWN = "UNKNOWN"
    VOID = "VOID"


class StabilityStatus(str, Enum):
    STABLE = "STABLE"
    ADAPTIVE = "ADAPTIVE"
    UNSTABLE = "UNSTABLE"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    VOID_RELATED = "VOID_RELATED"


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


class OperatorOrientation(CanonicalModel):
    orientation_id: str = Field(min_length=1)
    weights: dict[str, float] = Field(default_factory=dict)
    resolution: dict[str, float] = Field(default_factory=dict)
    target_dimensions: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SlicePolicy(CanonicalModel):
    policy_id: str = Field(min_length=1)
    policy_type: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeLimits(CanonicalModel):
    max_slice_operations: int = Field(default=1, ge=1, le=1)
    max_reslice_depth: int = Field(default=2, ge=1, le=16)
    max_context_chain_length: int = Field(default=3, ge=1, le=64)
    max_branch_count: int = Field(default=2, ge=1, le=64)
    max_evidence_refs: int = Field(default=128, ge=1, le=4096)
    max_payload_bytes: int = Field(default=1_048_576, ge=1024, le=16_777_216)
    deadline_ms: int = Field(default=5000, ge=1, le=120_000)


class RuntimeStructureInput(CanonicalModel):
    structure_id: str = Field(min_length=1)
    current_mode: dict[str, Any]
    retained_conditions: dict[str, Any] = Field(default_factory=dict)
    continuity_refs: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SliceRequest(CanonicalModel):
    mode: SliceMode
    source_type: SliceSourceType
    source_ref: str = Field(min_length=1)
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


class LoopStepRequest(CanonicalModel):
    request_id: str = Field(min_length=1)
    loop_id: str = Field(min_length=1)
    structure: RuntimeStructureInput
    slice_request: SliceRequest
    runtime_limits: RuntimeLimits = Field(default_factory=RuntimeLimits)
    idempotency_key: str | None = None
    client_trace_id: str | None = None
    previous_state_ref: str | None = None
    expected_current_scope_ref: str | None = None
    policy_ref: str | None = None
    request_context: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_source_contract(self) -> "LoopStepRequest":
        req = self.slice_request
        if req.mode == SliceMode.SLICE:
            if req.source_type != SliceSourceType.RUNTIME_STRUCTURE:
                raise ValueError("SLICE requires source_type=RUNTIME_STRUCTURE")
            if req.source_ref != self.structure.structure_id:
                raise ValueError("SLICE source_ref must equal structure.structure_id")
        else:
            missing = [
                name
                for name, value in {
                    "parent_process_ref": req.parent_process_ref,
                    "parent_slice_ref": req.parent_slice_ref,
                    "requested_by_response_ref": req.requested_by_response_ref,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"RESLICE missing lineage: {', '.join(missing)}")
            if req.source_type == SliceSourceType.RUNTIME_STRUCTURE:
                raise ValueError("RESLICE requires an explicitly retained Runtime source")
        return self


class SliceReadability(CanonicalModel):
    representation_readable: bool
    deviation_readable: bool
    boundary_readability: float | None = Field(default=None, ge=0.0, le=1.0)
    target_relation_readability: float | None = Field(default=None, ge=0.0, le=1.0)
    unreadable_aspects: list[str] = Field(default_factory=list)
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BoundaryEvidence(CanonicalModel):
    boundary_evidence_id: str
    slice_id: str
    process_id: str
    relation_ref: str
    distinction_type: str
    boundary_readability: float = Field(ge=0.0, le=1.0)
    source_evidence_refs: list[str] = Field(default_factory=list)
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
    context_confidence: float = Field(ge=0.0, le=1.0)
    source_evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoidEvidence(CanonicalModel):
    void_evidence_id: str
    slice_id: str
    process_id: str
    boundary_ref: str
    relation_ref: str
    reason: str
    target_relation_readability: float | None = Field(default=None, ge=0.0, le=1.0)
    connectability: float | None = Field(default=None, ge=0.0, le=1.0)
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
    created_at: datetime = Field(default_factory=utc_now)
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
    supporting_evidence_refs: list[str] = Field(default_factory=list)
    conflicting_evidence_refs: list[str] = Field(default_factory=list)
    evaluation_policy_ref: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorResponse(CanonicalModel):
    operator_response_id: str
    process_id: str
    slice_id: str
    stability_result_ref: str
    response_type: OperatorResponseType
    reason: str
    response_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    considered_evidence_refs: list[str] = Field(default_factory=list)
    decisive_evidence_refs: list[str] = Field(default_factory=list)
    conflicting_evidence_refs: list[str] = Field(default_factory=list)
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
    pending: bool = False
    terminated_for_current_scope: bool = False
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
