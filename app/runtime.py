from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from uuid import uuid4

from .models import (
    BoundaryEvidence,
    BoundaryStateRecord,
    BoundaryStateType,
    ContextEvidence,
    DeferredRelationRecord,
    LoopStepRequest,
    LoopStepResult,
    OperatorResponse,
    OperatorResponseType,
    RuntimeContinuityResult,
    RuntimeContinuityType,
    SliceDone,
    SliceMode,
    SliceReadability,
    SliceRequest,
    SliceSourceType,
    StabilityResult,
    StabilityStatus,
    TrajectoryEdge,
    VoidEvidence,
)
from .repositories import InMemoryStore


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def canonical_digest(request: LoopStepRequest) -> str:
    payload = request.model_dump(mode="json", exclude={"client_trace_id"})
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ReferenceError(ValueError):
    pass


@dataclass
class ReferenceResolver:
    store: InMemoryStore

    def validate(self, request: LoopStepRequest) -> None:
        refs = [
            request.previous_state_ref,
            request.slice_request.parent_process_ref,
            request.slice_request.parent_slice_ref,
            request.slice_request.requested_by_response_ref,
            request.slice_request.trajectory_ref,
            *request.slice_request.context_refs,
            *request.slice_request.boundary_refs,
            *request.slice_request.boundary_state_refs,
            *request.slice_request.void_refs,
        ]
        for ref in filter(None, refs):
            if self.store.get_record(ref) is None:
                raise ReferenceError(f"record not found: {ref}")

        if request.expected_current_scope_ref is not None:
            current = self.store.get_current_scope(request.loop_id)
            if current != request.expected_current_scope_ref:
                raise RuntimeError("current-scope conflict")

        if request.slice_request.mode == SliceMode.RESLICE:
            response = self.store.get_record(request.slice_request.requested_by_response_ref or "")
            if not isinstance(response, OperatorResponse):
                raise ReferenceError("requested_by_response_ref is not OperatorResponse")
            if response.response_type != OperatorResponseType.RESLICE:
                raise ValueError("requested_by_response_ref did not select RESLICE")


class SliceEngine:
    def execute(self, request: LoopStepRequest, process_id: str) -> SliceDone:
        slice_id = new_id("slice")
        mode = request.structure.current_mode
        boundary_readability = mode.get("boundary_readability")
        target_readability = mode.get("target_relation_readability")
        relation_ref = str(mode.get("relation_ref", request.structure.structure_id))

        readability = SliceReadability(
            representation_readable=bool(mode.get("representation_readable", True)),
            deviation_readable=bool(mode.get("deviation_readable", True)),
            boundary_readability=boundary_readability,
            target_relation_readability=target_readability,
            unreadable_aspects=list(mode.get("unreadable_aspects", [])),
            reason=mode.get("readability_reason"),
        )

        boundary_evidence: list[BoundaryEvidence] = []
        boundary_states: list[BoundaryStateRecord] = []
        context_evidence: list[ContextEvidence] = []
        void_evidence: list[VoidEvidence] = []

        boundary_ref: str | None = None
        if boundary_readability is not None:
            boundary_ref = new_id("boundary")
            boundary_evidence.append(
                BoundaryEvidence(
                    boundary_evidence_id=boundary_ref,
                    slice_id=slice_id,
                    process_id=process_id,
                    relation_ref=relation_ref,
                    distinction_type=str(mode.get("distinction_type", "RUNTIME_RELATION")),
                    boundary_readability=float(boundary_readability),
                )
            )

        state_raw = mode.get("boundary_state")
        if state_raw is not None:
            state_type = BoundaryStateType(state_raw)
            if boundary_ref is None:
                raise ValueError("Boundary State requires identifiable BoundaryEvidence")
            if state_type == BoundaryStateType.VOID and target_readability is None:
                raise ValueError("VOID requires target_relation_readability")
            state_ref = new_id("boundary_state")
            boundary_states.append(
                BoundaryStateRecord(
                    boundary_state_record_id=state_ref,
                    slice_id=slice_id,
                    process_id=process_id,
                    boundary_ref=boundary_ref,
                    relation_ref=relation_ref,
                    state_type=state_type,
                    boundary_state_confidence=float(mode.get("boundary_state_confidence", 1.0)),
                    classification_reason=str(mode.get("boundary_state_reason", "bounded demo classification")),
                    evidence_refs=[boundary_ref],
                )
            )
            if state_type == BoundaryStateType.VOID:
                void_evidence.append(
                    VoidEvidence(
                        void_evidence_id=new_id("void"),
                        slice_id=slice_id,
                        process_id=process_id,
                        boundary_ref=boundary_ref,
                        relation_ref=relation_ref,
                        reason=str(mode.get("void_reason", "target relation unreadable under identifiable Boundary")),
                        target_relation_readability=float(target_readability),
                        connectability=float(mode.get("connectability", 0.0)),
                        supporting_evidence_refs=[boundary_ref, state_ref],
                    )
                )

        if mode.get("context") is not None:
            context_evidence.append(
                ContextEvidence(
                    context_evidence_id=new_id("context"),
                    slice_id=slice_id,
                    process_id=process_id,
                    relation_ref=relation_ref,
                    source_type=str(mode.get("context_source_type", "OBSERVED_SURROUNDING")),
                    content=dict(mode["context"]),
                    context_confidence=float(mode.get("context_confidence", 1.0)),
                )
            )

        representation = dict(mode.get("representation", {}))
        if "stability" in mode:
            representation["stability"] = mode["stability"]

        return SliceDone(
            slice_id=slice_id,
            process_id=process_id,
            structure_ref=request.structure.structure_id,
            representation=representation,
            deviation=dict(mode.get("deviation", {})),
            readability=readability,
            boundary_evidence=boundary_evidence,
            boundary_state_records=boundary_states,
            context_evidence=context_evidence,
            void_evidence=void_evidence,
            boundary_refs=list(request.slice_request.boundary_refs),
            boundary_state_refs=list(request.slice_request.boundary_state_refs),
            context_refs=list(request.slice_request.context_refs),
            void_refs=list(request.slice_request.void_refs),
            orientation_ref=request.slice_request.orientation.orientation_id,
            slice_policy_ref=request.slice_request.slice_policy.policy_id,
            trajectory_ref=request.slice_request.trajectory_ref,
            parent_process_ref=request.slice_request.parent_process_ref,
            parent_slice_ref=request.slice_request.parent_slice_ref,
            source_type=request.slice_request.source_type,
            source_ref=request.slice_request.source_ref,
            metadata={"relation_ref": relation_ref},
        )


