# 18. Void / Defer / Jump — Priority D-1 Alignment

---

## 1. Purpose

This document defines how GyroOS represents and handles **Void-related runtime evidence**, **DEFER**, and **JUMP** after the Gyro Logic v3.1 refinement and the Priority A, B, and C runtime reviews.

The purpose is not to redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Void is not a new Core element.

Void is not a Runtime Stage.

Void is not an actor.

DEFER and JUMP are Operator Responses. They are not Boundary States and are not actions performed by Void itself.

---

## 2. Canonical Responsibility Separation

GyroOS must keep the following distinct:

```text
Boundary
= a Slice-relative distinction that became readable through Slice

Boundary State
= a provisional relation-to-Boundary classification

Void as Boundary State
= the relevant Boundary is identifiable,
  but the target relation cannot currently be read or connected sufficiently

VoidEvidence
= runtime evidence of unreadability or unconnectability

Void reference
= retained reference to Void-related evidence or relation

DEFER
= Operator Response that preserves future connectability as pending

JUMP
= Operator Response requesting non-continuous reconnection

STOP
= Operator Response ending execution connection in the current control scope
```

These concepts are related, but they are not interchangeable.

```text
Void ≠ DEFER
Void ≠ JUMP
Void ≠ STOP
Boundary State ≠ Operator Response
Stability ≠ Operator Response
```

---

## 3. Runtime Position

A safe runtime relation is:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  distinctions and relations become readable or remain unreadable
  slice-done {
    representation
    Difference / Deviation
    Boundary evidence if readable
    Boundary State records if classifiable
    Context references
    Void evidence / references if retained
  }
}
↓
Stability
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
Runtime Continuity relation
```

Void is represented through Slice-derived evidence.

Void does not appear as a mandatory stage between Slice and Stability.

---

## 4. Void Runtime Definition

```text
Void is a provisional Boundary-relative runtime condition in which
an identifiable target relation cannot currently be read or connected sufficiently
under the active Structure, Operator Orientation, Slice conditions,
and available Context.
```

Japanese:

```text
Voidとは、現在のStructure・Operator Orientation・Slice条件・利用可能なContextのもとで、
関連するBoundaryは識別できるが、そのBoundaryに対する対象関係を
十分に読み取り、または接続することができない、暫定的なBoundary-relative Runtime conditionである。
```

Void is relative to the current Slice conditions.

Void is not an absolute assertion that no relation exists.

Void is not identical to Nothing, Absence, Blank, or Unknown.

---

## 5. Boundary Readability and Void

The following distinction is required:

```text
Boundary relation readability
≠ target relation readability
```

Void as Boundary State may be assigned only when:

```text
the relevant Boundary is identifiable
+
the target relation is not sufficiently readable or connectable relative to it
```

If the Boundary distinction itself is not readable enough to support classification, GyroOS should preserve:

```text
unclassified Boundary evidence
or
unreadable distinction evidence
```

It must not automatically assign `VOID`.

Therefore:

```text
no readable Boundary
≠ automatic Void as Boundary State
```

---

## 6. Void and Other Boundary States

Void must remain distinct from related Boundary States.

```text
Unknown
= the classification target is readable,
  but evidence is insufficient to classify it

Void
= the relevant Boundary is identifiable,
  but the target relation or connection is not sufficiently readable

Absence
= an expected or referenceable relation is readable as not present

Blank
= a readable place or relation exists, but expected content is unfilled

Non
= a readable outside or exclusion relation

Un
= a readable not-yet-established or incompletely formed relation
```

Collapsing these into `null`, `error`, `invalid`, or one generic negative state destroys runtime information.

---

## 7. VoidEvidence Model

Void-related evidence should be represented independently from Operator Response state.

A provisional model is:

```python
class VoidEvidence:
    void_evidence_id: str

    source_slice_ref: str
    source_process_ref: str
    boundary_ref: str | None
    boundary_state_ref: str | None
    relation_ref: str | None

    unreadability_type: str
    reason: str

    relation_readability: float | None
    connectability: float | None
    inferability: float | None
    severity: float | None

    evidence_refs: list[str]
    context_refs: list[str]
    orientation_ref: str | None
    slice_policy_ref: str | None
    trajectory_ref: str | None

    provisional: bool
    resolved_by_ref: str | None
    metadata: dict
