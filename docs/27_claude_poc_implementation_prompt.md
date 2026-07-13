# 27. Claude PoC Implementation Prompt

---

## 1. Purpose

This document is the implementation prompt for the first bounded GyroOS v4 / vNext PoC.

The goal is not to build a real operating system.

The goal is to implement the smallest executable Runtime demonstration that preserves the Gyro Logic v3.1 Core and the Priority A / B / C / D responsibility boundaries.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The PoC must make the following Runtime relation visible:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
↓
StabilityResult
↓
LoopController / OperatorResponse
↓
RuntimeContinuityResult
↓
Next Process when applicable
```

---

# Claude Prompt

You are the implementation AI for the first bounded GyroOS v4 / vNext PoC.

Implement the specification below exactly.

Do not redesign Gyro Logic.

Do not expand the scope beyond a local console demonstration.

Do not implement a real OS, application layer, authentication system, autonomous agent, network service, or persistent database.

---

## 0. Non-negotiable Principles

The theoretical Core is:

```text
Structure → Slice → Stability
```

Do not modify it.

Operator Orientation, Slice Policy, slice-ing, and slice-done are Runtime distinctions internal to Slice.

```text
Operator Orientation
≠ independent Core stage

slice-done
≠ Stability

StabilityResult
≠ OperatorResponse

Boundary State
≠ Stability

Boundary State
≠ OperatorResponse

Void
≠ action
```

LoopController is the only component that selects OperatorResponse.

The canonical OperatorResponse vocabulary is:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Do not use the following legacy names as response types:

```text
RESLICE_CONTEXT
CHANGE_ORIENTATION
DEFER_VOID
VOID
```

Compatibility meaning only:

```text
RESLICE_CONTEXT → RESLICE with Context source references
CHANGE_ORIENTATION → ADJUST
DEFER_VOID → DEFER with Void-related evidence
```

---

## 1. Implementation Scope

Implement only a bounded Python console PoC.

Required core objects:

```text
RuntimeStructure
OperatorOrientation
SlicePolicy
SliceRequest
GyroProcess
SliceDone
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityResult
OperatorResponse
UpdateDecision
RuntimeContinuityResult
DeferredRelationRecord
LoopState
MemoryRuntime
TrajectoryEdge
TrajectoryCacheEntry
TrajectoryCache
DamperState
LoopStepResult
GyroRuntime
SliceEngine
StabilityEngine
LoopController
UpdateEngine
ReSliceEngine
```

Optional only when the implementation remains simple:

```text
CurrentScopeView
DynamicEquivalenceRuntime stub
```

---

## 2. What Must Not Be Implemented

Do not implement:

```text
real OS kernel
real authentication
GyroAuth
FastAPI
HTTP server
WebSocket
React
Streamlit
GUI
external database
persistent file storage
cloud sync
distributed storage
vector database
LLM integration
background daemon
multi-user runtime
plugin system
real security enforcement
unbounded autonomous execution
real Boundary detection AI
machine-learning classification
```

Do not implement conceptual shortcuts such as:

```text
Stability as controller
UpdateEngine as response owner
ReSliceEngine as response owner
MemoryRuntime as response owner
DamperState as response owner
Context existence automatically starts Re-Slice
Boundary State automatically determines Stability
Boundary State automatically determines OperatorResponse
Void evidence automatically produces DEFER
low Stability automatically produces STOP
large Difference automatically produces JUMP
```

---

## 3. Runtime Limits

Hard-code bounded limits.

```python
MAX_PROCESS_STEPS = 10
MAX_RESLICE_DEPTH = 2
MAX_SOURCE_CHAIN_LENGTH = 4
MAX_TRAJECTORY_EDGES = 24
MAX_BOUNDARIES_PER_SLICE = 3
MAX_BOUNDARY_STATES_PER_SLICE = 3
MAX_BOUNDARY_RECORDS = 20
MAX_VOID_RECORDS = 8
MAX_BRANCH_COUNT = 3
DYNAMIC_EQUIVALENCE_ENABLED = False
GYROAUTH_ENABLED = False
```

Requirements:

```text
no infinite loops
no unbounded recursion
no background execution
no external I/O except console output
no implicit retry loop
```

Limit signals are evidence for LoopController.

A limit must not choose a response by itself.

---

## 4. Project Structure

Use Python 3.11 or later.

Prefer the following minimal structure:

```text
gyroos_poc/
  README.md
  requirements.txt
  demo.py
