# 33. Re-Slice Runtime

---

## 1. Overview

This document defines **Re-Slice** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

GyroOS does not redefine Gyro Logic. The invariant Core remains:

```text
Structure → Slice → Stability
```

Re-Slice is not a fourth Core stage.

---

## 2. Decision and Operation

```text
RESLICE is an Operator Response that requests a new Slice
from an established or retained traceable runtime source.
```

```text
Re-Slice is the runtime operation that opens and executes that new Slice path.
```

Japanese:

```text
RESLICEとは、成立済みまたは追跡可能な形で保持されたRuntime sourceから、
新しいSliceを開始することを要求するOperator Responseである。

Re-Sliceとは、その要求に基づいて新しいSlice Pathを開き、
Structure → Slice → Stability を再び実行するRuntime operationである。
```

The distinction is mandatory:

```text
RESLICE decision ≠ Re-Slice operation
```

---

## 3. Runtime Flow

```text
SliceDone / retained traceable runtime source
↓
Stability or not-evaluable result
↓
Loop Controller / Operator Response
↓
RESLICE
↓
ReSliceRequest
↓
Re-Slice Engine
↓
new Structure condition
↓
new Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
↓
new Stability
↓
ReSliceResult
```

The Loop Controller owns the RESLICE decision. The Re-Slice Engine owns execution.

---

## 4. Re-Slice and the Core

Each Re-Slice follows the same invariant Core:

```text
retained source
→ new Structure condition
→ new Slice
→ new Stability
```

Therefore:

```text
Re-Slice ≠ fourth Core stage
Re-Slice ≠ extension after Stability inside the Core
RESLICE ≠ Slice itself
```

---

## 5. Re-Slice Sources

Possible sources include:

```text
Context
prior SliceDone
Boundary
Boundary State
Unknown relation
Void reference
Trajectory section
retained Structure condition
other retained traceable runtime relation
```

A source does not automatically trigger RESLICE.

```text
Context existence ≠ RESLICE
Boundary State ≠ RESLICE
Void ≠ RESLICE
large Δ ≠ RESLICE
low Stability ≠ RESLICE
```

These may orient the response space, but the Loop Controller owns the decision.

---

## 6. Re-Slice and Runtime Continuity

Re-Slice may preserve Runtime Continuity by opening another readable path from retained evidence.

```text
prior path remains traceable
+
new Slice path is opened
```

Re-Slice must not silently replace:

```text
prior SliceDone
prior StabilityResult
prior Δ
prior Boundary / Boundary State
prior Context
prior Void reference
Trajectory relation
```

```text
Re-Slice does not erase the prior path.
Re-Slice makes another path readable.
```

---

## 7. Re-Slice Is Not Retry

```text
Re-Slice ≠ simple retry
```

A retry usually repeats substantially the same operation under substantially the same conditions.

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

Retry may be implemented as a constrained special case, but it is not the definition.

---

## 8. Relation to Other Responses

```text
CONTINUE
= use the current established path as the direct connection substrate

ADJUST
= preserve the current path with bounded continuous modification

RESLICE
= request a new Slice from a retained direct source

JUMP
= request non-continuous reconstruction of source or connection

DEFER
= retain the relation pending possible later action

STOP
= end the current execution connection in the active control scope
```

### Re-Slice and Continue

Continue uses the current established path directly. Re-Slice opens another Slice path.

### Re-Slice and Adjust

Adjust modifies the existing path continuously. Re-Slice starts a new Slice execution.

### Re-Slice and Jump

```text
Re-Slice preserves source-relative path continuity.
Jump may replace direct source continuity with a traceable non-continuous relation.
```

Re-Slice should be preferred when the retained source can still support another readable Slice.

### Re-Slice and Defer

Defer may preserve a future Re-Slice possibility without executing it now.

---

## 9. Re-Slice Types

### Context Re-Slice

```text
Context_n
→ RESLICE_CONTEXT
→ ReSliceRequest
→ Slice_n+1
```

Context becomes a target only when Operator Response selects it.

