# 26. PoC Runtime Object Graph

---

## 1. Overview

This document defines the minimal runtime object graph for the GyroOS Boundary-aware PoC after the Gyro Logic v3.1 Core refinement and Priority A / B / C / D alignment.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The PoC implements the bounded Runtime expansion:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Runtime Continuity relation
→ Gyro Processₙ₊₁ when applicable
```

The object graph must make responsibility boundaries visible without implementing a full operating system.

---

## 2. PoC Scope

The first implementation should demonstrate:

```text
RuntimeStructure
SliceRequest
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
Boundary-aware SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
MemoryRuntime
TrajectoryCache
bounded pressure signals
```

The PoC must not implement:

```text
real Boundary detection AI
machine learning
LLM inference
persistent database
distributed runtime
application-specific policy
GyroAuth authentication decisions
unbounded autonomous looping
```

---

## 3. Canonical Responsibility Chain

```text
RuntimeStructure
↓
SliceRequest
↓
SliceEngine
↓
SliceDone {
  representation
  Difference / Deviation
  BoundaryEvidence[]
  BoundaryStateRecord[]
  ContextEvidence[]
  VoidEvidence[]
  record refs
}
↓
StabilityEngine
↓
StabilityResult
↓
LoopController
↓
OperatorResponse
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
RuntimeContinuityResult
↓
MemoryRuntime / TrajectoryCache preservation
```

The following must remain separate:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

Boundary and Boundary State are Slice-derived evidence, not Runtime stages.

---

## 4. Core Object Graph

```text
GyroRuntime
├─ LoopState
│  ├─ current_process_ref
│  ├─ current_structure_ref
│  ├─ current_orientation_ref
│  ├─ active_trajectory_ref
│  ├─ current_scope_view
│  └─ runtime_limits
│
├─ Engines
│  ├─ SliceEngine
│  ├─ StabilityEngine
│  ├─ LoopController
│  ├─ UpdateEngine
│  ├─ ReSliceEngine
│  └─ DynamicEquivalenceRuntime [optional]
│
├─ MemoryRuntime
│  ├─ SliceDoneRecord
│  ├─ DeviationRecord
│  ├─ BoundaryEvidence
│  ├─ BoundaryStateRecord
│  ├─ ContextEvidence
│  ├─ VoidEvidence
│  ├─ StabilityRecord
│  ├─ OperatorResponseRecord
│  ├─ ContinuityRecord
│  └─ DeferredRelationRecord
│
└─ TrajectoryCache
   ├─ TrajectoryCacheEntry
   ├─ TrajectoryEdge
   └─ TrajectoryCurrentScopeView
```

---

## 5. Runtime Orchestrator

```python
class GyroRuntime:
    loop_state: "LoopState"
    slice_engine: "SliceEngine"
    stability_engine: "StabilityEngine"
    loop_controller: "LoopController"
    update_engine: "UpdateEngine"
    reslice_engine: "ReSliceEngine"
    memory: "MemoryRuntime"
    trajectory_cache: "TrajectoryCache"

    def loop_step(
        self,
        structure: "RuntimeStructure",
        slice_request: "SliceRequest",
    ) -> "LoopStepResult":
        ...
```

`GyroRuntime` orchestrates one bounded `/loop/step` execution.

It does not:

```text
redefine Gyro Logic
select application outcomes
make GyroAuth decisions
silently repeat Processes without limits
```

---

## 6. LoopState

```python
class LoopState:
    loop_id: str
    process_index: int

    current_process_ref: str | None
    current_structure_ref: str | None
    current_orientation_ref: str | None
    active_trajectory_ref: str | None

    last_response_ref: str | None
    current_scope_view_ref: str | None

    runtime_limits: "RuntimeLimits"
    metadata: dict
```

`LoopState` is a current-scope view.

```text
LoopState
≠ complete Runtime history
```

Complete evidence and lineage remain in MemoryRuntime and TrajectoryCache.

---

## 7. GyroProcess

```python
class GyroProcess:
    process_id: str
    process_index: int

    structure_ref: str
    slice_request_ref: str
    slice_done_ref: str | None
    stability_ref: str | None
    response_ref: str | None
    continuity_ref: str | None

    parent_process_ref: str | None
    trajectory_ref: str | None
    status: str
    metadata: dict