```

Prefer a single-file implementation first.

Use the Python standard library only.

`requirements.txt` may remain empty.

Use:

```text
dataclasses
enum
typing
uuid
```

Do not add frameworks.

---

## 5. Required Data Model

Use `@dataclass` and `Enum`.

### RuntimeStructure

```python
@dataclass
class RuntimeStructure:
    structure_id: str
    current_mode: dict
    retained_conditions: dict = field(default_factory=dict)
    continuity_refs: list[str] = field(default_factory=list)
    constraints: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

RuntimeStructure is the current Runtime mode in which another establishment remains possible.

It is not merely an input payload.

### OperatorOrientation

```python
@dataclass
class OperatorOrientation:
    orientation_id: str
    weights: dict[str, float]
    resolution: dict[str, float]
    target_dimensions: list[str]
    constraints: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

### SlicePolicy

```python
@dataclass
class SlicePolicy:
    policy_id: str
    mode: str
    thresholds: dict[str, float] = field(default_factory=dict)
    limits: dict[str, int] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

OperatorOrientation and SlicePolicy are internal Runtime configuration for Slice.

### SliceRequest

```python
@dataclass
class SliceRequest:
    request_id: str
    process_index: int
    source_type: str
    source_ref: str
    mode: str
    orientation: OperatorOrientation
    slice_policy: SlicePolicy
    context_refs: list[str] = field(default_factory=list)
    parent_process_id: str | None = None
    parent_slice_id: str | None = None
    reslice_depth: int = 0
    source_chain: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

Allowed example `source_type` values:

```text
runtime_structure
slice_done
context_evidence
boundary_evidence
boundary_state_record
void_evidence
trajectory_segment
retained_relation
```

`mode = "reslice"` is an implementation marker only.

Re-Slice remains Slice applied again to a retained source relation.

### BoundaryEvidence

```python
@dataclass
class BoundaryEvidence:
    boundary_id: str
    source_slice_id: str
    distinction_type: str
    relation_a_ref: str | None
    relation_b_ref: str | None
    boundary_readability: float
    evidence_refs: list[str] = field(default_factory=list)
    context_refs: list[str] = field(default_factory=list)
    origin_mode: str | None = None
    metadata: dict = field(default_factory=dict)
```

Canonical statement:

```text
The distinction became readable through the current Slice.
```

`origin_mode` is optional metadata such as:

```text
formed
exposed
retained
unknown
```

### BoundaryStateRecord

```python
class BoundaryStateType(str, Enum):
    NORMAL = "NORMAL"
    NON = "NON"
    UN = "UN"
    ABSENCE = "ABSENCE"
    BLANK = "BLANK"
    UNKNOWN = "UNKNOWN"
    VOID = "VOID"

@dataclass
class BoundaryStateRecord:
    boundary_state_id: str
    boundary_ref: str
    relation_ref: str | None
    source_slice_id: str
    state_type: BoundaryStateType
    boundary_state_confidence: float
    provisional: bool = True
    previous_state_ref: str | None = None
    lineage_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

The full candidate vocabulary remains available.

For the first PoC scenarios, use only:

```text
NORMAL
UNKNOWN
VOID
```

This subset is not the closed GyroOS enum.

### ContextEvidence

```python
@dataclass
class ContextEvidence:
    context_id: str
    source_slice_id: str
    source_type: str
    relation_refs: list[str]
    context_readability: float
    context_confidence: float
    inferability_score: float
    inference_basis_refs: list[str] = field(default_factory=list)
    provisional: bool = True
    metadata: dict = field(default_factory=dict)
```

Context is Slice-relative evidence related to the opened Path but not fully included in the explicit representation.

### VoidEvidence

```python
@dataclass
class VoidEvidence:
    void_id: str
    source_slice_id: str
    boundary_ref: str | None
    relation_ref: str | None
    reason: str
    unreadability: float
    unconnectability: float
    evidence_refs: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

Do not add fields such as:

```text
deferred
resolved
response_type
```

VoidEvidence does not own a response state.

### SliceDone

```python
@dataclass
class SliceDone:
    slice_id: str
    process_id: str
    process_index: int
    representation: dict
    deviation: dict
    boundary_evidence: list[BoundaryEvidence] = field(default_factory=list)
    boundary_state_records: list[BoundaryStateRecord] = field(default_factory=list)
    context_evidence: list[ContextEvidence] = field(default_factory=list)
    void_evidence: list[VoidEvidence] = field(default_factory=list)
    boundary_refs: list[str] = field(default_factory=list)
    boundary_state_refs: list[str] = field(default_factory=list)
    context_refs: list[str] = field(default_factory=list)
    void_refs: list[str] = field(default_factory=list)
    orientation_ref: str | None = None
    slice_policy_ref: str | None = None
    parent_slice_ref: str | None = None
    trajectory_ref: str | None = None
    readability: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