class StabilityEngine:
    def read(self, slice_done: SliceDone, policy_ref: str | None) -> StabilityResult:
        mode = slice_done.representation
        raw_value = mode.get("stability")
        state_types = {item.state_type for item in slice_done.boundary_state_records}
        if BoundaryStateType.VOID in state_types:
            status = StabilityStatus.VOID_RELATED
            continuability = None
            reason = "Stability reading is materially affected by Void-related evidence."
        elif raw_value is None:
            status = StabilityStatus.NOT_EVALUABLE
            continuability = None
            reason = "No numeric Stability reading was supplied by the bounded Slice policy."
        else:
            value = float(raw_value)
            if value >= 0.8:
                status, continuability = StabilityStatus.STABLE, True
            elif value >= 0.5:
                status, continuability = StabilityStatus.ADAPTIVE, True
            else:
                status, continuability = StabilityStatus.UNSTABLE, False
            reason = "Bounded demo Stability policy evaluated the Slice representation."

        return StabilityResult(
            stability_result_id=new_id("stability"),
            process_id=slice_done.process_id,
            slice_id=slice_done.slice_id,
            value=float(raw_value) if raw_value is not None else None,
            status=status,
            continuability=continuability,
            reason=reason,
            evidence_refs=[
                *(item.boundary_evidence_id for item in slice_done.boundary_evidence),
                *(item.boundary_state_record_id for item in slice_done.boundary_state_records),
                *(item.context_evidence_id for item in slice_done.context_evidence),
                *(item.void_evidence_id for item in slice_done.void_evidence),
            ],
            evaluation_policy_ref=policy_ref,
        )


class LoopController:
    """The sole OperatorResponse selector in the bounded implementation."""

    def select(
        self,
        request: LoopStepRequest,
        slice_done: SliceDone,
        stability: StabilityResult,
    ) -> OperatorResponse:
        policy = request.slice_request.slice_policy
        response_type = OperatorResponseType(policy.parameters.get("response_type", "CONTINUE"))
        response_id = new_id("response")
        next_request: SliceRequest | None = None

        if response_type == OperatorResponseType.RESLICE:
            source_ref = policy.parameters.get("reslice_source_ref")
            source_type = policy.parameters.get("reslice_source_type")
            if not source_ref or not source_type:
                raise ValueError("RESLICE policy requires reslice_source_ref and reslice_source_type")
            next_request = SliceRequest(
                mode=SliceMode.RESLICE,
                source_type=SliceSourceType(source_type),
                source_ref=str(source_ref),
                orientation=request.slice_request.orientation,
                slice_policy=request.slice_request.slice_policy,
                parent_process_ref=slice_done.process_id,
                parent_slice_ref=slice_done.slice_id,
                trajectory_ref=slice_done.trajectory_ref,
                requested_by_response_ref=response_id,
            )

        considered = list(stability.evidence_refs)
        decisive = list(policy.parameters.get("decisive_evidence_refs", []))
        if not set(decisive).issubset(considered):
            raise ValueError("decisive_evidence_refs must be a subset of considered evidence")

        return OperatorResponse(
            operator_response_id=response_id,
            process_id=slice_done.process_id,
            slice_id=slice_done.slice_id,
            stability_result_ref=stability.stability_result_id,
            response_type=response_type,
            reason=str(policy.parameters.get("response_reason", "Selected by bounded SlicePolicy.")),
            response_confidence=float(policy.parameters.get("response_confidence", 1.0)),
            considered_evidence_refs=considered,
            decisive_evidence_refs=decisive,
            next_request=next_request,
            selected_by_policy_ref=policy.policy_id,
        )


