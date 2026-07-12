# 45. Boundary Memory and Trajectory Preservation

---

## 1. Overview

This document defines **Boundary Memory and Trajectory Preservation** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

The invariant Core remains:

```text
Structure → Slice → Stability
```

Boundary and Boundary State are not new Core elements.

They are Slice-relative runtime-readable relations that may change, be refined, conflict, coexist, or become unreadable across later Slices.

Therefore, GyroOS must preserve enough evidence to reconstruct:

```text
what Boundary became readable
under which Slice conditions
how it was provisionally classified
how later Slices changed that reading
which Operator Response followed
```

This document addresses **Priority C-7: Boundary Memory and Trajectory Preservation**.

---

## 2. Core Preservation Principle

```text
Boundary-related runtime evidence must remain traceable across later Slice, Stability, and Operator Response relations without being treated as a permanent object property.
```

Japanese:

```text
Boundary関連のRuntime evidenceは、
対象の恒久的属性として固定されることなく、
後続のSlice・Stability・Operator Responseとの関係を
再構成できる形で追跡可能に保持されなければならない。
```

The goal is not to preserve every byte forever.

The goal is to preserve sufficient lineage and relation.

---

## 3. What Must Be Preserved

A Boundary-related record may need to preserve:

```text
boundary_id
boundary_state_id
source_structure_ref
source_slice_id
source_slice_done_ref
operator_orientation_ref
slice_policy_ref
context_refs
resolution / granularity
boundary evidence
boundary readability
boundary confidence if implemented
Difference / Deviation refs
Void refs if applicable
StabilityResult ref
Operator Response ref
Trajectory position
lineage relations
created_at / observed_at
metadata
```

Not every implementation must expose every field publicly.

However, the internal record must preserve enough information to explain why the Boundary was readable in that runtime scope.

---

## 4. Boundary Is Not a Permanent Object Property

Incorrect model:

```text
object.boundary_state = "Unknown"
```

when the value is treated as timeless and globally true.

Safer model:

```text
BoundaryStateRecord {
  object_ref,
  boundary_ref,
  slice_ref,
  trajectory_ref,
  state,
  evidence_refs,
  scope,
  timestamp
}
```

The same object or relation may be classified differently under another Slice.

```text
Slice_A → BoundaryState = Unknown
Slice_B → BoundaryState = Normal
Slice_C → BoundaryState = Non
```

These are not necessarily contradictions.

They may represent different:

```text
Orientations
Contexts
resolutions
Boundary definitions
Trajectory sections
runtime scopes
```

---

## 5. Preserve, Do Not Silently Overwrite

A later Boundary reading must not silently replace an earlier one.

Incorrect:

```text
BoundaryState.Unknown
↓ overwrite
BoundaryState.Normal
```

Correct:

```text
BoundaryState_A: Unknown
↓ reclassified_by Slice_B
BoundaryState_B: Normal
```

Recommended lineage relations include:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
supersedes_for_current_scope
reopened_from
invalidated_by_evidence
unreadable_under
```

`supersedes_for_current_scope` does not mean deletion of the prior record.

---

## 6. Memory Runtime Responsibility

Memory Runtime is the preservation substrate.

It must not:

```text
create Boundary
classify Boundary State independently
create Stability
decide Operator Response
```

It should:

```text
retain Boundary evidence
retain Boundary State records
retain Slice-relative scope
retain references to Stability and Operator Response
retain lineage among later classifications
support bounded resolution decay
support retrieval for Re-Slice, Jump, Defer, and review
```

Safe responsibility chain:

```text
Slice
→ Boundary becomes readable
→ SliceDone preserves Boundary evidence
→ Stability reads the Path establishment
→ Operator Response selects next relation
→ Memory Runtime preserves the resulting evidence graph
```

---

## 7. Trajectory Cache Responsibility

Trajectory Cache represents how Boundary readings change across runtime relations.

Example:

```text
Trajectory_T1
├─ Process_1
│  ├─ SliceDone_1
│  ├─ Boundary_B1
│  └─ BoundaryState_1 = Unknown
├─ OperatorResponse_1 = RESLICE
├─ Process_2
│  ├─ SliceDone_2
│  ├─ Boundary_B2 refined_from B1
│  └─ BoundaryState_2 = Normal
└─ OperatorResponse_2 = CONTINUE
```

The Trajectory must preserve both the earlier provisional reading and the later refinement.

Boundary history is therefore not a flat list of labels.

It is a graph of runtime-readable relations.

---

## 8. Boundary Lineage Graph

A minimal Boundary lineage model may be:

```python
class BoundaryRecord:
    boundary_id: str
    source_slice_id: str
    source_slice_done_ref: str
    trajectory_id: str

    orientation_ref: str | None
    slice_policy_ref: str | None
    context_refs: list[str]

    evidence_refs: list[str]
    readability: str
    confidence: float | None

    parent_boundary_refs: list[str]
    lineage_relations: list[str]
    metadata: dict