SliceDone is the readable established Slice result.

```text
SliceDone
≠ StabilityResult
```

Boundary-aware does not mean Boundary-required.

A SliceDone with no Boundary is valid.

### StabilityResult

```python
@dataclass
class StabilityResult:
    process_id: str
    value: float | None
    status: str
    continuability: bool | None
    reason: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

Possible implementation statuses:

```text
stable
adaptive
unstable
not_evaluable
void_related
```

These are Runtime statuses, not new theory definitions.

Keep separate:

```text
boundary_readability
boundary_state_confidence
context_confidence
stability
response_confidence
```

### OperatorResponse

```python
class ResponseType(str, Enum):
    CONTINUE = "CONTINUE"
    ADJUST = "ADJUST"
    RESLICE = "RESLICE"
    JUMP = "JUMP"
    DEFER = "DEFER"
    STOP = "STOP"

@dataclass
class OperatorResponse:
    process_id: str
    response_type: ResponseType
    reason: str
    decisive_evidence_refs: list[str] = field(default_factory=list)
    considered_evidence_refs: list[str] = field(default_factory=list)
    conflicting_evidence_refs: list[str] = field(default_factory=list)
    response_confidence: float | None = None
    next_request: SliceRequest | None = None
    metadata: dict = field(default_factory=dict)
```

### RuntimeContinuityResult

```python
@dataclass
class RuntimeContinuityResult:
    continuity_id: str
    process_id: str
    continuity_type: str
    source_ref: str
    target_ref: str | None
    pending: bool
    terminated_for_current_scope: bool
    metadata: dict = field(default_factory=dict)
```

Example `continuity_type` values:

```text
direct_connection
adjusted_connection
reslice_connection
jump_reconnection
deferred_pending_relation
stopped_for_current_scope
```

### DeferredRelationRecord

```python
@dataclass
class DeferredRelationRecord:
    deferred_relation_id: str
    source_process_id: str
    source_ref: str
    evidence_refs: list[str]
    revisit_condition: dict | None
    active_for_current_scope: bool = True
    metadata: dict = field(default_factory=dict)
```

A deferred relation is created because OperatorResponse selected `DEFER`.

It is not a field inside VoidEvidence.

---

## 6. Memory and Trajectory Objects

### MemoryRuntime

Use separate record stores.

```python
@dataclass
class MemoryRuntime:
    slice_done_records: dict[str, SliceDone] = field(default_factory=dict)
    boundary_records: dict[str, BoundaryEvidence] = field(default_factory=dict)
    boundary_state_records: dict[str, BoundaryStateRecord] = field(default_factory=dict)
    context_records: dict[str, ContextEvidence] = field(default_factory=dict)
    void_records: dict[str, VoidEvidence] = field(default_factory=dict)
    stability_records: dict[str, StabilityResult] = field(default_factory=dict)
    response_records: dict[str, OperatorResponse] = field(default_factory=dict)
    continuity_records: dict[str, RuntimeContinuityResult] = field(default_factory=dict)
    deferred_relation_records: dict[str, DeferredRelationRecord] = field(default_factory=dict)
```

Requirements:

```text
never overwrite Boundary State history silently
never attach DEFER state to VoidEvidence
preserve parent and lineage references
allow a current-scope record without deleting prior records
```

### TrajectoryEdge

```python
@dataclass
class TrajectoryEdge:
    edge_id: str
    source_process_ref: str
    target_process_ref: str | None
    response_ref: str
    continuity_ref: str
    relation_type: str
    evidence_refs: list[str] = field(default_factory=list)
```

### TrajectoryCacheEntry

```python
@dataclass
class TrajectoryCacheEntry:
    trajectory_id: str
    process_refs: list[str] = field(default_factory=list)
    slice_refs: list[str] = field(default_factory=list)
    boundary_refs: list[str] = field(default_factory=list)
    boundary_state_refs: list[str] = field(default_factory=list)
    context_refs: list[str] = field(default_factory=list)
    void_refs: list[str] = field(default_factory=list)
    stability_refs: list[str] = field(default_factory=list)
    response_refs: list[str] = field(default_factory=list)
    continuity_refs: list[str] = field(default_factory=list)
    edges: list[TrajectoryEdge] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

Trajectory may contain direct continuation, Re-Slice lineage, Jump branches, pending Defer relations, and Stop boundaries.

It is not required to remain one linear sequence.

---

## 7. Engine Responsibilities

### SliceEngine

```text
Input: SliceRequest + Runtime source
Output: SliceDone
```