```

Candidate status values:

```text
created
slice_ing
slice_done
stability_read
responded
continuity_recorded
completed_for_scope
```

A status is an implementation lifecycle marker, not a Core definition.

---

## 8. RuntimeStructure

```python
class RuntimeStructure:
    structure_id: str
    current_mode: dict
    retained_conditions: dict
    continuity_refs: list[str]
    constraints: dict
    metadata: dict
```

Runtime Structure is not merely an input payload.

```text
RuntimeStructure
= current Runtime mode in which a next establishment remains possible
```

It may retain effects from prior Stability, Context, Difference, Boundary, and Trajectory records.

---

## 9. OperatorOrientation and SlicePolicy

```python
class OperatorOrientation:
    orientation_id: str
    weights: dict[str, float]
    resolution: dict[str, float]
    target_dimensions: list[str]
    constraints: dict
    metadata: dict


class SlicePolicy:
    policy_id: str
    orientation_ref: str
    source_constraints: dict
    execution_limits: dict
    metadata: dict
```

Operator Orientation and Slice Policy remain internal directional conditions of Slice.

Incorrect:

```text
Structure → Operator Orientation → Slice
```

Correct:

```text
Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
↓
Stability
```

---

## 10. SliceRequest

```python
class SliceRequest:
    request_id: str
    process_id: str

    mode: str                 # slice | reslice
    source_type: str
    source_ref: str

    orientation: OperatorOrientation
    slice_policy: SlicePolicy
    context_refs: list[str]

    parent_process_ref: str | None
    parent_slice_ref: str | None
    trajectory_ref: str | None

    requested_by_response_ref: str | None
    metadata: dict
```

Candidate `source_type` values:

```text
runtime_structure
slice_done
context_evidence
boundary_evidence
boundary_state_record
void_evidence
trajectory_segment
prior_process_result
retained_relation
```

`mode="reslice"` is an implementation marker only.

Re-Slice remains Slice applied again to a retained Runtime source.

---

## 11. Boundary-aware SliceDone

```python
class SliceDone:
    slice_id: str
    process_id: str
    structure_ref: str

    representation: dict
    deviation: dict

    boundary_evidence: list["BoundaryEvidence"]
    boundary_state_records: list["BoundaryStateRecord"]
    context_evidence: list["ContextEvidence"]
    void_evidence: list["VoidEvidence"]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str
    slice_policy_ref: str
    parent_slice_ref: str | None
    trajectory_ref: str | None

    readability: dict
    metadata: dict
```

SliceDone is:

```text
the readable established result of Slice
```

It is not merely:

```text
execution finished
X + Δ only
```

Boundary-aware does not mean Boundary-required.

All Boundary-related collections may be empty.

---

## 12. BoundaryEvidence

```python
class BoundaryEvidence:
    boundary_id: str
    source_slice_ref: str
    source_process_ref: str

    distinction_type: str
    relation_a_ref: str | None
    relation_b_ref: str | None

    orientation_ref: str
    slice_policy_ref: str
    context_refs: list[str]
    evidence_refs: list[str]

    boundary_readability: float | None
    resolution: str | None
    boundary_origin_mode: str | None

    provisional: bool
    metadata: dict
```

`boundary_origin_mode` is optional metadata:

```text
formed | exposed | retained | unknown
```

The canonical statement remains:

```text
The distinction became readable through the current Slice.
```

---

## 13. BoundaryStateRecord

```python
class BoundaryStateRecord:
    boundary_state_id: str

    boundary_ref: str
    relation_ref: str | None
    slice_ref: str
    process_ref: str
    trajectory_ref: str | None

    state_type: str
    boundary_state_confidence: float | None
    relation_readability: float | None
    inferability: float | None

    evidence_refs: list[str]
    context_refs: list[str]
    orientation_ref: str | None

    provisional: bool
    lineage_refs: list[str]
    supersedes_for_current_scope_ref: str | None
    metadata: dict
```

Initial candidate vocabulary:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

The first PoC may implement only:

```text
NORMAL
UNKNOWN
VOID
```

This subset is not a closed GyroOS enum.

A `VOID` Boundary State requires:

```text
the relevant Boundary is identifiable
+
the target relation is not sufficiently readable or connectable relative to it
```

If the Boundary itself is unreadable, preserve unclassified Boundary evidence instead of forcing `VOID`.

---

## 14. ContextEvidence

```python
class ContextEvidence:
    context_id: str
    source_slice_ref: str
    source_process_ref: str

    relation_refs: list[str]
    inferred_structure_ref: str | None
    source_type: str

    context_readability: float | None
    context_confidence: float | None
    inferability_score: float | None

    inference_basis_refs: list[str]
    resolution: str | None
    provisional: bool
    metadata: dict
