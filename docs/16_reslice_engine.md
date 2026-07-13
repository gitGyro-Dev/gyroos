# 16. Re-Slice Engine

---

## 1. Overview

This document defines the GyroOS **Re-Slice Engine** after the Gyro Logic v3.1 Core refinement and the Priority B / Priority C Runtime alignment.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Re-Slice is not a fourth Core element.

Re-Slice is the Runtime operation that performs another Slice over a retained and traceable source after the Loop Controller has selected the `RESLICE` Operator Response.

```text
RESLICE
= Operator Response requesting another Slice

Re-Slice
= Runtime operation executing that requested Slice
```

These must remain distinct.

---

## 2. Canonical Definition

```text
Re-Slice is another bounded Slice performed over a retained Runtime source relation, with explicit lineage to the prior Process and Slice from which that source became available.
```

Japanese:

```text
Re-Sliceとは、保持されたRuntime source relationに対して、
そのsourceが成立した過去のProcessおよびSliceとのlineageを維持しながら、
もう一度実行されるboundedなSliceである。
```

Short reading:

```text
Re-Slice = Slice again over a retained source.
```

Re-Slice does not replace Slice.

It uses the same conceptual relation:

```text
Structure-like source condition
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
↓
Stability
```

The difference is the retained source and lineage, not the Core process.

---

## 3. Runtime Position

Correct responsibility chain:

```text
SliceDone_n
↓
StabilityResult_n
↓
Loop Controller / Operator Response
↓
RESLICE selected
↓
SliceRequest(mode="reslice")
↓
Re-Slice Engine
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
↓
SliceDone_n+1
↓
StabilityResult_n+1
```

Incorrect:

```text
Context exists
→ Re-Slice starts
```

Incorrect:

```text
Void exists
→ Re-Slice starts
```

Incorrect:

```text
low Stability
→ Re-Slice starts
```

Context, Void evidence, Boundary evidence, Difference / Deviation, and Stability may orient the response space.

They do not start Re-Slice by themselves.

---

## 4. Re-Slice Source

A Re-Slice source must be retained and traceable.

Possible source types include:

```text
runtime_structure
slice_done
context_evidence
boundary_evidence
boundary_state_record
void_evidence
trajectory_segment
prior_process_result
retained_relation
```

The source is not required to be a complete prior object.

It may be a selected relation or evidence reference preserved by Memory Runtime or Trajectory Cache.

Important distinctions:

```text
ContextEvidence
≠ automatic Re-Slice target

VoidEvidence
≠ Void acting

BoundaryStateRecord
≠ Re-Slice command
```

The Loop Controller selects `RESLICE` and identifies the retained source to be sliced again.

---

## 5. SliceRequest Model

A provisional request model is:

```python
class SliceRequest:
    request_id: str
    process_index: int

    mode: str  # slice | reslice
    source_type: str
    source_ref: str

    orientation: OperatorOrientation
    slice_policy: dict

    context_refs: list[str]
    boundary_refs: list[str]
    boundary_state_refs: list[str]
    void_refs: list[str]

    parent_process_id: str | None
    parent_slice_id: str | None
    parent_response_id: str | None

    reslice_depth: int
    trajectory_ref: str | None
    metadata: dict
```

`mode="reslice"` is an implementation marker.

It does not define a new theoretical operation.

The request must preserve:

```text
which source is being sliced again
why that source was selected
which Operator Response requested it
which prior Process and Slice supplied it
which Orientation and Slice Policy are active
```

---

## 6. Re-Slice Engine Responsibilities

The Re-Slice Engine performs only the requested operation.

### 6.1 Validate the Request

It verifies that:

```text
response_type = RESLICE
source_ref is retained and resolvable
parent lineage is available
runtime limits permit another Slice
```

It does not reconsider whether `RESLICE` should have been selected.

### 6.2 Resolve the Retained Source

The engine resolves the source reference through Memory Runtime, Trajectory Cache, or current LoopState.

It must not convert missing source data into a new response by itself.

If the source cannot be resolved, the failure becomes Runtime evidence returned to the Loop Controller.

### 6.3 Execute Slice

Re-Slice executes the normal internal Slice distinctions:

```text
Operator Orientation
↓
Slice Policy
↓
slice-ing
↓
slice-done
```

Operator Orientation remains internal to Slice.

### 6.4 Produce a New SliceDone

Re-Slice always produces a new SliceDone identity when execution reaches slice-done.

It must not overwrite the parent SliceDone.

### 6.5 Preserve Lineage

The new result must preserve relations such as:

```text
parent_process_ref
parent_slice_ref
parent_response_ref
source_ref
source_type
resliced_from
trajectory_ref
reslice_depth
```

---

## 7. Boundary-aware SliceDone Output

A candidate result is:

```python
class SliceDone:
    slice_id: str
    process_id: str

    representation: dict
    deviation: dict

    boundary_evidence: list[BoundaryEvidence]
    boundary_state_records: list[BoundaryStateRecord]
    context_evidence: list[ContextEvidence]
    void_evidence: list[VoidEvidence]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str
    slice_policy_ref: str
    parent_slice_ref: str | None
    trajectory_ref: str | None

    readability: dict
    metadata: dict
```

Naming rule:

```text
*_evidence = directly retained evidence objects
*_records = classified records with identity and lineage
*_refs = references to separately retained records
```

Boundary-aware does not mean Boundary-required.

A Re-Slice result may contain no readable Boundary.

---

## 8. Context and Re-Slice

Context may be selected as a Re-Slice source when it remains sufficiently retained and traceable.

Correct:

```text
ContextEvidence retained
+
other Runtime evidence
↓
Loop Controller selects RESLICE
↓
SliceRequest(source_type="context_evidence")
↓
Re-Slice Engine executes
```