```

```python
class BoundaryStateRecord:
    boundary_state_id: str
    boundary_id: str
    state: str

    source_slice_id: str
    trajectory_id: str
    scope: dict

    evidence_refs: list[str]
    prior_state_refs: list[str]
    relation_to_prior: str | None

    provisional: bool
    metadata: dict
```

These models are provisional GyroOS implementation models.

They do not redefine Gyro Logic.

---

## 9. Void Preservation

Void-related material requires explicit separation.

```text
Void as Boundary State
≠ Void evidence
≠ Void reference
≠ Deferred Void record
≠ Operator Response
```

Memory Runtime may preserve:

```text
Void Boundary State record
reason for unreadability
source Slice conditions
Boundary refs
Context refs
Difference / Deviation refs
future Re-Slice conditions
Defer record if selected
later resolution or reclassification
```

Example:

```text
BoundaryState_A = Void
↓ DEFER
DeferredRuntimeRecord_D1
↓ new Context
RESLICE
↓
BoundaryState_B = Unknown
↓ additional evidence
RESLICE
↓
BoundaryState_C = Normal
```

The prior Void record remains traceable.

It is not rewritten as if it had never existed.

---

## 10. Relation to Runtime Continuity

Boundary preservation supports Runtime Continuity by retaining connectability across changing readings.

```text
Boundary evidence
↓ retained with lineage
future Slice / Re-Slice / Jump / review
↓
new readable relation
```

This does not mean every Boundary record must remain active.

A record may become:

```text
active
historical
superseded_for_current_scope
deferred
archived
compressed
pointer_only
```

Runtime Continuity requires traceable relation, not permanent full-resolution storage.

---

## 11. Resolution Decay and Compression

GyroOS may reduce storage resolution.

Permitted forms include:

```text
full record
→ structured summary
→ evidence vector
→ lineage pointer
→ archived external reference
```

Compression is acceptable when the following remain recoverable:

```text
which Boundary was read
under which Slice scope
which Boundary State was assigned
which evidence supported it
which later record refined or contradicted it
which Operator Response followed
```

Silent loss of these relations is not acceptable.

---

## 12. Conflict and Coexistence

Multiple Boundary readings may coexist.

```text
Boundary_A
Boundary_B
Boundary_C
```

Possible relations:

```text
coexists_with
partially_overlaps
conflicts_with
higher_resolution_than
lower_resolution_than
context_specific_to
trajectory_specific_to
```

A conflict must not automatically cause:

```text
JUMP
STOP
DEFER
RESLICE
```

Conflict becomes evidence for Operator Response.

The decision remains with the Loop Controller.

---

## 13. Re-Slice Preservation

Re-Slice must preserve parent-child lineage.

```text
Boundary_B1
↓ RESLICE selected
ReSliceRequest_R1
↓ Re-Slice operation
Boundary_B2
```

Required relations may include:

```text
B2 refined_from B1
B2 reclassified_from B1
B2 conflicts_with B1
B2 coexists_with B1
```

Re-Slice must not silently replace B1.

---

## 14. Jump Preservation

Jump may leave the current local Boundary relation.

```text
Trajectory_A
├─ Boundary_B1
└─ JUMP
   ↓
