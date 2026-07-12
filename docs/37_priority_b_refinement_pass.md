# 37. Priority B Refinement Pass

---

## 1. Purpose

This document records the Priority B refinement pass for GyroOS Runtime Continuity.

The refinement is intentionally narrow.

It does not reopen the full Priority B design.

It refines only the following documents:

```text
docs/29_runtime_continuity.md
docs/31_stop_runtime.md
docs/32_jump_runtime.md
docs/33_reslice_runtime.md
```

It also recognizes:

```text
docs/36_adjust_runtime.md
```

as the dedicated definition of Adjust.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Refinement Status

```text
Core consistency: PASS
Runtime Continuity consistency: PASS
Operator Response ownership: PASS
Layer consistency: PASS
Refinement scope: MINOR AND LOCAL
```

No Priority B definition is rejected.

The purpose is to sharpen responsibility boundaries and terminology.

---

## 3. Refinement 1 — Runtime Continuity Source

### Target

```text
docs/29_runtime_continuity.md
```

### Previous Narrow Reading

```text
Runtime Continuity is the runtime condition in which an established Slice result remains connectable...
```

This remains correct for ordinary established continuation.

However, Defer and Void Hold may preserve a relation that has not yet become a fully established Slice result.

### Refined Working Definition

```text
Runtime Continuity is the runtime condition in which an established Slice result
or a retained traceable runtime relation remains connectable to a subsequent
Structure, Slice, Process, or Trajectory relation.
```

Japanese:

```text
Runtime Continuityとは、
成立したSlice結果、または追跡可能な形で保持されたRuntime関係が、
次のStructure・Slice・Process・Trajectory関係へ
接続可能な状態として保持されていることである。
```

### Refined Continuity Source

```text
continuity source
= established runtime result
  or retained traceable runtime relation
```

Possible retained traceable relations include:

```text
deferred relation
Void Hold reference
pending Boundary relation
archived trajectory reference
stopped but reconstructable runtime evidence
```

### Constraint

This refinement does not mean that unreadable material is Stability.

```text
retained traceability ≠ established Stability
```

It means only that Runtime Continuity may preserve future connectability beyond active established execution.

---

## 4. Refinement 2 — Stop and Defer Boundary

### Target

```text
docs/31_stop_runtime.md
```

### Problem

Expressions such as:

```text
Stop ends or suspends the current runtime continuation.
```

may blur the distinction between Stop and Defer.

### Refined Stop Definition

```text
Stop is an Operator Response that ends the current execution connection
within the current control scope, while preserving required runtime evidence.
```

Japanese:

```text
Stopとは、必要なRuntime evidenceを保持しながら、
現在のcontrol scopeにおけるexecution connectionを終了するOperator Responseである。
```

### Refined Defer Boundary

```text
Stop
= end the current execution connection within the current control scope

Defer
= retain the current relation as pending without immediate connection
```

### Important Distinction

A stopped runtime may still be:

```text
restartable
reconstructable
referenced later
used as a future Slice source
```

But Stop itself does not mean:

```text
pending resolution
waiting for additional Context
scheduled automatic resume
```

Those relations belong to Defer or an external lifecycle mechanism.

### Preferred Wording

Use:

```text
Stop ends the current execution connection.
```

Avoid using `suspend` as the primary definition of Stop.

If a runtime platform has a technical pause state, it must be classified separately from GyroOS Operator Response semantics.

---

## 5. Refinement 3 — Jump Decision and Jump Connection

### Target

```text
docs/32_jump_runtime.md
```

### Problem

The term `Jump` may refer both to the Operator Response decision and to the later runtime reconstruction result.

These must remain distinguishable.

### Refined Separation

```text
JUMP
= Operator Response selecting non-continuous reconstruction

Jump Preparation
= creation of target Structure / Orientation / Slice / Trajectory references

Jump Connection
= successful establishment of the new runtime connection
```

### Runtime Flow

```text
Loop Controller / Operator Response
↓
JUMP
↓
JumpDecision
↓
Jump Preparation
↓
JUMP_CONNECTED | JUMP_DEFERRED | JUMP_REJECTED | JUMP_FAILED
```

### Important Distinction

```text
JUMP selected
≠ new connection already established
```

A failed or deferred Jump must return to Operator Response selection explicitly.

It must not silently become Continue.

### Terminology Rule

Use:

```text
JUMP
```

for the response type.

Use:

```text
Jump operation
Jump preparation
Jump connection
```

for implementation stages after the response decision.

