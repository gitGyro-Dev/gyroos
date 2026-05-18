# 18. Void / Defer / Jump

---

## Overview

This document defines how GyroOS handles **Void**, **Defer**, and **Jump** in the runtime layer.

GyroOS does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

Void / Defer / Jump are runtime response patterns around unresolved or non-inferable regions.

They must be handled through Operator Response.

---

## Theoretical Definitions

### Void

```text
Void = region or state that cannot be connected, inferred, or evaluated by the current Slice.
```

Void is not simply an error.

It is an unresolved region relative to the current Slice and Operator Orientation.

---

### Defer

```text
Defer = runtime decision to hold an unresolved Void for later processing.
```

Defer is not failure.

It preserves unresolved material without forcing immediate resolution.

---

### Jump

```text
Jump = non-continuous reconstruction of Orientation / Slice / Structure mapping.
```

Jump is used when continuous adjustment or Re-Slice is insufficient.

---

## Core Constraint

Void does not act.

Stability does not decide.

Update Engine does not initiate Jump.

Correct relation:

```text
slice-done
→ Stability
→ Loop Controller / Operator Response
→ DEFER_VOID | JUMP | CHANGE_ORIENTATION | STOP
```

Incorrect relation:

```text
Void → Jump
Stability → Jump
Update Engine → Jump
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
→ DEFER_VOID | JUMP | STOP | CHANGE_ORIENTATION
→ Next Process
```

Void appears in or around SliceDone.

Operator Response decides what to do with it.

---

## VoidState Model

```python
class VoidState:
    void_id: str
    source_slice_id: str
    source_process_id: str

    reason: str
    inferability: float
    severity: float

    deferred: bool
    resolved: bool

    metadata: dict
```

Recommended reason values:

```text
non_inferable
low_stability
missing_context
conflicting_context
excessive_deviation
cycle_detected
unknown_relation
```

---

## Operator Decisions

Void-related decisions are made by Loop Controller / Operator Response.

Recommended decision types:

```text
CONTINUE
DEFER_VOID
RESLICE_CONTEXT
CHANGE_ORIENTATION
JUMP
STOP
```

---

## DEFER_VOID

### Meaning

```text
DEFER_VOID = preserve unresolved Void without resolving it immediately.
```

### Use when

```text
Void exists
inferability is low
immediate Re-Slice is not useful
Jump is too costly or premature
future context may clarify the Void
```

### Runtime effect

```text
VoidState.deferred = true
Void is stored in LoopState.deferred_voids
Process continues or waits depending on Operator Response
```

Example:

```python
class DeferredVoid:
    void_id: str
    deferred_at_process: int
    reason: str
    revisit_condition: dict | None
```

---

## JUMP

### Meaning

```text
JUMP = non-continuous reconstruction of Orientation / Slice / Structure mapping.
```

Jump is not normal adjustment.

Jump is selected when continuous responses fail.

---

### Use when

```text
repeated low Stability
Void expansion
Context Loop cycle detected
Re-Slice depth exceeded
trajectory collapse
orientation no longer viable
```

---

### Runtime effect

Jump may produce:

```text
new Operator Orientation
new Slice Policy
new source target
new process branch
reset of context chain
```

Jump must preserve history.

It should not erase prior Void or Deviation.

---

## STOP

### Meaning

```text
STOP = runtime decision to terminate or suspend process repetition.
```

STOP is not part of the timeless Gyro Unit.

It is a runtime control response.

---

### Use when

```text
explicit stop requested
cost budget exceeded
max depth exceeded
unrecoverable Void
policy requires termination
```

---

## CHANGE_ORIENTATION

### Meaning

```text
CHANGE_ORIENTATION = modify Operator Orientation without non-continuous Jump.
```

This is a continuous adjustment.

It differs from Jump.

---

### Use when

```text
current Orientation cannot read Context well
Deviation remains high but inferability exists
Re-Slice may work under different Orientation
```

---

## Relation to Stability

Stability may indicate that the current SliceDone is unstable or non-evaluable.

However:

```text
Stability does not choose DEFER_VOID.
Stability does not choose JUMP.
Stability does not choose STOP.
```

The Loop Controller uses Stability as one input to Operator Response.

---

## Relation to Context Loop

Context Loop may encounter Void.

```text
Context Loop
→ Re-Slice
→ SliceDone
→ Void detected
→ Operator Response
```

The controller may decide:

```text
DEFER_VOID
CHANGE_ORIENTATION
JUMP
STOP
```

Context Loop must not recurse indefinitely to avoid Void.

---

## Runtime Flow

```text
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
   ├─ CONTINUE
   ├─ DEFER_VOID
   ├─ RESLICE_CONTEXT
   ├─ CHANGE_ORIENTATION
   ├─ JUMP
   └─ STOP
```

---

## API Implications

`POST /loop/step` may return Void-related response data.

Example:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 12,
  "slice_done": {
    "representation": {},
    "deviation": {},
    "context": null,
    "void": {
      "void_id": "void_012",
      "reason": "non_inferable",
      "inferability": 0.18,
      "severity": 0.82
    }
  },
  "stability": {
    "value": null,
    "status": "not_evaluable"
  },
  "operator_response": {
    "response_type": "DEFER_VOID",
    "reason": "void is not currently inferable; preserve for later context"
  }
}
```

---

## Design Constraints

Void / Defer / Jump handling MUST NOT:

```text
redefine Structure → Slice → Stability
treat Void as an actor
treat Void as simple error
automatically convert Void to Jump
automatically convert low Stability to STOP
erase Void history
erase Deviation history
mix GyroAuth authentication failure into GyroOS core
```

Void / Defer / Jump handling MUST:

```text
preserve unresolved regions
make decisions through Operator Response
track deferred voids
support Jump as non-continuous reconstruction
support Stop as runtime control
preserve history and lineage
```

---

## Key Insight

Void is not failure.

Void is unresolved structure relative to the current Slice.

In short:

```text
Void is held.
Defer preserves.
Jump reconstructs.
Operator Response decides.
```

---

## Summary

GyroOS handles Void, Defer, and Jump as runtime response mechanisms.

They do not modify the invariant core:

```text
Structure → Slice → Stability
```

They are controlled through:

```text
StabilityResult
→ Loop Controller / Operator Response
→ DEFER_VOID | JUMP | STOP
```

---

## Next

```text
docs/19_dynamic_equivalence_runtime.md
```