```

Recommended `unreadability_type` candidates may include:

```text
relation_unreadable
connection_unavailable
context_insufficient
conflicting_evidence
resolution_insufficient
non_inferable
trajectory_discontinuity
```

The model is provisional.

The following fields must not be embedded as properties of VoidEvidence:

```text
deferred: bool
jumped: bool
stopped: bool
```

Those are consequences of independently recorded Operator Responses, not intrinsic Void properties.

---

## 8. Void References and Retained Relations

A runtime may preserve a Void-related relation for later processing.

```text
VoidEvidence
↓ retained as
Void reference / retained pending relation
```

A retained relation should preserve at least:

```text
source Slice
source Process
relevant Boundary if identifiable
reason for unreadability or unconnectability
available evidence
Context references
Trajectory relation
later Re-Slice or response lineage
```

Retention does not itself mean DEFER was selected.

```text
retained Void reference
≠ DEFER response
```

Evidence may be retained after CONTINUE, ADJUST, RESLICE, JUMP, DEFER, or STOP when traceability requires it.

---

## 9. DEFER

### 9.1 Meaning

```text
DEFER is an Operator Response that keeps a runtime relation pending
while preserving its future connectability.
```

DEFER is not failure.

DEFER does not resolve the relation.

DEFER does not declare the relation impossible.

DEFER preserves a traceable source for possible future reconnection.

### 9.2 Selection Inputs

DEFER may be considered when:

```text
current direct connection is not appropriate
future Context may improve readability
Re-Slice is not currently useful or permitted
non-continuous reconstruction is premature
retention remains possible
Runtime limits permit pending preservation
```

Void evidence may be one input, but:

```text
Void existence
≠ automatic DEFER
```

### 9.3 Runtime Effect

A DEFER response may produce a pending relation record:

```python
class DeferredRelationRecord:
    deferred_relation_id: str
    source_relation_ref: str
    source_slice_ref: str
    source_process_ref: str

    evidence_refs: list[str]
    boundary_refs: list[str]
    boundary_state_refs: list[str]
    void_refs: list[str]

    deferred_at_process_index: int
    revisit_conditions: dict | None
    expiry_conditions: dict | None
    trajectory_ref: str | None

    metadata: dict
```

The deferred record is owned by Runtime continuity and memory handling.

It is not a mutation that turns Void into an acting object.

### 9.4 `DEFER_VOID`

`DEFER_VOID` may remain as an implementation-specific response label when the deferred relation is primarily Void-related.

However, its semantic owner is still DEFER.

```text
DEFER_VOID
= specialized DEFER response label
≠ action performed by Void
```

Canonical response vocabulary should prefer:

```text
DEFER
```

with Void evidence references explaining the reason.

---

## 10. JUMP

### 10.1 Meaning

```text
JUMP is an Operator Response requesting non-continuous reconnection
when direct continuation, bounded adjustment, or source-relative Re-Slice
is not the selected continuity relation.
```

Jump is not ordinary adjustment.

Jump is not another name for Re-Slice.

Jump does not erase the previous runtime path.

### 10.2 Jump Response and Jump Operation

GyroOS must distinguish:

```text
JUMP
= Operator Response request