Responsibilities:

```text
execute bounded slice-ing
produce representation and deviation
optionally make Boundary evidence readable
optionally produce provisional Boundary State records
optionally retain ContextEvidence and VoidEvidence
preserve source and parent references
```

SliceEngine does not select OperatorResponse.

### StabilityEngine

```text
Input: SliceDone
Output: StabilityResult
```

It may consider all SliceDone evidence.

It does not classify Boundary State and does not select OperatorResponse.

### LoopController

```text
Input:
  SliceDone
  StabilityResult
  LoopState
  Memory / Trajectory summaries
  DamperState

Output:
  OperatorResponse
```

LoopController is the only response owner.

### UpdateEngine

Applies a selected `ADJUST` or prepares selected reconnection parameters.

It does not select the response.

### ReSliceEngine

Executes an already selected `RESLICE` request.

```text
RESLICE response
→ SliceRequest(mode="reslice")
→ ReSliceEngine
→ new SliceDone
```

It must preserve parent and source lineage.

### DamperState

DamperState reports bounded pressure evidence only.

```python
@dataclass
class DamperState:
    memory_pressure: float
    trajectory_branch_count: int
    reslice_depth: int
    source_chain_length: int
    void_record_count: int
    cycle_detected: bool
    limit_evidence_refs: list[str] = field(default_factory=list)
```

DamperState does not issue `DEFER`, `JUMP`, or `STOP`.

---

## 8. Required Runtime Flow

Implement `GyroRuntime.loop_step()` with the following bounded sequence:

```text
1. Create GyroProcess.
2. Create or accept SliceRequest.
3. SliceEngine executes slice-ing.
4. SliceEngine produces SliceDone.
5. MemoryRuntime stores SliceDone and embedded evidence records.
6. StabilityEngine produces StabilityResult.
7. LoopController considers multiple evidence inputs.
8. LoopController selects exactly one OperatorResponse.
9. UpdateEngine or ReSliceEngine prepares execution only when requested.
10. Create RuntimeContinuityResult.
11. Create DeferredRelationRecord only when response is DEFER.
12. Append TrajectoryEdge and references.
13. Update DamperState pressure evidence.
14. Return LoopStepResult.
```

The loop must remain bounded by `MAX_PROCESS_STEPS`.

---

## 9. Required Decision Policy

Use deterministic PoC policy, but combine multiple evidence fields.

Do not write direct rules such as:

```python
if boundary_state == "VOID":
    return "DEFER"
```

Do not write:

```python
if stability.status == "not_evaluable":
    return "DEFER"
```

Use a rule shape similar to:

```python
if (
    has_identifiable_boundary
    and has_void_target_relation
    and future_context_is_plausible
    and not reslice_currently_viable
    and runtime_can_retain_relation
):
    response = ResponseType.DEFER
elif (
    boundary_state_is_unknown
    and context_source_available
    and reslice_depth_below_limit
    and trajectory_not_cyclic
):
    response = ResponseType.RESLICE
elif (
    conflicting_boundary_evidence
    and bounded_adjustment_is_viable
):
    response = ResponseType.ADJUST
elif (
    conflicting_boundary_evidence
    and bounded_adjustment_is_not_viable
    and reconstruction_is_necessary
):
    response = ResponseType.JUMP
elif (
    path_is_readable
    and stability_continuability_is_true
    and no_stronger_runtime_constraint
):
    response = ResponseType.CONTINUE
else:
    response = ResponseType.STOP
```

This is only a PoC policy example.

Do not describe it as a Gyro Logic definition.

Every response must include:

```text
reason
decisive_evidence_refs
considered_evidence_refs
response_confidence when implemented
```

---

## 10. Required Demo Scenarios

Implement four deterministic scenarios.

### Scenario 1: Readable Boundary / NORMAL / CONTINUE

```text
Boundary distinction is readable.
Boundary State = NORMAL.
Difference is bounded.
Stability is continuable.
OperatorResponse = CONTINUE.
```

The output must not imply:

```text
NORMAL automatically means CONTINUE.
```

### Scenario 2: UNKNOWN / Context Source / RESLICE

```text
Boundary is identifiable.
Boundary State = UNKNOWN.
Classification evidence is insufficient.
ContextEvidence is available.
Re-Slice is viable and within limits.
OperatorResponse = RESLICE.
next_request.source_type = context_evidence.
```

The output must show that `UNKNOWN` was considered with Context, Stability, Difference, and limits.

### Scenario 3: VOID / DEFER

