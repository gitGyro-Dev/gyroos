# 26. PoC Runtime Object Graph

---

## Overview

This document defines a minimal runtime object graph for a GyroOS PoC implementation.

The goal is to make GyroOS concepts implementable without collapsing the theory.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

The PoC should implement runtime expansion:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

This document is intended to guide coding, class design, runtime state storage, and demo implementation.

---

## PoC Scope

The PoC should be minimal.

It does not need to implement full OS behavior.

It should demonstrate:

```text
Structure input
Operator Orientation
slice-ing
SliceDone = X + Δ + Context / Void
StabilityResult
Operator Response
Re-Slice / Defer / Jump / Stop decisions
Memory Runtime
Trajectory Cache
Local Inertia
Gyro-OOM Damper signals
```

---

## Core Object Graph

```text
GyroRuntime
├─ LoopState
│  ├─ current_process: GyroProcess
│  ├─ current_orientation: OperatorOrientation
│  ├─ memory: MemoryRuntime
│  ├─ trajectory_cache: TrajectoryCache
│  └─ damper_state: DamperState
│
├─ Engines
│  ├─ SliceEngine
│  ├─ StabilityEngine
│  ├─ LoopController
│  ├─ UpdateEngine
│  ├─ ReSliceEngine
│  └─ DynamicEquivalenceRuntime
│
└─ Records
   ├─ SliceDoneRecord
   ├─ ContextRecord
   ├─ VoidRecord
   ├─ TrajectoryRecord
   ├─ StabilityRecord
   ├─ DeviationRecord
   └─ OperatorResponseRecord
```

---

## Main Runtime Classes

### GyroRuntime

```python
class GyroRuntime:
    loop_state: LoopState
    slice_engine: SliceEngine
    stability_engine: StabilityEngine
    loop_controller: LoopController
    update_engine: UpdateEngine
    reslice_engine: ReSliceEngine
    equivalence_runtime: DynamicEquivalenceRuntime

    def loop_step(self, structure: "Structure") -> "LoopStepResult":
        ...
```

Role:

```text
Orchestrates one /loop/step execution.
Does not redefine theory.
Does not make application decisions.
```

---

### LoopState

```python
class LoopState:
    loop_id: str
    process_index: int
    current_orientation: "OperatorOrientation"

    memory: "MemoryRuntime"
    trajectory_cache: "TrajectoryCache"
    damper_state: "DamperState"

    active_trajectory_id: str | None
    last_response: "OperatorResponse" | None
```

Role:

```text
Stores current runtime state.
Keeps references to memory and trajectory systems.
```

---

### GyroProcess

```python
class GyroProcess:
    process_id: str
    process_index: int
    source_type: str
    source_ref: str | None
    orientation: "OperatorOrientation"
    status: str
```

Possible status:

```text
created
slice_ing
slice_done
stability_measured
responded
completed
stopped
```

---

## Core Data Objects

### Structure

```python
class Structure:
    structure_id: str
    payload: dict
    metadata: dict
```

Structure is the runtime input or source state.

---

### OperatorOrientation

```python
class OperatorOrientation:
    orientation_id: str
    weights: dict[str, float]
    resolution: dict[str, float]
    target_dimensions: list[str]
    constraints: dict
    metadata: dict
```

OperatorOrientation is pre-Slice direction.

It is not Slice itself.

---

### SliceRequest

```python
class SliceRequest:
    request_id: str
    process_index: int
    source_type: str       # structure | context | slice_done | void
    source_ref: str | None
    mode: str              # slice | reslice
    orientation: OperatorOrientation
    parent_process_id: str | None
    parent_slice_id: str | None
    metadata: dict
```

---

### SliceDone

```python
class SliceDone:
    slice_id: str
    process_index: int
    representation: dict
    deviation: dict
    context: dict | None
    void: dict | None
    metadata: dict
```

Important:

```text
SliceDone = completed Slice result.
Stability is measured after SliceDone.
```

---

### StabilityResult

```python
class StabilityResult:
    process_index: int
    value: float | None
    status: str
    reason: str | None
    metadata: dict
```

Possible status:

```text
stable
adaptive
unstable
not_evaluable
void_related
```

---

### OperatorResponse

```python
class OperatorResponse:
    process_index: int
    response_type: str
    reason: str
    next_request: SliceRequest | None
    update_decision: "UpdateDecision" | None
    metadata: dict
```

Recommended response types:

```text
CONTINUE
ADJUST
RESLICE_CONTEXT
DEFER_VOID
JUMP
STOP
```

---

### UpdateDecision

```python
class UpdateDecision:
    update_type: str
    previous_orientation: OperatorOrientation
    next_orientation: OperatorOrientation | None
    reason: str
    metadata: dict
```

---

## Memory Runtime Objects

### MemoryRuntime

```python
class MemoryRuntime:
    slice_done_records: dict[str, SliceDoneRecord]
    context_records: dict[str, ContextRecord]
    void_records: dict[str, VoidRecord]
    stability_records: dict[str, StabilityRecord]
    deviation_records: dict[str, DeviationRecord]
    response_records: dict[str, OperatorResponseRecord]

    def store_slice_done(self, slice_done: SliceDone) -> str:
        ...

    def retrieve_context(self, context_id: str) -> ContextRecord:
        ...

    def compress(self, target_ref: str, level: str) -> None:
        ...
```

---

### SliceDoneRecord