class ContinuityBuilder:
    _mapping = {
        OperatorResponseType.CONTINUE: RuntimeContinuityType.DIRECT_CONNECTION,
        OperatorResponseType.ADJUST: RuntimeContinuityType.ADJUSTED_CONNECTION,
        OperatorResponseType.RESLICE: RuntimeContinuityType.RESLICE_CONNECTION,
        OperatorResponseType.JUMP: RuntimeContinuityType.JUMP_RECONNECTION,
        OperatorResponseType.DEFER: RuntimeContinuityType.DEFERRED_PENDING_RELATION,
        OperatorResponseType.STOP: RuntimeContinuityType.STOPPED_FOR_CURRENT_SCOPE,
    }

    def build(self, response: OperatorResponse, source_ref: str) -> RuntimeContinuityResult:
        return RuntimeContinuityResult(
            continuity_result_id=new_id("continuity"),
            process_id=response.process_id,
            operator_response_ref=response.operator_response_id,
            continuity_type=self._mapping[response.response_type],
            connected=response.response_type in {OperatorResponseType.CONTINUE, OperatorResponseType.ADJUST},
            pending=response.response_type == OperatorResponseType.DEFER,
            terminated_for_current_scope=response.response_type == OperatorResponseType.STOP,
            source_ref=source_ref,
            target_ref=response.next_request.source_ref if response.next_request else None,
        )


@dataclass
class ProcessExecutor:
    store: InMemoryStore

    def execute(self, request: LoopStepRequest) -> LoopStepResult:
        digest = canonical_digest(request)
        if request.idempotency_key:
            prior = self.store.get_idempotent(request.loop_id, request.idempotency_key)
            if prior:
                prior_digest, prior_result = prior
                if prior_digest != digest:
                    raise RuntimeError("idempotency conflict")
                return prior_result.model_copy(update={"replayed": True})

        ReferenceResolver(self.store).validate(request)
        process_id = new_id("process")
        slice_done = SliceEngine().execute(request, process_id)
        stability = StabilityEngine().read(slice_done, request.policy_ref)
        response = LoopController().select(request, slice_done, stability)
        continuity = ContinuityBuilder().build(response, slice_done.source_ref)

        if response.response_type == OperatorResponseType.RESLICE and response.next_request is None:
            raise ValueError("RESLICE requires next_request")
        if response.response_type == OperatorResponseType.STOP and response.next_request is not None:
            raise ValueError("STOP requires next_request=null")

        deferred_record = None
        if response.response_type == OperatorResponseType.DEFER:
            deferred_record = DeferredRelationRecord(
                deferred_relation_record_id=new_id("deferred_relation"),
                process_id=process_id,
                operator_response_ref=response.operator_response_id,
                continuity_result_ref=continuity.continuity_result_id,
                relation_ref=slice_done.source_ref,
                evidence_refs=list(response.considered_evidence_refs),
            )

        relation_ref = str(slice_done.metadata.get("relation_ref", slice_done.source_ref))
        trajectory_edge = TrajectoryEdge(
            trajectory_edge_id=new_id("trajectory_edge"),
            process_id=process_id,
            operator_response_ref=response.operator_response_id,
            continuity_result_ref=continuity.continuity_result_id,
            edge_type=continuity.continuity_type,
            relation_ref=relation_ref,
            source_ref=continuity.source_ref,
            target_ref=continuity.target_ref,
            parent_process_ref=slice_done.parent_process_ref,
        )

        created_refs = [
            slice_done.slice_id,
            stability.stability_result_id,
            response.operator_response_id,
            continuity.continuity_result_id,
            trajectory_edge.trajectory_edge_id,
            *(item.boundary_evidence_id for item in slice_done.boundary_evidence),
            *(item.boundary_state_record_id for item in slice_done.boundary_state_records),
            *(item.context_evidence_id for item in slice_done.context_evidence),
            *(item.void_evidence_id for item in slice_done.void_evidence),
        ]
        if deferred_record is not None:
            created_refs.append(deferred_record.deferred_relation_record_id)

        result = LoopStepResult(
            process_id=process_id,
            request_id=request.request_id,
            loop_id=request.loop_id,
            slice_done=slice_done,
            stability=stability,
            operator_response=response,
            continuity=continuity,
            deferred_relation_record=deferred_record,
            trajectory_edges=[trajectory_edge],
            created_record_refs=created_refs,
        )
        self.store.publish(
            result=result,
            request_digest=digest,
            idempotency_key=request.idempotency_key,
        )
        return result