Jump operation
= preparation and execution of non-continuous reconnection
```

The Loop Controller selects `JUMP`.

An Update Engine, Jump executor, or related runtime component may implement the selected response, but it does not independently decide to Jump.

### 10.3 Selection Inputs

JUMP may be considered when:

```text
direct path connection is no longer selected
bounded ADJUST is insufficient
source-relative RESLICE is insufficient or inappropriate
reconstruction from a different source or orientation is required
trajectory evidence supports branch reconnection
Runtime policy permits non-continuous reconnection
```

Void evidence may contribute, but:

```text
Void existence
≠ automatic JUMP
```

### 10.4 Runtime Effect

A Jump operation may prepare:

```text
new Operator Orientation
new Slice Policy
new source reference
new process branch
new reconstruction relation
Context-chain reset or replacement
```

It must preserve:

```text
prior SliceDone records
prior Boundary and Boundary State evidence
prior Void evidence
Difference / Deviation history
selected-response reason
source and destination lineage
```

---

## 11. STOP

```text
STOP is an Operator Response that ends execution connection
in the current control scope while preserving runtime evidence.
```

STOP is not pending retention.

STOP is not DEFER.

STOP does not mean the timeless Gyro Core has ended.

STOP does not mean Stability was absent.

STOP may be considered when:

```text
explicit Stop is requested
current control-scope execution must end
cost or depth limit is reached
policy prohibits further execution connection
no permitted reconnection is selected
```

Void evidence may contribute to the decision, but:

```text
Void
≠ automatic STOP
```

The word `suspend` should not be used as a synonym for STOP. Pending preservation belongs to DEFER.

---

## 12. ADJUST and RESLICE

The older label `CHANGE_ORIENTATION` is aligned to Priority B as:

```text
ADJUST
= preserve Runtime Continuity through bounded continuous modification
```

Orientation modification may be one implementation effect of ADJUST.

```text
CHANGE_ORIENTATION
= possible implementation action under ADJUST
≠ independent canonical Operator Response
```

RESLICE remains distinct:

```text
RESLICE
= Operator Response requesting another Slice from a retained source

Re-Slice
= runtime operation that performs the requested new Slice
```

Void evidence may orient ADJUST or RESLICE consideration, but does not select either automatically.

---

## 13. Relation to Stability

Stability reads whether the opened path has become readable as an establishment that can continue.

It does not select the next response.

```text
Stability does not choose DEFER.
Stability does not choose JUMP.
Stability does not choose STOP.
Stability does not choose RESLICE.
```

The Loop Controller may consider:

```text
SliceDone readability
StabilityResult
Difference / Deviation
Boundary evidence
Boundary State records
Void evidence
Context
Trajectory history
recoverability
retainability
Runtime limits
policy
```

and then select an Operator Response.

Also:

```text
continuability
≠ CONTINUE response
```

A path may be readable as an establishment that can continue while the Operator Response still selects ADJUST, RESLICE, JUMP, DEFER, or STOP.

---

## 14. Relation to Context Loop

A Context Loop may encounter or retain Void-related evidence.

Safe relation:

```text
Context-aware Slice
↓
SliceDone with Context and possible Void evidence
↓
StabilityResult
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
```

Context existence does not automatically require Re-Slice.

Void existence does not automatically require another Context Loop.

Runtime limits must prevent unbounded recursion, repeated Re-Slice, or indefinite Context-chain expansion.

---

## 15. Memory and Trajectory Preservation

Void-related evidence must remain traceable across later runtime relations.

A later Slice may reclassify a prior relation:

```text
BoundaryState_A: VOID
↓ reclassified_by Slice_B
BoundaryState_B: UNKNOWN
↓ reclassified_by Slice_C
BoundaryState_C: NORMAL
```

The later record must not silently overwrite the earlier one.

Recommended lineage relations include:

```text
reclassified_from
refined_from
resolved_by
reopened_from
unreadable_under
supersedes_for_current_scope
```

Memory Runtime stores evidence and lineage.

Trajectory Cache preserves how readability, classification, Stability, and Operator Response changed across Processes.

Neither Memory Runtime nor Trajectory Cache independently decides the next response.

---

## 16. Boundary-aware API Implications

`POST /loop/step` may return Void-related evidence and a separately selected Operator Response.

Example:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 12,
  "slice_done": {
    "representation": {},
    "deviation": {},
    "boundary_evidence": [
      {
        "boundary_id": "boundary_012",
        "boundary_readability": 0.81
      }
    ],
    "boundary_state_records": [
      {
        "boundary_state_id": "boundary_state_012",
        "boundary_ref": "boundary_012",
        "state_type": "VOID",
        "boundary_state_confidence": 0.76
      }
    ],
    "void_evidence": [
      {
        "void_evidence_id": "void_evidence_012",
        "boundary_ref": "boundary_012",
        "reason": "relation_unreadable",
        "relation_readability": 0.18,
        "connectability": 0.22
      }
    ]
  },
  "stability": {
    "value": null,
    "status": "not_evaluable"
  },
  "operator_response": {
    "response_type": "DEFER",
    "reason": "future context may improve relation readability",
    "considered_void_refs": ["void_evidence_012"],
    "decisive_evidence_refs": ["void_evidence_012", "boundary_state_012"]
  },
  "continuity": {
    "effect": "pending_future_connectability"
  }
}
```

