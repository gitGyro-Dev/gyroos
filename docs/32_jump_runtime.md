# 32. Jump Runtime

---

## 1. Overview

This document defines **Jump** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

Jump is used when the current local path should not remain the direct continuation substrate.

The invariant Core remains:

```text
Structure → Slice → Stability
```

Jump is not a new Core element.

---

## 2. Core Definition

```text
JUMP is an Operator Response that requests a non-continuous reconstruction
of the current runtime connection while preserving traceable relation
to the prior path.
```

```text
Jump operation is the runtime operation that prepares, executes,
and records that non-continuous connection.
```

Japanese:

```text
JUMPとは、過去のPathとの追跡可能な関係を保持しながら、
現在のRuntime connectionを非連続的に再構成することを要求する
Operator Responseである。

Jump operationとは、その要求に基づいて、
新しいStructure・Orientation・Slice条件・Trajectory断面への接続を
準備・実行・記録するRuntime operationである。
```

---

## 3. Decision and Operation Must Be Separated

```text
Loop Controller / Operator Response
→ JUMP decision
→ JumpRequest
→ Jump operation
→ JumpResult
```

The Operator Response owns the decision. A Jump Engine or equivalent runtime component owns execution.

```text
JUMP decision ≠ Jump operation
Jump preparation ≠ Jump connection
Jump failure ≠ automatic fallback
```

This separation is required because a requested Jump may be prepared, connected, deferred, rejected, or failed.

---

## 4. What Jump Is Not

```text
Jump ≠ Stop
Jump ≠ Continue
Jump ≠ Adjust
Jump ≠ Re-Slice
Jump ≠ random reset
Jump ≠ history deletion
Jump ≠ loss of all continuity
Jump ≠ new Core stage
```

Void, low Stability, Boundary State, large Δ, or runtime pressure may orient the response space, but none executes Jump by itself.

---

## 5. Jump and Runtime Continuity

A local path may become unreadable, cyclic, too costly, incompatible, or unrecoverable under the current Orientation.

In that case:

```text
local path continuity may break
while trajectory-level traceability remains
```

The prior path must not be silently merged with the new path.

```text
Trajectory_A
↓
JumpBoundary
↓
Trajectory_B
```

```text
Trajectory_A ≠ Trajectory_B
```

They remain related through an explicit Jump record.

---

## 6. Jump as Operator Response

A safe decision relation is:

```text
Stability or not-evaluable result
+ Δ
+ Boundary State
+ Context
+ Void reference
+ Trajectory history
+ Recoverability
+ Runtime limits
↓
Loop Controller / Operator Response
↓
JUMP
```

No single signal must automatically force Jump.

---

## 7. Relation to Other Responses

```text
CONTINUE
= preserve connection through the current path

ADJUST
= preserve the current path with bounded continuous modification

RESLICE
= request another Slice from a retained direct source

JUMP
= request a non-continuous reconstruction of source or connection

DEFER
= preserve the unresolved relation for later

STOP
= end the current execution connection in the active control scope
```

### Jump and Re-Slice

```text
Re-Slice preserves source-relative path continuity.
Jump may replace direct source continuity with a traceable non-continuous relation.
```

Re-Slice should be preferred when a retained source can still support another readable Slice. Jump may be selected when that source-relative connection is insufficient or inappropriate.

### Jump and Stop

Stop ends the current execution connection without preparing another one. Jump requests another connection.

### Jump and Defer

Jump reconnects elsewhere now. Defer postpones reconnection.

---

## 8. Jump Types

Implementation-level Jump types may include:

```text
Orientation Jump
Slice-Condition Jump
Structure-Mapping Jump
Trajectory Branch Jump
Protective Jump
```

These are runtime classifications, not Gyro Logic concepts.

---

## 9. Jump Preconditions

Candidate evidence may include:

```text
continuous adjustment is insufficient
Re-Slice has no viable direct source
current path is cyclic
current path exceeds runtime limits
Boundary relation is incompatible with intended continuation
current Void cannot be held or deferred safely
protective runtime policy requires reconstruction
explicit Operator policy requests discontinuous change
```

No single item automatically selects JUMP.

---

## 10. Jump Request and Result

```python
class JumpRequest:
    jump_id: str
    process_index: int
    source_process_id: str
    source_slice_id: str | None
    source_trajectory_id: str
    jump_type: str
    reason: str
    evidence_refs: list[str]
    target_structure_ref: str | None
    target_orientation: OperatorOrientation | None
    target_slice_policy: SlicePolicy | None
    metadata: dict
```

```python
class JumpResult:
    jump_id: str
    status: str
    source_trajectory_id: str
    target_trajectory_id: str | None
    traceability_preserved: bool
    next_ready: bool
    failure_reason: str | None
    metadata: dict
```

Recommended status values:

```text
JUMP_PREPARED
JUMP_CONNECTED
JUMP_DEFERRED
JUMP_REJECTED
JUMP_FAILED
```

`JUMP_FAILED` must not silently become Continue. The Loop Controller must select the next response explicitly.

---

## 11. Trajectory Record

A JumpBoundary should preserve:

```text
source_process_id
source_slice_id
source_trajectory_id
target_structure_ref
target_orientation_ref
target_trajectory_id
reason
evidence_refs
boundary_state
void_ref if applicable
operator_response_ref
timestamp
```

Jump creates a trajectory relation, not static equality.

---

## 12. API Implications

A `/loop/step` response may return the JUMP decision and preparation status:

```json
{
  "operator_response": "JUMP",
  "jump": {
    "status": "JUMP_PREPARED",
    "jump_type": "ORIENTATION_JUMP",
    "reason": "continuous adjustment is insufficient",
    "source_trajectory_id": "trajectory-a",
    "target_trajectory_id": null,
    "next_ready": false
  }
}
```

The support operation may later return `JUMP_CONNECTED`, `JUMP_DEFERRED`, `JUMP_REJECTED`, or `JUMP_FAILED`.

```text
JUMP response ≠ HTTP error by definition
Jump operation failure ≠ automatic Stop
```

---

## 13. Design Constraints

JUMP MUST NOT:

```text
be added to the Core
be triggered automatically by a single signal
delete prior trajectory evidence
silently merge discontinuous trajectory sections
be treated as Re-Slice
be treated as Stop
imply successful connection before JumpResult exists
make GyroAuth decisions
```

JUMP MUST:

```text
remain an Operator Response
produce an explicit JumpRequest
preserve source traceability
separate decision, preparation, and connection
record the operation outcome
require a new Operator Response after failure or deferral
```

---

## 14. Key Insight

```text
JUMP selects non-continuous reconstruction.
Jump operation attempts and records that reconstruction.
```

Local path continuity may break while trajectory-level relation remains readable.

---

## 15. Refinement Record

This document incorporates the Priority B refinement pass defined in:

```text
docs/35_priority_b_runtime_continuity_review.md
docs/37_priority_b_refinement_pass.md
```