```

Context may become a Re-Slice source candidate.

It does not automatically trigger `RESLICE`.

---

## 15. VoidEvidence

```python
class VoidEvidence:
    void_id: str
    source_slice_ref: str
    source_process_ref: str

    boundary_ref: str | None
    relation_ref: str | None

    reason: str
    relation_readability: float | None
    inferability: float | None
    connectability: float | None

    evidence_refs: list[str]
    context_refs: list[str]
    provisional: bool
    metadata: dict
```

Do not include:

```python
deferred: bool
resolved: bool
```

because:

```text
VoidEvidence
≠ DEFER response
≠ Deferred relation
```

Defer status belongs to a separate continuity or deferred-relation record.

---

## 16. StabilityResult

```python
class StabilityResult:
    process_id: str
    slice_ref: str

    value: float | None
    status: str
    continuability: bool | None
    reason: str | None

    evidence_refs: list[str]
    metadata: dict
```

Candidate status values:

```text
stable
adaptive
unstable
not_evaluable
void_related
```

Important:

```text
StabilityResult
≠ OperatorResponse
continuability
≠ CONTINUE
```

The following values must remain separate:

```text
boundary_readability
boundary_state_confidence
context_confidence
stability
response_confidence
```

---

## 17. OperatorResponse

```python
class OperatorResponse:
    response_id: str
    process_id: str

    response_type: str
    reason: str

    considered_evidence_refs: list[str]
    decisive_evidence_refs: list[str]
    conflicting_evidence_refs: list[str]

    response_confidence: float | None
    next_request: SliceRequest | None
    update_decision_ref: str | None
    metadata: dict
```

Canonical response vocabulary:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Compatibility aliases only:

```text
RESLICE_CONTEXT → RESLICE with Context source refs
CHANGE_ORIENTATION → ADJUST
DEFER_VOID → DEFER with Void-related evidence
```

`VOID` is not an Operator Response.

No direct universal mappings are allowed:

```text
NORMAL → CONTINUE
UNKNOWN → RESLICE
VOID → DEFER
low Stability → STOP
large Δ → JUMP
```

A deterministic PoC rule must combine multiple evidence inputs.

---

## 18. UpdateDecision

```python
class UpdateDecision:
    update_decision_id: str
    process_id: str
    response_ref: str

    update_type: str
    previous_orientation_ref: str | None
    next_orientation: OperatorOrientation | None
    next_slice_policy: SlicePolicy | None

    reason: str
    metadata: dict
```

UpdateEngine applies an already selected response effect.

It does not select OperatorResponse.

`ADJUST` may produce an orientation or Slice Policy update.

---

## 19. RuntimeContinuityResult

```python
class RuntimeContinuityResult:
    continuity_id: str
    process_id: str
    response_ref: str

    continuity_type: str
    source_ref: str
    target_ref: str | None

    pending: bool
    terminated_for_current_scope: bool
    evidence_refs: list[str]
    metadata: dict
```

Candidate continuity types:

```text
direct_connection
adjusted_connection
reslice_connection
jump_reconnection
deferred_pending_relation
stopped_for_current_scope
```

OperatorResponse selects the disposition.

RuntimeContinuityResult records the resulting connection relation.

---

## 20. MemoryRuntime

```python
class MemoryRuntime:
    runtime_structure_records: dict[str, RuntimeStructure]
    slice_done_records: dict[str, "SliceDoneRecord"]
    deviation_records: dict[str, "DeviationRecord"]

    boundary_records: dict[str, BoundaryEvidence]
    boundary_state_records: dict[str, BoundaryStateRecord]
    context_records: dict[str, ContextEvidence]
    void_records: dict[str, VoidEvidence]

    stability_records: dict[str, "StabilityRecord"]
    response_records: dict[str, "OperatorResponseRecord"]
    continuity_records: dict[str, "ContinuityRecord"]
    deferred_relation_records: dict[str, "DeferredRelationRecord"]

    def record_process_result(self, result: "LoopStepResult") -> None:
        ...

    def retrieve_source(self, source_ref: str) -> object:
        ...

    def compress(self, target_ref: str, level: str) -> None:
        ...
