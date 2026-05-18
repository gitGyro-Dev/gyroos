# 15. Context Runtime

---

## Overview

This document defines how **Context** from Gyro Logic v2.7 is represented in GyroOS runtime.

GyroOS does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

Context is an auxiliary runtime field that appears around a completed Slice result.

It does not replace Structure, Slice, Representation, Deviation, or Stability.

---

## Theoretical Definition

In Gyro Logic v2.7:

```text
Context = surrounding Structure that was not explicitly represented by Slice,
but remains inferable by the Operator.
```

Context is therefore:

```text
operator-relative
slice-dependent
provisional
inferred
incomplete
```

Context is not the same as Representation.

Context is not the same as Void.

---

## Runtime Position

GyroOS runtime flow:

```text
Structure
→ Operator Orientation
→ slice-ing
→ slice-done
→ Stability
→ Operator Response
→ Next Process
```

Context appears with `slice-done`.

```text
slice-done = X + Δ + C + V + M
```

where:

```text
X = representation
Δ = deviation
C = context
V = void / unresolved region
M = metadata
```

However, this notation must not be read as changing the core formula:

```text
slice-done = X + Δ
```

Instead, GyroOS may store additional runtime fields alongside the completed Slice result.

---

## Recommended Runtime Model

Use `SliceDone` to store the completed Slice result and its runtime surroundings.

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

Stability should remain a separate measured result.

```python
class StabilityResult:
    process_index: int
    value: float | None
    status: str
    reason: str | None
```

This separation keeps the architecture clean:

```text
slice-done → Stability Engine → StabilityResult
```

---

## Context Field

The `context` field may contain inferred surrounding information.

Example:

```python
context = {
    "inferred_relations": [],
    "surrounding_signals": {},
    "unobserved_candidates": [],
    "confidence": 0.72,
    "source": "operator_inferred"
}
```

Context may include:

```text
nearby relations
unobserved dimensions
implicit structure
operator assumptions
surrounding signals
possible next Slice targets
```

---

## Context Confidence

Because Context is inferred, it should carry confidence or inferability metadata.

Recommended fields:

```text
context_confidence
inferability_score
source_type
inference_basis
```

Example:

```python
class ContextState:
    context_id: str
    source_slice_id: str
    inferred_structure: dict
    confidence: float
    inferability_score: float
    source_type: str
    metadata: dict
```

---

## Relation to Representation

Representation is what Slice explicitly produced.

```text
X = explicitly represented result
```

Context is what surrounds or supports that representation but was not directly sliced.

```text
C = inferred surrounding structure
```

Incorrect:

```text
Context = Representation
```

Correct:

```text
Representation is explicit.
Context is inferred.
```

---

## Relation to Deviation

Deviation is the gap between Structure and Representation.

```text
Δ = deviation between Structure and Representation
```

Context may explain or qualify deviation, but it is not deviation itself.

Examples:

```text
large Δ with high-context confidence → possible hidden structure
large Δ with low-context confidence → possible void
small Δ with strong context → stable surrounding structure
```

---

## Relation to Void

Void is an unresolved or non-inferable region.

Context is inferable surrounding structure.

```text
Context = inferable surrounding structure
Void = non-inferable unresolved region
```

Incorrect:

```text
Context = Void
```

Correct:

```text
Context may become a Re-Slice target.
Void may be deferred, held, or trigger Jump through Operator Response.
```

---

## Relation to Operator Response

Context does not decide the next process by itself.

Stability does not decide the next process by itself.

The Loop Controller implements Operator Response.

Correct relation:

```text
slice-done
→ Stability
→ Loop Controller / Operator Response
→ CONTINUE | RESLICE_CONTEXT | DEFER_VOID | JUMP | STOP
```

Context may be selected by Operator Response as the next target.

```text
Operator Response → RESLICE_CONTEXT → Re-Slice Engine
```

---

## Re-Slice Candidate

Context can become a candidate target for Re-Slice.

Example:

```python
class ReSliceCandidate:
    candidate_id: str
    source_context_id: str
    source_slice_id: str
    reason: str
    priority: float
    confidence: float
```

Context should not automatically trigger Re-Slice.

Correct:

```text
Context exists → Operator Response may select RESLICE_CONTEXT
```

Incorrect:

```text
Context exists → Re-Slice automatically starts
```

---

## Runtime Flow with Context

```text
Structure
   ↓
Operator Orientation
   ↓
slice-ing
   ↓
SliceDone {
  representation: X,
  deviation: Δ,
  context: C,
  void: V,
  metadata: M
}
   ↓
Stability Engine
   ↓
StabilityResult
   ↓
Loop Controller / Operator Response
   ├─ CONTINUE
   ├─ RESLICE_CONTEXT
   ├─ CHANGE_ORIENTATION
   ├─ DEFER_VOID
   ├─ JUMP
   └─ STOP
```

---

## API Implications

`POST /loop/step` may return Context in the response.

Example:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 7,
  "slice_done": {
    "representation": {},
    "deviation": {},
    "context": {
      "confidence": 0.72,
      "inferred_relations": []
    },
    "void": null,
    "metadata": {}
  },
  "stability": {
    "value": 0.84,
    "status": "stable"
  },
  "operator_response": {
    "response_type": "continue"
  }
}
```

---

## Design Constraints

Context Runtime MUST NOT:

```text
redefine Structure → Slice → Stability
treat Context as Representation
treat Context as Void
treat Context as Stability
automatically trigger Re-Slice
make Context the loop controller
mix GyroAuth authentication logic into GyroOS
```

Context Runtime MUST:

```text
preserve Context as inferred surrounding structure
store Context with slice-done runtime data
allow Context to become a Re-Slice candidate
keep Stability separate as measured state quantity
let Loop Controller / Operator Response decide next action
```

---

## Key Insight

Context is not what was sliced.

Context is what remains inferable around what was sliced.

In short:

```text
Representation is explicit.
Context is inferred.
Void is unresolved.
```

---

## Summary

Context Runtime extends GyroOS by allowing `slice-done` to carry inferred surrounding structure.

It enables future Re-Slice and Context Loop behavior without changing the invariant core:

```text
Structure → Slice → Stability
```

Context is stored, evaluated, and possibly selected as a future target by Operator Response.

---

## Next

```text
docs/16_reslice_engine.md
```