### Prior SliceDone Re-Slice

A prior Slice result is read under a different Orientation, resolution, or policy without rewriting the original record.

### Boundary-aware Re-Slice

Boundary-related evidence may orient a different Slice condition.

Examples:

```text
Unknown → higher-resolution Re-Slice
Blank → Context-completion Re-Slice
Un → convergence-oriented Re-Slice
Non → alternate Boundary Re-Slice
Void → Re-Slice only when a new readable condition can be formed
```

### Trajectory Re-Slice

A prior Trajectory section becomes the source of a later Slice when new Context makes it newly readable.

---

## 10. Bounded Execution

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
CONTINUE with retained unresolved evidence
```

The Re-Slice Engine does not select these responses by itself.

---

## 11. Runtime Objects

```python
class ReSliceRequest:
    request_id: str
    process_index: int
    response_ref: str

    source_type: str
    source_ref: str

    orientation: OperatorOrientation
    slice_policy: SlicePolicy

    parent_process_id: str
    parent_slice_id: str | None
    parent_trajectory_id: str | None

    reslice_depth: int
    reason: str
    metadata: dict
```

```python
class ReSliceResult:
    request_id: str
    status: str
    process_index: int
    slice_done: SliceDone | None
    stability: StabilityResult | None
    parent_source_ref: str
    trajectory_relation: str
    failure_reason: str | None
    metadata: dict
```

Recommended statuses:

```text
RESLICE_PREPARED
RESLICE_COMPLETED
RESLICE_DEFERRED
RESLICE_REJECTED
RESLICE_FAILED
```

A failed operation does not silently become Continue or Jump. A new Operator Response is required.

---

## 12. API Implications

The canonical runtime API remains:

```text
POST /loop/step
```

A RESLICE response may return a request:

```json
{
  "operator_response": {
    "type": "RESLICE_CONTEXT",
    "reason": "context may resolve unknown boundary relation",
    "next_request": {
      "request_id": "reslice-001",
      "source_type": "context",
      "source_ref": "context-123",
      "reslice_depth": 1
    }
  }
}
```

A support endpoint may execute the request:

```text
POST /reslice/execute
```

That endpoint performs the Re-Slice operation. It does not own the RESLICE decision and does not replace `/loop/step` as the canonical response-selection boundary.

---

## 13. Memory and Trajectory

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
operation status
```

Trajectory Cache should represent a Re-Slice as an explicit branch or relation:

```text
Trajectory_n
├─ SliceDone_n
└─ ReSliceRelation
   └─ SliceDone_n+1
```

A Re-Slice branch is not silent replacement.

---

## 14. Relation to Other Runtime Components

Dynamic Equivalence Runtime may use Re-Slice results as additional evidence, but Re-Slice does not guarantee equivalence.

Gyro-OOM Damper may report recursion or memory pressure, but it does not independently select RESLICE, JUMP, DEFER, or STOP.

---

## 15. Design Constraints

RESLICE MUST NOT:

```text
be added to the Core
be treated as automatic retry
be triggered automatically by Context, Boundary, Void, Δ, or Stability alone
replace prior SliceDone silently
erase Δ, Boundary, Context, or Void
be treated as JUMP
imply operation completion when only a decision exists
recurse without limits
make GyroAuth decisions
```

RESLICE MUST:

```text
remain an Operator Response
produce an explicit ReSliceRequest
identify a retained traceable source
preserve parent-source traceability
```

Re-Slice operation MUST:

```text
be executed by the Re-Slice Engine or equivalent runtime component
open a new Slice path
produce an explicit operation result
produce a new SliceDone and StabilityResult when completed
preserve prior runtime evidence
remain bounded
```

---

## 16. Key Insight

```text
RESLICE selects another Slice.
Re-Slice performs that Slice.
```

The decision and execution boundaries must remain separate.

---

## 17. Refinement Record

This document incorporates the Priority B refinement pass defined in:

```text
docs/35_priority_b_runtime_continuity_review.md
docs/37_priority_b_refinement_pass.md
```