Trajectory_B
└─ Boundary_B2
```

The JumpBoundary should preserve:

```text
source_boundary_refs
target_boundary_refs if available
source_boundary_state_refs
target_slice conditions
reason for discontinuous reconstruction
evidence refs
traceability relation
```

Jump may break local path continuity.

It must not silently erase Boundary lineage.

---

## 15. Stop Preservation

STOP ends the current execution connection within its control scope.

Before Stop finalization, GyroOS should preserve:

```text
final Boundary refs
final Boundary State refs
final SliceDone ref
final StabilityResult ref
final Operator Response
unresolved conflict refs
Void refs
resume / reconstruction metadata
```

Preserved evidence after Stop does not automatically mean a pending Defer relation.

```text
STOP evidence preservation
≠ DEFER pending relation
```

---

## 16. Defer Preservation

DEFER explicitly preserves a pending relation.

For Boundary-related Defer, retain:

```text
boundary_ref
boundary_state_ref
reason for Defer
pending relation
resume / review conditions
required Context or evidence
expiry conditions
resolved_by_response
```

The distinction remains:

```text
Stop
= execution connection ends

Defer
= relation remains pending
```

---

## 17. Retrieval Requirements

Memory Runtime should support retrieval by:

```text
boundary_id
boundary_state_id
slice_id
slice_done_ref
trajectory_id
object / relation ref
Context ref
Void ref
Operator Response ref
lineage relation
runtime time range
```

This supports:

```text
Re-Slice
Trajectory review
Dynamic Equivalence evaluation
Boundary conflict analysis
Void recovery
PoC visualization
runtime debugging
```

Retrieval support does not imply application-specific judgment.

---

## 18. API Implications

The canonical API mapping is handled in Priority C-8.

However, a Boundary-aware runtime response may expose compact lineage information:

```json
{
  "boundary_refs": ["boundary-12"],
  "boundary_state_refs": ["boundary-state-19"],
  "boundary_lineage": {
    "refined_from": ["boundary-08"],
    "conflicts_with": []
  },
  "trajectory_ref": "trajectory-04"
}
```

The API does not need to expose the complete internal evidence graph.

It must not flatten all Boundary history into one permanent label.

---

## 19. Bounded Preservation

Boundary preservation must be bounded.

Possible controls include:

```text
max_boundary_records_per_trajectory
max_boundary_lineage_depth
max_conflict_edges
max_full_resolution_records
memory tier policy
archive threshold
retention duration
criticality-based preservation
```

When limits are reached, GyroOS may:

```text
compress
summarize
archive
retain pointers
preserve critical records at higher resolution
```

The limit itself does not select Operator Response.

---

## 20. Design Constraints

Boundary Memory and Trajectory Preservation MUST NOT:

```text
turn Boundary State into a permanent object property
silently overwrite prior Boundary records
treat latest as always true
collapse Void evidence into Operator Response
automatically trigger RESLICE, JUMP, DEFER, or STOP
require permanent full-resolution storage
erase Slice-relative scope
erase Difference / Deviation lineage
mix GyroAuth decisions into GyroOS
```

Boundary Memory and Trajectory Preservation MUST:

```text
preserve Boundary lineage
preserve Boundary State history
preserve source Slice and Trajectory relations
preserve reclassification and conflict relations
support bounded storage and resolution decay
retain enough evidence for later reconnection or explanation
keep Stability and Operator Response conceptually separate
```

---

## 21. Key Insight

Boundary memory is not the storage of a final classification.

It is the preservation of how a distinction became readable and how that reading changed.

```text
Do not store only the latest Boundary State.
Preserve the trajectory of Boundary readability.
```

Japanese:

```text
最新のBoundary Stateだけを保存しない。
Boundaryがどのように読めるようになり、
その読みがどのように変化したかというTrajectoryを保持する。
```

---

## 22. Summary

Boundary and Boundary State are Slice-relative and provisional.

Memory Runtime preserves their evidence and lineage.

Trajectory Cache preserves their changes across Processes and Operator Responses.

The safe relation is:

```text
Slice
→ Boundary / Boundary State become readable
→ SliceDone preserves evidence
→ Stability reads the Path establishment
→ Operator Response selects the next relation
→ Memory Runtime and Trajectory Cache preserve lineage
```

The invariant Core remains unchanged:

```text
Structure → Slice → Stability
```

---

## Next

```text
Priority C-8: Boundary-aware API Mapping
```
