# 33. Re-Slice Runtime

---

## 1. Overview

This document defines **Re-Slice** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

GyroOS does not redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Re-Slice is not a new Core element.

Re-Slice is a runtime relation in which Operator Response selects a new Slice over an already established or retained runtime source.

---

## 2. Core Definition

```text
Re-Slice is an Operator Response that opens a new Slice path
from an established or retained runtime source
when the current Slice result should not be used as the only readable path.
```

Japanese:

```text
Re-Sliceとは、現在のSlice結果だけを唯一の読めるPathとして扱わず、
成立済みまたは保持されているRuntime sourceから
新しいSlice Pathを開くOperator Responseである。
```

Possible Re-Slice sources include:

```text
Context
prior SliceDone
Boundary
Boundary State
Unknown relation
Void reference
Trajectory section
retained Structure condition
```

---

## 3. Re-Slice and the Core

Re-Slice does not modify:

```text
Structure → Slice → Stability
```

Each Re-Slice still follows the Core.

```text
Retained Runtime Source
↓
new Structure condition
↓
new Slice
↓
new Stability
```

A Re-Slice may begin from information produced or retained by a previous Core establishment, but the new Slice remains a Slice.

Therefore:

```text
Re-Slice ≠ fourth Core stage
Re-Slice ≠ extension after Stability inside the Core
```

---

## 4. Re-Slice and Runtime Continuity

Re-Slice is one way of preserving Runtime Continuity.

```text
Current established Slice result
↓
Operator Response selects Re-Slice
↓
new Slice source / condition
↓
new path opening
↓
next established result
```

The original path is not necessarily invalidated.

Instead, GyroOS may preserve:

```text
prior SliceDone
prior StabilityResult
prior Δ
prior Boundary / Boundary State
prior Context
prior Void reference
Trajectory relation
```

Re-Slice therefore preserves continuity by opening another readable path without silently erasing the previous one.

---

## 5. Re-Slice Is Not Retry

```text
Re-Slice ≠ simple retry
```

A retry usually repeats the same operation under substantially the same conditions.

Re-Slice may change:

```text
Operator Orientation
Slice Policy
source Structure
Context target
resolution
granularity
target dimensions
Boundary condition
Trajectory section
```

A retry may be implemented as a special case, but it is not the definition of Re-Slice.

---

## 6. Re-Slice Is Not Continue

Continue preserves connectability through the current established Slice result.

Re-Slice opens another Slice path from a retained source.

```text
Continue:
current established path remains the selected connection

Re-Slice:
a new Slice path is selected from retained runtime evidence
```

Re-Slice is not the opposite of Continue.

Both may preserve Runtime Continuity in different ways.

---

## 7. Re-Slice Is Not Jump

Re-Slice and Jump must remain distinct.

```text
Re-Slice
= opens a new Slice while retaining a readable relation to the current or prior source

Jump
= discontinues the current local path and establishes a non-continuous connection
```

A safe distinction is:

```text
Re-Slice preserves source-relative path continuity.
Jump may break local path continuity while preserving trajectory-level traceability.
```

Re-Slice should be preferred when the retained source can still support another readable Slice.

Jump may be selected when source-relative continuation is insufficient or inappropriate.

---

## 8. Re-Slice and Operator Response

Re-Slice is selected by Operator Response.

```text
SliceDone
↓
Stability
↓
Loop Controller / Operator Response
↓
RESLICE
```

The following do not automatically trigger Re-Slice:

```text
Context existence alone
Boundary existence alone
Boundary State alone
Unknown alone
Void alone
large Δ alone
low Stability alone
```

These may orient the response space, but they do not determine the response.

The Loop Controller may consider:

```text
Stability
Δ
Boundary State
Context inferability
Void readability
Trajectory history
recoverability
criticality
cost and depth limits
Operator Orientation
```

---

## 9. Re-Slice Sources

### 9.1 Context Re-Slice

```text
Context_n
↓
RESLICE_CONTEXT
↓
Slice_{n+1}
```

Context becomes a target only when Operator Response selects it.

Context existence does not automatically create a Context Loop.

---

### 9.2 Prior SliceDone Re-Slice

A prior Slice result may be re-read under a different Orientation, resolution, or target relation.

```text
SliceDone_n
↓
new Orientation / Policy
↓
Re-Slice
```

This does not rewrite the prior SliceDone record.

---

### 9.3 Boundary-aware Re-Slice

Boundary or Boundary State may indicate that the current distinction is insufficient, ambiguous, or too coarse.

Possible cases:

```text
Unknown → higher-resolution Re-Slice
Blank → Context completion Re-Slice
Un → convergence-oriented Re-Slice
Non → alternate Boundary Re-Slice
Void → Re-Slice only if a new readable condition can be formed
```