```

Memory Runtime preserves evidence and lineage.

It does not:

```text
select RESLICE
select DEFER
select JUMP
select STOP
classify Stability
```

---

## 21. SliceDoneRecord

```python
class SliceDoneRecord:
    slice_id: str
    process_ref: str

    representation_ref: str
    deviation_ref: str

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    parent_slice_ref: str | None
    trajectory_ref: str | None

    resolution_level: str
    storage_tier: str
    metadata: dict
```

The record may retain references rather than full embedded evidence.

---

## 22. DeferredRelationRecord

```python
class DeferredRelationRecord:
    deferred_relation_id: str
    source_process_ref: str
    source_response_ref: str

    retained_relation_refs: list[str]
    void_refs: list[str]

    deferred_at_process_index: int
    revisit_condition: dict | None
    current_scope_active: bool
    metadata: dict
```

This object stores the effect of `DEFER`.

It must not be merged into `VoidEvidence`.

---

## 23. TrajectoryCache

```python
class TrajectoryCache:
    entries: dict[str, "TrajectoryCacheEntry"]
    edges: dict[str, "TrajectoryEdge"]
    current_scope_views: dict[str, "TrajectoryCurrentScopeView"]

    def record_step(self, result: "LoopStepResult") -> None:
        ...

    def locate_source_refs(self, query: dict) -> list[str]:
        ...

    def retrieve(self, trajectory_id: str) -> "TrajectoryCacheEntry":
        ...
```

Trajectory Cache indexes continuity evidence.

It does not decide the next Process.

---

## 24. TrajectoryCacheEntry

```python
class TrajectoryCacheEntry:
    trajectory_id: str

    process_refs: list[str]
    slice_refs: list[str]
    structure_refs: list[str]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    stability_refs: list[str]
    response_refs: list[str]
    continuity_refs: list[str]

    edge_refs: list[str]
    branch_refs: list[str]

    stability_summary: dict
    deviation_summary: dict
    boundary_summary: dict
    continuity_summary: dict

    resolution_level: str
    storage_tier: str
    metadata: dict
```

Trajectory history must not be reduced to only its latest state.

---

## 25. TrajectoryEdge

```python
class TrajectoryEdge:
    edge_id: str
    trajectory_ref: str

    source_process_ref: str
    target_process_ref: str | None
    response_ref: str
    continuity_ref: str

    relation_type: str
    evidence_refs: list[str]
    metadata: dict
```

Candidate relation types:

```text
direct_continue
bounded_adjustment
reslice_from_retained_source
jump_branch
deferred_pending
stopped_for_current_scope
reclassified_from
conflicts_with
coexists_with
```

---

## 26. DamperState and Pressure Signals

```python
class DamperState:
    memory_pressure: float
    hot_tier_overflow: bool
    lineage_growth: int
    context_chain_growth: int
    reslice_depth: int
    trajectory_branch_count: int
    void_evidence_accumulation: int
    cycle_detected: bool
    evidence_refs: list[str]
    metadata: dict
```

DamperState emits pressure evidence only.

It does not select:

```text
RESLICE
DEFER
JUMP
STOP
```

Storage-level actions may include:

```text
RESOLUTION_DECAY
CONTEXT_COMPRESSION
TRAJECTORY_COMPRESSION
COLD_ARCHIVE
INDEX_REBUILD
SOURCE_MATERIALIZATION
```

The following are requests or signals to LoopController, not Damper actions:

```text
limit reached
jump may be considered
stop may be considered
defer may be considered
```

---

## 27. Engine Responsibilities

### SliceEngine

```text
Input: SliceRequest
Output: SliceDone
```

Responsibilities:

```text
execute slice-ing
produce representation
produce Difference / Deviation
preserve readable Boundary evidence
preserve classifiable Boundary State records
preserve Context and Void evidence
```

### StabilityEngine

```text
Input: SliceDone
Output: StabilityResult
```

It reads whether the opened Path is a continuing establishment.

It does not control the Loop.

### LoopController

```text
Input:
  SliceDone
  StabilityResult
  LoopState
  trajectory evidence
  Runtime limits

Output:
  OperatorResponse
