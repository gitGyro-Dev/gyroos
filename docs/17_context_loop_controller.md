# 17. Context Loop Controller

---

## Overview

This document defines how GyroOS controls **Context Loop** execution.

Context Loop is a special case of Gyro Loop in which Context produced by a completed Slice becomes the target of a subsequent Re-Slice.

GyroOS does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

Context Loop is an implementation-level runtime pattern.

---

## Theoretical Definition

In Gyro Logic v2.7:

```text
Context Loop = a Gyro Loop connected by treating Context as a Re-Slice target.
```

Core form:

```text
Process_n
→ SliceDone_n
→ Context_n
→ OperatorResponse_n
→ ReSlice(Context_n)
→ Process_{n+1}
```

---

## Relation to Gyro Loop

Base Gyro Loop:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

Context Loop is not a different core structure.

It is a Gyro Loop where the next process source is Context.

```text
Gyro Processₙ
→ Operator Responseₙ(RESLICE_CONTEXT)
→ ReSlice(Contextₙ)
→ Gyro Processₙ₊₁
```

---

## Runtime Position

```text
Structure
→ Operator Orientation
→ slice-ing
→ SliceDone {
     representation: X,
     deviation: Δ,
     context: C,
     void: V
  }
→ Stability
→ Loop Controller / Operator Response
→ RESLICE_CONTEXT
→ Re-Slice Engine
→ Next Process
```

The Context Loop Controller is not a separate theoretical controller.

It is a Loop Controller responsibility specialized for Context.

---

## Responsibilities

### 1. Detect Context Availability

The controller checks whether `SliceDone.context` exists and whether it is inferable enough to become a Re-Slice candidate.

Example:

```python
if slice_done.context and slice_done.context["confidence"] >= context_threshold:
    candidate_available = True
```

However, availability does not automatically trigger Re-Slice.

---

### 2. Select Operator Response

The Loop Controller decides the next response.

Possible responses include:

```text
CONTINUE
RESLICE_CONTEXT
CHANGE_ORIENTATION
DEFER_VOID
JUMP
STOP
```

Context Loop begins only when Operator Response selects:

```text
RESLICE_CONTEXT
```

---

### 3. Create Re-Slice Request

When `RESLICE_CONTEXT` is selected, the controller creates a Re-Slice request.

```python
class SliceRequest:
    request_id: str
    source_type: str   # "context"
    source_ref: str
    mode: str          # "reslice"
    orientation: OperatorOrientation
    parent_process_id: str
    parent_slice_id: str
```

---

### 4. Track Context Chain

Context Loops may form chains.

```text
Context_1 → Context_2 → Context_3 → ...
```

The controller must track this chain.

Recommended fields:

```text
context_chain
source_context_id
parent_process_id
reslice_depth
loop_depth
```

---

### 5. Prevent Uncontrolled Recursion

Context Loop must not recurse without limit.

The controller should enforce:

```text
max_reslice_depth
max_context_chain_length
cycle detection
time budget
cost budget
```

If recursion risk appears, the controller may select:

```text
STOP
DEFER_VOID
CHANGE_ORIENTATION
JUMP
```

---

### 6. Handle Void and Defer

Context Loop may encounter Void.

Void is not an actor.

The controller decides how to respond.

Possible responses:

```text
DEFER_VOID
JUMP
CHANGE_ORIENTATION
STOP
```

---

## Data Model

### ContextLoopState

```python
class ContextLoopState:
    loop_id: str
    process_index: int

    active: bool
    source_context_id: str | None
    parent_process_id: str | None
    parent_slice_id: str | None

    context_chain: list[str]
    reslice_depth: int
    max_reslice_depth: int

    cycle_detected: bool
    deferred_voids: list[str]
    metadata: dict
```

---

### ContextLoopDecision

```python
class ContextLoopDecision:
    process_index: int
    decision: str  # CONTINUE | RESLICE_CONTEXT | DEFER_VOID | JUMP | STOP
    reason: str
    next_request: SliceRequest | None
    updated_context_loop_state: ContextLoopState
```

---

## Decision Inputs

The controller may consider:

```text
StabilityResult
Deviation
Context confidence
Context inferability
VoidState
Re-Slice depth
Context chain length
History
Cost
Purpose
```