Incorrect:

```text
Context exists
→ RESLICE_CONTEXT
```

`RESLICE_CONTEXT` is a legacy compatibility name only.

Canonical representation:

```text
response_type = RESLICE
source_type = context_evidence
```

---

## 9. Boundary and Re-Slice

Boundary-related evidence may orient Re-Slice when:

```text
Boundary is provisional
Boundary evidence conflicts
Boundary State remains Unknown
resolution is insufficient
another retained relation may expose a different distinction
```

However:

```text
Boundary State = UNKNOWN
≠ automatic RESLICE

Boundary State = VOID
≠ automatic RESLICE
```

The Loop Controller must consider multiple inputs before selecting `RESLICE`.

A later Slice may produce:

```text
refined Boundary
new Boundary
conflicting Boundary
no readable Boundary
reclassified Boundary State
```

The earlier records remain preserved.

---

## 10. Void and Re-Slice

The engine must distinguish:

```text
Void as Boundary State
VoidEvidence
Void reference
RESLICE response
Re-Slice operation
```

A retained `VoidEvidence` object may be selected as source material.

This does not mean that Void performs Re-Slice.

Correct:

```text
VoidEvidence retained
+
Re-Slice viability
+
Context availability
+
Stability
+
Runtime limits
↓
Loop Controller selects RESLICE
↓
Re-Slice Engine executes
```

If the Boundary distinction itself was unreadable, the source should remain unclassified Boundary or unreadable-distinction evidence rather than being forced into `VOID`.

---

## 11. Stability Relation

Re-Slice does not produce Stability directly.

```text
Re-Slice Engine
↓
new SliceDone
↓
Stability Engine
↓
new StabilityResult
```

Stability does not initiate Re-Slice.

Important:

```text
not_evaluable Stability
≠ automatic RESLICE

low Stability
≠ automatic RESLICE
```

Stability is one input to Loop Controller response selection.

---

## 12. Operator Response Relation

The canonical response vocabulary is:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Re-Slice Engine runs only for:

```text
response_type = RESLICE
```

Legacy names map as follows:

```text
RESLICE_CONTEXT → RESLICE with Context source refs
CHANGE_ORIENTATION → ADJUST
DEFER_VOID → DEFER with Void-related evidence
```

`ADJUST` may alter Orientation continuously.

A later `RESLICE` may then use the adjusted Orientation, but `orientation_reslice` is not a separate canonical response type.

---

## 13. Re-Slice Depth and Bounded Execution

Re-Slice must remain bounded.

Candidate state:

```python
class ReSliceState:
    reslice_depth: int
    max_reslice_depth: int
    source_chain: list[str]
    visited_slice_refs: list[str]
    cycle_detected: bool
    metadata: dict
```

Required controls:

```text
bounded reslice_depth
bounded source_chain length
cycle detection
source resolution limits
memory pressure checks
trajectory branch limits
```

When a limit is reached, the Re-Slice Engine does not select `DEFER`, `JUMP`, or `STOP` itself.

It returns limit evidence to the Loop Controller.

The Loop Controller then selects the next Operator Response.

---

## 14. API Mapping

The main endpoint remains:

```text
POST /loop/step
```

Example response selecting another Slice:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 8,
  "operator_response": {
    "response_type": "RESLICE",
    "reason": "retained context may expose a more readable path",
    "decisive_evidence_refs": ["ctx_007", "stability_008"]
  },
  "next_request": {
    "mode": "reslice",
    "source_type": "context_evidence",
    "source_ref": "ctx_007",
    "parent_process_id": "process_008",
    "parent_slice_id": "slice_008",
    "reslice_depth": 1
  }
}
```

An optional lower-level endpoint may exist:

```text
POST /reslice/execute
```

But it only executes an already selected request.

```text
POST /reslice/execute
≠ Operator Response owner
```

---

## 15. Memory and Trajectory Preservation

Re-Slice must preserve:

```text
prior SliceDone
prior Boundary evidence
prior Boundary State records
prior Context evidence
prior Void evidence
prior StabilityResult
Operator Response that selected RESLICE
new SliceRequest
new SliceDone
```

The relation may be expressed as:

```text
SliceDone_B.resliced_from = SliceDone_A
```

or with more specific lineage:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
reopened_from
```

Later results must not silently overwrite earlier records.

---

## 16. Design Constraints

The Re-Slice Engine MUST NOT:

```text
redefine Structure → Slice → Stability
act as Loop Controller
self-trigger from Context
self-trigger from Boundary State
self-trigger from Void
self-trigger from Stability
convert missing source into an Operator Response
silently overwrite prior SliceDone or evidence
create GyroAuth application decisions
run without bounded limits
```

The Re-Slice Engine MUST:

```text
run only after RESLICE is selected
execute another bounded Slice
resolve a retained and traceable source
preserve parent and response lineage
produce a new SliceDone
pass the new result to Stability Engine
return limit or resolution problems as evidence
preserve Memory and Trajectory history
```

---

## 17. Key Insight

```text
RESLICE requests another Slice.
Re-Slice executes that request.
The source changes; the Core does not.
```

Re-Slice is therefore not a special escape from Gyro Logic.

It is the Runtime repetition of Slice over a retained relation.

---

## 18. Summary

Correct flow:

```text
SliceDone_n
↓
StabilityResult_n
↓
Loop Controller selects RESLICE
↓
Re-Slice Engine executes Slice over retained source
↓
SliceDone_n+1
↓
StabilityResult_n+1
```

Incorrect flow:

```text
Context / Void / Boundary State / Stability
→ Re-Slice automatically
```

Next alignment target:

```text
docs/17_context_loop_controller.md
```