```

LoopController is the only owner of response selection.

### UpdateEngine

```text
Input: selected OperatorResponse + current Runtime configuration
Output: UpdateDecision
```

It applies bounded continuous modification when required.

### ReSliceEngine

```text
Input: SliceRequest(mode="reslice")
Output: new SliceDone
```

It executes an already selected `RESLICE` request.

It does not self-trigger.

### MemoryRuntime

```text
Input: Runtime records and retrieval requests
Output: retained or materialized evidence
```

It preserves and retrieves.

It does not select responses.

### TrajectoryCache

```text
Input: Process, response, continuity, and lineage records
Output: indexed trajectory evidence
```

It records connectability changes and branch relations.

---

## 28. `/loop/step` Execution Graph

```text
RuntimeStructure
↓
GyroRuntime.loop_step
↓
Create GyroProcess
↓
Create SliceRequest
↓
SliceEngine.execute
↓
SliceDone
↓
StabilityEngine.read
↓
StabilityResult
↓
LoopController.respond
↓
OperatorResponse
↓
UpdateEngine or ReSlice request preparation if applicable
↓
RuntimeContinuityResult
↓
MemoryRuntime.record_process_result
↓
TrajectoryCache.record_step
↓
LoopStepResult
```

`RESLICE` normally prepares the next request.

A bounded demo may execute that request in a subsequent `/loop/step` call.

---

## 29. LoopStepResult

```python
class LoopStepResult:
    loop_id: str
    process_id: str
    process_index: int

    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    continuity: RuntimeContinuityResult

    update_decision: UpdateDecision | None
    pressure_evidence_refs: list[str]

    trajectory_id: str
    next_process_ready: bool
    metadata: dict
```

The result must preserve the conceptual object separation.

---

## 30. Minimal First PoC Object Set

Required:

```text
RuntimeStructure
OperatorOrientation
SlicePolicy
SliceRequest
SliceDone
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityResult
OperatorResponse
RuntimeContinuityResult
LoopState
MemoryRuntime
TrajectoryCache
LoopStepResult
```

Recommended Boundary State subset:

```text
NORMAL
UNKNOWN
VOID
```

Optional later:

```text
DynamicEquivalenceRuntime
LocalInertiaPolicy
ExternalStorageReference
full Boundary lineage graph
persistent database
```

---

## 31. Minimum Demo Scenarios

### Scenario 1: Readable Boundary

```text
Boundary readable
Boundary State NORMAL
Stability continuable
OperatorResponse CONTINUE
```

This is a policy scenario, not a universal mapping.

### Scenario 2: Unknown Relation

```text
Boundary readable
Boundary State UNKNOWN
additional Context source available
OperatorResponse RESLICE
```

The response must cite multiple evidence inputs.

### Scenario 3: Void-related Pending Relation

```text
relevant Boundary identifiable
target relation unreadable or unconnectable
Boundary State VOID
VoidEvidence retained
OperatorResponse DEFER
```

`VOID` does not execute `DEFER`.

### Scenario 4: Conflicting Boundary Evidence

```text
multiple BoundaryEvidence records
conflict retained
bounded recovery possible or reconstruction required
OperatorResponse ADJUST or JUMP
```

Use one response per execution branch.

---

## 32. Design Constraints

The PoC object graph MUST NOT:

```text
redefine Structure → Slice → Stability
place Operator Orientation outside Slice conceptually
reduce SliceDone to X + Δ only
collapse Boundary State into Stability
collapse VoidEvidence into DEFER
use VOID as OperatorResponse
let UpdateEngine, ReSliceEngine, MemoryRuntime, TrajectoryCache, or Damper select responses
auto-trigger Re-Slice from Context or Boundary State
silently overwrite prior Boundary State records
erase Difference / Deviation or Void evidence
mix GyroAuth application decisions into GyroOS
```

The PoC object graph MUST:

```text
preserve SliceDone / StabilityResult / OperatorResponse / Continuity separation
use CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
preserve evidence references and lineage
retain Boundary, Context, Void, response, and continuity history
support current-scope views without deleting history
keep execution bounded
return an inspectable LoopStepResult
```

---

## 33. Key Insight

The PoC should implement the smallest graph that makes the responsibility chain visible:

```text
Slice makes relations readable.
Stability reads the opened Path.
LoopController selects the connection disposition.
Runtime Continuity records the resulting relation.
Memory and Trajectory preserve how that reading changed.
```

---

## 34. Summary

This object graph is the implementation bridge from the GyroOS Runtime design to the bounded PoC.

It preserves:

```text
Structure → Slice → Stability
```

and implements:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Runtime Continuity relation
→ Gyro Processₙ₊₁ when applicable
```

---

## 35. Next

```text
Priority D-9: docs/27_claude_poc_implementation_prompt.md Alignment
```