---

## 6. Refinement 4 — RESLICE and Re-Slice Operation

### Target

```text
docs/33_reslice_runtime.md
```

### Problem

The sentence:

```text
Re-Slice is an Operator Response...
```

mixes the response decision with the Slice execution that follows.

### Refined Separation

```text
RESLICE
= Operator Response selecting a retained runtime source as the basis for a new Slice

Re-Slice
= runtime operation that opens and executes the new Slice over that retained source
```

### Refined Flow

```text
Loop Controller / Operator Response
↓
RESLICE
↓
ReSliceRequest
↓
Re-Slice Engine
↓
new Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
↓
new Stability
```

### Refined Definition of RESLICE

```text
RESLICE is an Operator Response that selects a retained runtime source
and requests a new Slice path when the current Slice result should not be used
as the only readable path.
```

### Refined Definition of Re-Slice

```text
Re-Slice is the runtime operation that opens and executes the requested new Slice
from the selected retained source.
```

### Important Distinction

```text
RESLICE selected
≠ Re-Slice already executed
```

The Re-Slice operation may be:

```text
prepared
executed
bounded
rejected
deferred
failed
```

The Re-Slice Engine does not own the Operator Response decision.

---

## 7. Adjust Integration

`docs/36_adjust_runtime.md` completes the Priority B response set.

The refined response map is:

```text
CONTINUE
= preserve direct connectability without significant modification

ADJUST
= preserve direct connectability through bounded continuous modification

STOP
= end the current execution connection within the current control scope

JUMP
= select non-continuous reconstruction

RESLICE
= select a retained source for a new Slice operation

DEFER
= retain a pending relation for possible future reconnection

DEFER_VOID / VOID_HOLD
= Defer-related handling of unreadable retained material
```

---

## 8. Cross-Response Matrix

| Response | Immediate Connection | Direct Path Preserved | New Slice Opened | Non-continuous Reconstruction | Pending Relation Preserved | Current Execution Ended |
|---|---:|---:|---:|---:|---:|---:|
| CONTINUE | Yes | Yes | No | No | No | No |
| ADJUST | Yes | Yes | No | No | No | No |
| RESLICE | Requested | Source-relative | Yes | No | No | No |
| JUMP | Requested | No | Possible later | Yes | No | Local path ends |
| DEFER | No | Retained, not advanced | No | No | Yes | Active advancement pauses |
| STOP | No | No immediate continuation | No | No | Not by definition | Yes |

This table is implementation-oriented.

It does not redefine Gyro Logic.

---

## 9. Operator Response Ownership

The following responsibility boundary is fixed:

```text
Stability / Δ / Boundary State / Context / Void / Trajectory evidence / Runtime limits
↓
Loop Controller
↓
Operator Response
```

Then:

```text
CONTINUE
→ prepare next direct relation

ADJUST
→ Update Engine

RESLICE
→ ReSliceRequest → Re-Slice Engine

JUMP
→ JumpDecision → Jump operation

DEFER
→ DeferredRuntimeRecord

STOP
→ StopRecord / execution closure
```

No engine may promote its own condition into an Operator Response without Loop Controller selection.

---

## 10. Runtime Continuity After Refinement

Runtime Continuity now includes two source classes:

```text
1. established runtime source
2. retained traceable runtime source
```

Possible relation outcomes:

```text
direct continuation
bounded adjustment
source-relative new Slice
non-continuous reconstruction
pending retention
execution closure with evidence preservation
```

This provides a unified interpretation without reducing all responses to `continue` or `stop`.

---

## 11. Documentation Application Rule

For Priority B and later documents, use the following terminology consistently:

```text
CONTINUE / ADJUST / STOP / JUMP / RESLICE / DEFER
= Operator Response types
```

```text
Update
Jump operation
Re-Slice operation
Defer record creation
Stop finalization
= runtime operations or effects following the selected response
```

Do not use an operation name as if it owns the response decision.

---

## 12. Priority B Closure Status

After this refinement pass:

```text
Runtime Continuity: refined
Continue: accepted
Adjust: added
Stop: refined
Jump: refined
Re-Slice: refined
Defer: accepted
```

Overall:

```text
Priority B conceptual review: PASS
Priority B refinement: PASS
Priority B ready for Priority C review: YES
```

This does not mean all earlier runtime implementation documents are already updated.

It means the Priority B reference model is sufficiently stable to guide later document revisions.

---

## 13. Next

```text
Priority C: Boundary-aware Runtime
```
