# 16. Re-Slice Engine

---

## Overview

The Re-Slice Engine defines how GyroOS performs a secondary Slice over an existing runtime result, especially Context.

GyroOS does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

Re-Slice is an implementation-level runtime mode.

It does not replace Slice.

It applies Slice again to a previously produced runtime target such as Context or SliceDone.

---

## Theoretical Definition

In Gyro Logic v2.7:

```text
Re-Slice = secondary Slice performed over an existing Slice result,
especially Context.
```

Core statement:

```text
Reading Context = Re-Slice over Context
```

---

## Runtime Position

Base GyroOS flow:

```text
Structure
→ Operator Orientation
→ slice-ing
→ slice-done
→ Stability
→ Operator Response
→ Next Process
```

Re-Slice appears only after Operator Response selects it.

Correct relation:

```text
slice-done
→ Stability
→ Loop Controller / Operator Response
→ RESLICE_CONTEXT
→ Re-Slice Engine
→ Next Process
```

Incorrect relation:

```text
Stability
→ Re-Slice Engine
```

Re-Slice is not directly triggered by Stability.

---

## Re-Slice Target

A Re-Slice target may be:

```text
Context
SliceDone
Void-related deferred region
previous Process output
```

Primary target for v2.7:

```text
Context
```

---

## Slice Request Model

Use `SliceRequest` to distinguish initial Slice from Re-Slice.

```python
class SliceRequest:
    request_id: str
    process_index: int

    source_type: str   # "structure" | "context" | "slice_done" | "void"
    source_ref: str

    mode: str          # "slice" | "reslice"
    orientation: OperatorOrientation

    parent_process_id: str | None
    parent_slice_id: str | None
    metadata: dict
```

Important:

```text
mode = "reslice" does not create a new theory.
It marks the runtime source as an existing Slice result or Context.
```

---

## Process Types

Recommended process types:

```text
initial_slice
context_reslice
slice_done_reslice
void_reslice
orientation_reslice
```

### initial_slice

A first Slice over Structure.

### context_reslice

A Re-Slice over inferred Context.

### slice_done_reslice

A Re-Slice over a full SliceDone result.

### void_reslice

A Re-Slice attempt over a deferred Void region.

### orientation_reslice

A Re-Slice caused by changed Operator Orientation.

---

## Re-Slice Engine Responsibilities

### 1. Accept Re-Slice Requests

The Re-Slice Engine receives requests only from Loop Controller / Operator Response.

```text
Operator Response → Re-Slice Engine
```

It must not self-trigger.

---

### 2. Resolve Source Target

The engine resolves the source:

```text
Context
SliceDone
VoidState
previous runtime result
```

It then prepares that target for slice-ing.

---

### 3. Execute slice-ing

Re-Slice still uses slice-ing.

```text
Re-Slice target
→ Operator Orientation
→ slice-ing
→ slice-done
```

The difference is the source, not the core process.

---

### 4. Produce new SliceDone

Re-Slice produces a new SliceDone.

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

This result is then passed to Stability Engine.

---

### 5. Preserve Parent Linkage

Re-Slice must preserve lineage.

Recommended fields:

```text
parent_process_id
parent_slice_id
source_context_id
reslice_depth
context_chain
```

This allows trajectory and context chain analysis.

---

## Re-Slice Depth

Re-Slice may recurse.

Therefore, GyroOS must control depth.

Recommended fields:

```python
class ReSliceState:
    reslice_depth: int
    max_reslice_depth: int
    context_chain: list[str]
    cycle_detected: bool
```

Constraints:

```text
reslice_depth must have an upper bound
context_chain must be checked for loops
cyclic Re-Slice must be stopped, deferred, or jumped
```

---

## Relation to Context Runtime

Context Runtime stores Context in SliceDone.

Re-Slice Engine consumes Context as source.

```text
SliceDone.context
→ ReSliceCandidate
→ SliceRequest(mode="reslice")
→ Re-Slice Engine
```

Context does not automatically become Re-Slice.

Correct:

```text
Context is available.
Operator Response selects RESLICE_CONTEXT.
Re-Slice Engine executes.
```

Incorrect:

```text
Context exists, therefore Re-Slice starts automatically.
```

---

## Relation to Stability

Stability is measured after Re-Slice produces SliceDone.

```text
Re-Slice Engine
→ slice-done
→ Stability Engine
→ StabilityResult
```

Stability does not start Re-Slice.

Operator Response starts Re-Slice.

---

## Relation to Operator Response

Operator Response decides whether to Re-Slice.

Possible response:

```text
RESLICE_CONTEXT
```

Example response object:

```python
class OperatorResponse:
    process_index: int
    response_type: str  # CONTINUE | RESLICE_CONTEXT | CHANGE_ORIENTATION | DEFER_VOID | JUMP | STOP
    reason: str
    next_request: SliceRequest | None
```

If `response_type == "RESLICE_CONTEXT"`, Loop Controller may create a Re-Slice request.

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
Loop Controller / Operator Response
   ↓
RESLICE_CONTEXT
   ↓
SliceRequest(mode="reslice", source_type="context")
   ↓
Re-Slice Engine
   ↓
slice-ing
   ↓
SliceDone_{n+1}
   ↓
StabilityResult_{n+1}
```

---

## API Implications

`POST /loop/step` may trigger a Re-Slice step when Operator Response selects it.

Example response:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 8,
  "operator_response": {
    "response_type": "RESLICE_CONTEXT",
    "reason": "context has high inferability and unresolved deviation"
  },
  "next_request": {
    "mode": "reslice",
    "source_type": "context",
    "source_ref": "ctx_007"
  }
}
```

Optional lower-level endpoint:

```text
POST /reslice
```

However, `/reslice` should not be the main runtime endpoint.

The main runtime endpoint remains:

```text
POST /loop/step
```

---

## Design Constraints

The Re-Slice Engine MUST NOT:

```text
redefine Structure → Slice → Stability
replace Slice Engine entirely
self-trigger from Stability
self-trigger from Context existence
make Re-Slice the main loop controller
treat Context as Representation
treat Void as Context
mix GyroAuth authentication logic into GyroOS
```

The Re-Slice Engine MUST:

```text
run only when requested by Operator Response
preserve parent linkage
produce a new SliceDone
pass result to Stability Engine
track reslice_depth
prevent uncontrolled recursive Re-Slice
preserve Δ and Context history
```

---

## Key Insight

Re-Slice is not a new core operation.

It is Slice applied again to a runtime result.

In short:

```text
Slice reads Structure.
Re-Slice reads Context or prior Slice result.
```

---

## Summary

The Re-Slice Engine enables GyroOS to process Context without changing the invariant core.

It is selected by Operator Response, executed as a runtime mode, and produces a new SliceDone.

Correct flow:

```text
Operator Response
→ Re-Slice Engine
→ slice-done
→ Stability
```

not:

```text
Stability
→ Re-Slice
```

---

## Next

```text
docs/17_context_loop_controller.md
```