```python
class SliceDoneRecord:
    slice_id: str
    process_index: int
    representation_ref: str
    deviation_ref: str
    context_ref: str | None
    void_ref: str | None
    resolution_level: str
    storage_tier: str
    metadata: dict
```

---

### ContextRecord

```python
class ContextRecord:
    context_id: str
    source_slice_id: str
    source_process_id: str
    inferred_structure: dict
    confidence: float
    inferability_score: float
    context_chain: list[str]
    resolution_level: str
    storage_tier: str
    metadata: dict
```

---

### VoidRecord

```python
class VoidRecord:
    void_id: str
    source_slice_id: str
    source_process_id: str
    reason: str
    inferability: float
    severity: float
    deferred: bool
    resolved: bool
    resolution_level: str
    storage_tier: str
    metadata: dict
```

---

## Trajectory Objects

### TrajectoryCache

```python
class TrajectoryCache:
    entries: dict[str, TrajectoryCacheEntry]
    index: "TrajectoryIndex"

    def append_process(self, trajectory_id: str, process_ref: str) -> None:
        ...

    def retrieve(self, trajectory_id: str) -> "TrajectoryCacheEntry":
        ...

    def compute_local_inertia(self, trajectory_id: str) -> float:
        ...
```

---

### TrajectoryCacheEntry

```python
class TrajectoryCacheEntry:
    trajectory_id: str
    process_refs: list[str]
    slice_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]
    response_refs: list[str]
    stability_summary: dict
    deviation_summary: dict
    orientation_summary: dict
    dynamic_equivalence_evidence: dict
    local_inertia_score: float
    resolution_level: str
    storage_tier: str
    metadata: dict
```

---

## Damper Objects

### DamperState

```python
class DamperState:
    memory_pressure: float
    hot_tier_overflow: bool
    context_chain_growth: int
    reslice_depth: int
    trajectory_branch_count: int
    void_accumulation: int
    cycle_detected: bool
    metadata: dict
```

---

### DamperAction

```python
class DamperAction:
    action_type: str
    target_ref: str
    reason: str
    reversible: bool
    metadata: dict
```

Possible action types:

```text
RESOLUTION_DECAY
CONTEXT_COMPRESSION
TRAJECTORY_COMPRESSION
DEFER_VOID
LIMIT_RESLICE
BRANCH_FREEZE
COLD_ARCHIVE
REQUEST_JUMP
REQUEST_STOP
```

---

## Engine Responsibilities

### SliceEngine

```text
Input: SliceRequest
Output: SliceDone
```

Does:

```text
executes slice-ing
produces representation X
produces deviation Δ
may produce Context / Void
```

---

### StabilityEngine

```text
Input: SliceDone
Output: StabilityResult
```

Does not control the loop.

---

### LoopController

```text
Input: SliceDone + StabilityResult + LoopState
Output: OperatorResponse
```

Owns response decision.

---

### UpdateEngine

```text
Input: OperatorResponse + current Orientation
Output: UpdateDecision
```

Applies response when needed.

Does not decide the response.

---

### ReSliceEngine

```text
Input: SliceRequest(mode="reslice")
Output: SliceDone
```

Runs only when Operator Response requests Re-Slice.

---

### DynamicEquivalenceRuntime

```text
Input: state refs + trajectory evidence
Output: equivalent | not_equivalent | undecidable
```

Does not make application decisions.

---

## /loop/step Execution Graph

```text
Structure
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
MemoryRuntime.store_slice_done
   ↓
StabilityEngine.measure
   ↓
StabilityResult
   ↓
LoopController.respond
   ↓
OperatorResponse
   ↓
UpdateEngine / ReSliceEngine / Damper if requested
   ↓
TrajectoryCache.append_process
   ↓
LoopStepResult
```

---

## LoopStepResult

```python
class LoopStepResult:
    loop_id: str
    process_index: int
    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    update_decision: UpdateDecision | None
    damper_actions: list[DamperAction]
    trajectory_id: str
    next_ready: bool
    metadata: dict
```

---

## Minimal PoC Scenario Objects

For the first demo, implement only:

```text
Structure
OperatorOrientation
SliceRequest
SliceDone
StabilityResult
OperatorResponse
LoopState
MemoryRuntime
TrajectoryCache
DamperState
LoopStepResult
```

Optional later:

```text
DynamicEquivalenceRuntime
FluidSession
LocalInertiaPolicy
ExternalStorageReference
```

---

## Design Constraints

PoC Runtime Object Graph MUST NOT:

```text
redefine Structure → Slice → Stability
treat Stability as controller
collapse slice-ing and slice-done
let UpdateEngine decide response
auto-trigger Re-Slice from Context existence
erase Δ or Void silently
make authentication decisions
```

PoC Runtime Object Graph MUST:

```text
preserve runtime flow
separate SliceDone and StabilityResult
make LoopController own Operator Response
store runtime records
append trajectory evidence
report pressure through DamperState
return clear LoopStepResult
```

---

## Key Insight

The PoC should not implement a full OS.

It should implement the smallest object graph that makes GyroOS runtime visible.

In short:

```text
Implement the runtime relation, not the whole operating system.
```

---

## Summary

This object graph provides a minimal implementation bridge from GyroOS theory to PoC runtime.

It preserves the invariant core:

```text
Structure → Slice → Stability
```

and implements runtime expansion:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

---

## Next

```text
Claude PoC implementation prompt
```