Example input structure:

```python
class ContextResponseInput:
    stability: StabilityResult
    deviation: dict
    context: ContextState | None
    void: VoidState | None
    reslice_depth: int
    context_chain: list[str]
    history: dict
    cost_budget: float | None
    purpose: str | None
```

---

## Decision Rules

### Continue

Use when current process is stable and Context does not need further exploration.

```text
high Stability
low Δ
Context not required
```

---

### RESLICE_CONTEXT

Use when Context is sufficiently inferable and may explain unresolved deviation or improve stability.

```text
Context confidence is high
Δ remains meaningful
Void is not dominant
reslice_depth < max_reslice_depth
```

---

### DEFER_VOID

Use when Void exists but is not currently inferable.

```text
Void detected
low inferability
Re-Slice not useful yet
```

---

### CHANGE_ORIENTATION

Use when the current orientation is not adequate.

```text
Context exists but current orientation cannot read it well
```

---

### JUMP

Use when continuous Re-Slice or orientation change cannot restore stable trajectory.

```text
cycle detected
repeated low stability
context chain collapse
void expansion
```

---

### STOP

Use when external or runtime constraints require stopping.

```text
cost limit reached
max depth reached
explicit stop requested
```

---

## Runtime Flow

```text
Process_n
   ↓
SliceDone_n {
  representation: X,
  deviation: Δ,
  context: C,
  void: V
}
   ↓
StabilityResult_n
   ↓
Loop Controller
   ↓
Context Loop Decision
   ├─ CONTINUE
   ├─ RESLICE_CONTEXT
   ├─ DEFER_VOID
   ├─ CHANGE_ORIENTATION
   ├─ JUMP
   └─ STOP
   ↓
Next Process
```

If `RESLICE_CONTEXT`:

```text
Context_n
→ SliceRequest(mode="reslice", source_type="context")
→ Re-Slice Engine
→ SliceDone_{n+1}
```

---

## API Implications

`POST /loop/step` remains the main runtime endpoint.

It may return a context loop state.

Example:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 9,
  "operator_response": {
    "response_type": "RESLICE_CONTEXT",
    "reason": "context may explain unresolved deviation"
  },
  "context_loop": {
    "active": true,
    "source_context_id": "ctx_009",
    "reslice_depth": 1,
    "context_chain": ["ctx_007", "ctx_009"],
    "cycle_detected": false
  },
  "next_request": {
    "mode": "reslice",
    "source_type": "context",
    "source_ref": "ctx_009"
  }
}
```

---

## Relation to Re-Slice Engine

Context Loop Controller decides.

Re-Slice Engine executes.

Correct relation:

```text
Loop Controller / Operator Response
→ RESLICE_CONTEXT
→ Re-Slice Engine
```

Incorrect relation:

```text
Re-Slice Engine
→ decides to continue Context Loop
```

---

## Relation to Stability

Stability is an input to Operator Response.

Stability does not decide Context Loop.

Correct relation:

```text
StabilityResult
→ Loop Controller
→ Context Loop Decision
```

Incorrect relation:

```text
StabilityResult
→ Context Loop automatically starts
```

---

## Design Constraints

The Context Loop Controller MUST NOT:

```text
redefine Structure → Slice → Stability
treat Context Loop as a new theory core
auto-trigger from Context existence
auto-trigger from Stability alone
allow unlimited Re-Slice recursion
treat Void as an actor
mix GyroAuth authentication logic into GyroOS
```

The Context Loop Controller MUST:

```text
remain part of Loop Controller responsibility
select RESLICE_CONTEXT only through Operator Response
track context_chain
track reslice_depth
prevent cycles
support DEFER_VOID
support JUMP and STOP
preserve parent process linkage
```

---

## Key Insight

Context Loop is not a different loop.

It is a Gyro Loop whose next Slice target is Context.

In short:

```text
Gyro Loop repeats Process.
Context Loop repeats Process through Context.
```

---

## Summary

The Context Loop Controller allows GyroOS to follow inferred Context across Processes without changing the invariant core.

It is controlled by Operator Response, not Stability.

It enables Context-aware runtime behavior while preserving:

```text
Structure → Slice → Stability
```

---

## Next

```text
docs/18_void_defer_jump.md
```