Boundary State does not itself execute Re-Slice.

---

### 9.4 Trajectory Re-Slice

A prior Trajectory section may become a new Slice source.

```text
Trajectory section
↓
new Orientation
↓
Re-Slice
```

This is useful when a later state makes an earlier relation newly readable.

---

## 10. Re-Slice Depth and Bounded Execution

Re-Slice must not recurse without limit.

GyroOS should enforce:

```text
max_reslice_depth
max_context_chain_length
max_branch_count
cycle detection
time budget
cost budget
memory pressure limit
```

When a limit is reached, the Loop Controller may select:

```text
DEFER
VOID_HOLD
JUMP
STOP
CONTINUE with retained unresolved state
```

The Re-Slice Engine does not select these responses by itself.

---

## 11. Runtime Objects

### ReSliceRequest

```python
class ReSliceRequest:
    request_id: str
    process_index: int

    source_type: str
    source_ref: str

    orientation: OperatorOrientation
    slice_policy: SlicePolicy

    parent_process_id: str
    parent_slice_id: str
    parent_trajectory_id: str | None

    reslice_depth: int
    reason: str
    metadata: dict
```

Possible `source_type` values:

```text
context
slice_done
boundary
boundary_state
void_reference
trajectory_section
structure_reference
```

---

### ReSliceResult

```python
class ReSliceResult:
    request_id: str
    process_index: int

    slice_done: SliceDone
    stability: StabilityResult

    parent_source_ref: str
    trajectory_relation: str
    metadata: dict
```

---

## 12. Runtime Flow

```text
Current Structure
↓
Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
↓
Stability
↓
Loop Controller / Operator Response
↓
RESLICE
↓
ReSliceRequest {
  source_ref,
  new orientation,
  new policy,
  depth,
  reason
}
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

---

## 13. API Implications

The main runtime API remains:

```text
POST /loop/step
```

A Re-Slice may be represented as an Operator Response result:

```json
{
  "operator_response": {
    "type": "RESLICE_CONTEXT",
    "reason": "context may resolve unknown boundary relation",
    "next_request": {
      "mode": "reslice",
      "source_type": "context",
      "source_ref": "context-123",
      "reslice_depth": 1
    }
  }
}
```

Possible support endpoint:

```text
POST /reslice/execute
```

This support endpoint must not redefine `/loop/step` as the canonical runtime relation.

---

## 14. Memory Runtime and Trajectory Cache

Re-Slice must preserve parent-child traceability.

Memory Runtime should retain:

```text
parent_process_id
parent_slice_id
source_ref
orientation change
policy change
reslice_depth
reason
resulting SliceDone
resulting StabilityResult
```

Trajectory Cache should represent:

```text
Trajectory_n
├─ SliceDone_n
└─ ReSliceBranch
   └─ SliceDone_n+1
```

A Re-Slice branch is not silent replacement.

The prior path remains traceable.

---

## 15. Relation to Dynamic Equivalence

Re-Slice may produce additional evidence for Dynamic Equivalence.

```text
previously undecidable
↓
Re-Slice under new Context / Orientation
↓
additional Trajectory evidence
↓
equivalent | not_equivalent | still undecidable
```

Re-Slice does not guarantee equivalence.

Dynamic Equivalence Runtime remains responsible only for evaluating trajectory-based equivalence.

---

## 16. Relation to Gyro-OOM Damper

Repeated Re-Slice may create runtime pressure.

Possible pressure signals:

```text
reslice_depth_exceeded
context_chain_growth
branch_explosion
cycle_detected
memory_pressure
cost_budget_exceeded
```

Gyro-OOM Damper may report or apply selected damping actions, but it does not independently decide Re-Slice, Jump, or Stop.

---

## 17. Design Constraints

Re-Slice MUST NOT:

```text
be added to the Core
be treated as automatic retry
be triggered automatically by Context or Void existence
replace prior SliceDone silently
erase Δ, Boundary, Context, or Void
be treated as Jump
recurse without limits
make GyroAuth decisions
```

Re-Slice MUST:

```text
be selected through Operator Response
open a new Slice path
retain parent-source traceability
preserve prior runtime evidence
support bounded execution
produce a new SliceDone and StabilityResult
remain compatible with Runtime Continuity
```

---

## 18. Key Insight

Re-Slice does not repeat the same answer-seeking operation.

It opens another path through retained runtime evidence.

```text
Re-Slice does not erase the prior path.
Re-Slice makes another path readable.
```

---

## 19. Summary

Re-Slice is an Operator Response that opens a new Slice from an established or retained runtime source.

It preserves Runtime Continuity by retaining prior evidence while allowing another path to become readable.

It remains subordinate to:

```text
Structure → Slice → Stability
```

and is selected only through Operator Response.

---

## Next

```text
Priority B-6: Defer
```