```text
The relevant Boundary is identifiable.
The target relation is not sufficiently readable or connectable relative to it.
VoidEvidence is retained.
Future Context may restore connectability.
Immediate Re-Slice is not currently useful.
OperatorResponse = DEFER.
DeferredRelationRecord is created.
```

Important:

```text
Boundary itself unreadable
≠ automatic VOID
```

When the distinction itself is unreadable, emit unclassified Boundary evidence instead of assigning `VOID`.

### Scenario 4: Conflicting Boundary Evidence / ADJUST or JUMP

Implement two bounded variants or choose one clearly:

```text
Variant A:
  conflicting evidence
  bounded modification remains viable
  OperatorResponse = ADJUST

Variant B:
  conflicting evidence
  bounded modification is not viable
  reconstruction is necessary
  OperatorResponse = JUMP
```

Do not select both responses in one execution branch.

---

## 11. LoopStepResult

```python
@dataclass
class LoopStepResult:
    loop_id: str
    process_id: str
    process_index: int
    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    continuity: RuntimeContinuityResult
    update_decision: UpdateDecision | None
    deferred_relation: DeferredRelationRecord | None
    trajectory_id: str
    next_ready: bool
    metadata: dict = field(default_factory=dict)
```

---

## 12. Console Output Requirements

Print each Process clearly.

Each Process must show:

```text
Process index
Process ID
Operator Orientation
Slice Policy
slice-ing status
SliceDone representation
Difference / Deviation
BoundaryEvidence with boundary_readability
BoundaryStateRecord with state_type and boundary_state_confidence
ContextEvidence summary
VoidEvidence summary
StabilityResult
OperatorResponse
response reason
response decisive evidence refs
RuntimeContinuityResult
DeferredRelationRecord when applicable
Trajectory edge count
Damper pressure signals
```

Recommended output style:

```text
[Process 2]
Orientation: context_refinement
Slice Policy: bounded_reslice
slice-ing...
SliceDone: X={...}, Δ={...}
Boundary: boundary-002 readability=0.82
Boundary State: UNKNOWN confidence=0.61 provisional=true
Context refs: [context-002]
Void refs: []
Stability: adaptive continuability=true
LoopController: RESLICE
Reason: classification evidence is insufficient and a bounded Context source is available
Decisive evidence: [boundary-state-002, context-002, limit-ok-002]
Continuity: reslice_connection
```

Avoid output such as:

```text
Boundary UNKNOWN, therefore RESLICE.
Void exists, therefore DEFER.
Low Stability, therefore STOP.
```

---

## 13. Required Assertions

Add lightweight assertions proving:

```text
SliceDone is not StabilityResult.
StabilityResult is not OperatorResponse.
VOID is not a ResponseType.
BoundaryStateRecord does not contain response fields.
VoidEvidence does not contain deferred or resolved flags.
Only LoopController selects OperatorResponse.
ReSliceEngine runs only for a selected RESLICE request.
Boundary State history is not overwritten during reclassification.
A DEFER response creates a separate DeferredRelationRecord.
Trajectory preserves parent and branch references.
All execution respects configured limits.
```

---

## 14. Deliverables

Return:

```text
1. Short implementation explanation
2. File structure
3. requirements.txt
4. README.md
5. Complete demo.py
6. How to run
7. Expected console output
8. Notes on intentionally unimplemented scope
9. Explanation of how the four scenarios avoid direct Boundary State → Response mapping
```

The generated code must run with:

```bash
python demo.py
```

---

## 15. Acceptance Criteria

The PoC is acceptable only when a user can observe that:

```text
1. Structure → Slice → Stability remains unchanged.
2. Operator Orientation and slice-ing remain internal to Slice.
3. SliceDone preserves optional Boundary-aware evidence.
4. Boundary State remains provisional and Slice-relative.
5. Boundary readability, Boundary State confidence, Stability, and Response confidence remain distinct.
6. VoidEvidence remains separate from DEFER.
7. LoopController selects a response from multiple inputs.
8. RESLICE executes a new Slice from a retained source relation.
9. Memory preserves reclassification and lineage without silent overwrite.
10. Trajectory records direct, adjusted, resliced, jumped, deferred, and stopped continuity relations.
11. The runtime remains bounded.
```

---

## 16. Final Instruction

Implement the smallest bounded console demonstration that makes the following responsibility chain visible:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done with optional Boundary-aware evidence
}
↓
StabilityResult
↓
LoopController / OperatorResponse
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
RuntimeContinuityResult
↓
Memory and Trajectory preservation
```

Do not implement a real OS.

Do not implement GyroAuth.

Do not add autonomous or unbounded execution.

Implement the Runtime relation, not the whole operating system.