This remains a successful Runtime API response.

```text
Boundary State = VOID
Operator Response = DEFER
HTTP status = 200
```

Void, DEFER, JUMP, or STOP must not be treated as HTTP errors by definition.

---

## 17. Decision Constraints

Void-related runtime handling MUST NOT:

```text
redefine Structure → Slice → Stability
insert Void as a new Runtime Stage
treat Void as an actor
treat Void as a generic error
treat no readable Boundary as automatic VOID
automatically map VOID to DEFER
automatically map VOID to JUMP
automatically map VOID to STOP
automatically map low Stability to STOP
store DEFER state inside VoidEvidence
erase prior Boundary, Void, Stability, or Deviation history
mix GyroAuth authentication verdicts into GyroOS runtime definitions
```

Void-related runtime handling MUST:

```text
preserve Boundary-relative evidence
separate evidence from Operator Response
preserve pending relations when DEFER is selected
preserve source and destination lineage when JUMP is selected
end only the current control-scope connection when STOP is selected
retain historical records across reclassification
keep response ownership in Loop Controller / Operator Response
```

---

## 18. Aligned Runtime Flow

```text
SliceDone_n {
  representation
  Difference / Deviation
  BoundaryEvidence[]
  BoundaryStateRecord[]
  VoidEvidence[]
  Context references
}
↓
StabilityResult_n
↓
Loop Controller / Operator Response
├─ CONTINUE
├─ ADJUST
├─ RESLICE
├─ JUMP
├─ DEFER
└─ STOP
↓
Runtime Continuity result
↓
Memory / Trajectory preservation
```

No direct arrow is permitted from Void to a response.

Incorrect:

```text
Void → DEFER
Void → JUMP
Void → STOP
```

Correct:

```text
Void evidence
+ Boundary evidence
+ Boundary State
+ Stability
+ Difference / Deviation
+ Context
+ Trajectory
+ Runtime limits
↓
Loop Controller / Operator Response
↓
selected response
```

---

## 19. Key Insight

```text
Void describes a provisional Boundary-relative readability or connectability condition.
DEFER preserves future connectability as pending.
JUMP requests non-continuous reconnection.
STOP ends execution connection in the current control scope.
Operator Response selects among them.
Trajectory preserves why and how the selection occurred.
```

In short:

```text
Void does not act.
Evidence is preserved.
Stability reads the Path.
Operator Response selects the connection.
```

---

## 20. Priority D-1 Decision

`docs/18_void_defer_jump.md` is aligned to the Priority A, B, and C runtime model.

The following legacy representations are retired from this document:

```text
Void / Defer / Jump as one class of runtime response patterns
VoidState.deferred as intrinsic Void state
STOP as terminate or suspend
CHANGE_ORIENTATION as a separate canonical response
Void existence as a sufficient response condition
```

The canonical relation is now:

```text
Slice-derived Boundary / Boundary State / Void evidence
↓
Stability reading
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
Runtime Continuity and traceable history
```

The next Priority D item is:

```text
D-2 docs/14_api_design.md Alignment
```
