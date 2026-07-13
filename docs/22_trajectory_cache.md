# 22. Trajectory Cache

---

## 1. Overview

This document defines the **Trajectory Cache** model for GyroOS after the Gyro Logic v3.1 Core Definition refinement and the Priority B / Priority C Runtime alignment.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Trajectory Cache is not a Core element, Runtime Stage, Loop Controller, or source of Operator Response.

Its role is to preserve bounded, queryable evidence of how Runtime relations remain connectable, become reclassified, branch, defer, stop, or reconnect across Gyro Processes.

---

## 2. Core Definition

```text
Trajectory Cache
= a bounded Runtime index and cache of process-to-process evidence,
  lineage, branch relations, and continuity changes.
```

Short reading:

```text
Trajectory Cache preserves how Runtime readings changed and what may still be connected.
```

It is not merely:

```text
a chronological log
latest-state storage
one continuous path
an identity verdict
an Operator Response engine
```

---

## 3. Position in GyroOS

```text
Gyro Processₙ
↓
SliceDoneₙ
↓
StabilityResultₙ
↓
OperatorResponseₙ
↓
RuntimeContinuityResultₙ
↓
Gyro Processₙ₊₁ when connected
```

Trajectory Cache may retain references to every part of this chain.

It does not decide:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

The Loop Controller owns Operator Response selection.

---

## 4. Relation to Memory Runtime

Memory Runtime and Trajectory Cache have different responsibilities.

```text
Memory Runtime
= preserves evidence objects, records, lineage, resolution, and reconstructability

Trajectory Cache
= indexes and summarizes how those records relate across Gyro Processes
```

Therefore:

```text
Trajectory Cache ≠ Memory Runtime
Trajectory summary ≠ source record
current trajectory view ≠ complete history
```

Trajectory Cache may reference Memory Runtime records without duplicating all source content.

---

## 5. What Trajectory Cache Stores

Recommended references include:

```text
process_refs
runtime_structure_refs
slice_refs
deviation_refs
boundary_refs
boundary_state_refs
context_refs
void_refs
stability_refs
response_refs
continuity_refs
deferred_relation_refs
```

Recommended relational summaries include:

```text
stability_summary
deviation_summary
boundary_readability_summary
boundary_state_change_summary
context_source_summary
void_evidence_summary
response_summary
continuity_summary
orientation_summary
branch_summary
lineage_summary
local_inertia_summary
dynamic_equivalence_evidence
```

No summary may silently replace the referenced source records.

---

## 6. Candidate Data Model

```python
class TrajectoryCacheEntry:
    trajectory_id: str

    process_refs: list[str]
    runtime_structure_refs: list[str]
    slice_refs: list[str]

    deviation_refs: list[str]
    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    stability_refs: list[str]
    response_refs: list[str]
    continuity_refs: list[str]
    deferred_relation_refs: list[str]

    parent_trajectory_refs: list[str]
    child_trajectory_refs: list[str]
    branch_point_refs: list[str]

    stability_summary: dict
    deviation_summary: dict
    boundary_summary: dict
    context_summary: dict
    void_summary: dict
    response_summary: dict
    continuity_summary: dict
    orientation_summary: dict

    dynamic_equivalence_evidence: dict
    local_inertia_summary: dict

    current_scope_view_ref: str | None
    resolution_level: str
    storage_tier: str
    metadata: dict
```

This model is provisional.

It is an implementation mapping, not a Gyro Logic definition.

---

## 7. Trajectory Is Not Necessarily One Line

GyroOS must not assume:

```text
one trajectory = one uninterrupted linear sequence
```

A Runtime trajectory may contain:

```text
direct continuation
bounded adjustment
Re-Slice lineage
non-continuous Jump reconnection
deferred pending relation
branch coexistence
current-scope Stop boundary
conflicting readings
```

A safer model is a bounded directed relation graph with ordered process sections.

```text
Trajectory_A
├─ direct connection → Process_2
├─ RESLICE lineage → Process_3
├─ JUMP branch → Trajectory_B
└─ DEFER pending relation → DeferredRelation_1
```

The first PoC may use ordered lists, but the conceptual model must permit branching and lineage.

---

## 8. Runtime Continuity Mapping

Priority B defines Runtime Continuity as connectability across Runtime relations.

Trajectory Cache should preserve the continuity effect of each Operator Response.

```text
CONTINUE
= direct connection through the current established Path

ADJUST
= bounded continuous modification preserving continuity

RESLICE
= another Slice from a retained source relation

JUMP
= non-continuous reconnection request

DEFER
= pending relation with future connectability preserved

STOP
= execution connection ended in the current control scope
```

These are not inferred from trajectory shape alone.

They are recorded from Operator Response and Runtime Continuity results.

---

## 9. Boundary-aware Trajectory Preservation

Trajectory Cache must support Boundary-aware records.

It should preserve:

```text
which Boundary became readable
under which Slice
with which Orientation and Context
which relation received which Boundary State
how that classification later changed
which evidence conflicted or coexisted
which record is active for current scope
```

Example:

```text
Process_1
BoundaryState_A = UNKNOWN

Process_2
BoundaryState_B = NORMAL
BoundaryState_B reclassified_from BoundaryState_A
```

The later state must not overwrite the earlier state.

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

---

## 10. Void, Defer, and Trajectory

The following must remain distinct:

```text
Void as Boundary State
VoidEvidence
Void reference
DeferredRelationRecord
DEFER response
```

Trajectory Cache may preserve all of them as separate references.

Incorrect:

```text
void_ref exists
→ trajectory is deferred
```

Correct:

```text
VoidEvidence retained
+
OperatorResponse = DEFER
+
DeferredRelationRecord created
+
Trajectory references all three separately
```

A deferred relation may later be:

```text
reopened
re-sliced
reconnected by Jump
ended for current scope
left pending
```

without rewriting its prior history.

---

## 11. Relation to Re-Slice

Trajectory Cache may locate retained source evidence after the Loop Controller selects `RESLICE`.

```text
Loop Controller selects RESLICE
↓
Trajectory Cache locates source refs and lineage
↓
Memory Runtime retrieves or materializes records
↓
Re-Slice Engine executes another Slice
```

Trajectory Cache does not decide to Re-Slice.

The older response name:

```text
RESLICE_CONTEXT
```

is represented as:

```text
RESLICE with Context source references
```

---

## 12. Context-linked Trajectory

A Context-linked Loop is one possible trajectory pattern.

```text
Processₙ
→ ContextEvidenceₙ retained
→ OperatorResponseₙ = RESLICE
→ SliceRequest(source=context_evidence)
→ Processₙ₊₁
```

Trajectory Cache may retain:

```text
context_chain
source_chain
reslice_depth
visited_slice_refs
cycle_evidence
branch points
```

Context existence, confidence, or inferability does not automatically create a new trajectory section.

---

## 13. Jump and Branch Preservation

`JUMP` requests non-continuous reconnection.

A Jump may establish a new trajectory branch while preserving the prior branch.

```text
Trajectory_A
↓ JUMP selected
Trajectory_B
```

Trajectory Cache must preserve:

```text
source trajectory
source process
source SliceDone
selected response
reason and evidence refs
reconnection target
new branch identity
continuity relation
```

Jump does not automatically imply:

```text
prior trajectory failure
loss of Stability
not-equivalent identity
history deletion
```

Dynamic Equivalence remains a separate Runtime reading.

---

## 14. STOP and Current Scope

`STOP` ends execution connection in the current control scope.

Trajectory Cache should preserve:

```text
stop response ref
control scope ref
last established or retained source
termination reason
retained evidence refs
possible external or future reopening relation
```

STOP is not DEFER.

```text
STOP
= not pending in the current control scope

DEFER
= pending with future connectability preserved
```

A stopped trajectory record may remain queryable without being active.

---

## 15. Current Scope View

Trajectory history must remain traceable, while Runtime may still require a current view.

```python
class TrajectoryCurrentScopeView:
    trajectory_id: str
    active_process_ref: str | None
    active_slice_ref: str | None
    active_boundary_state_refs: list[str]
    active_context_refs: list[str]
    pending_relation_refs: list[str]
    latest_response_ref: str | None
    latest_continuity_ref: str | None
    execution_connected: bool
    metadata: dict
```

The current view does not delete historical records.

```text
supersedes_for_current_scope
≠ universal invalidation
```

---

## 16. Trajectory Index

Recommended indexes include:

```text
trajectory_id
process_id
slice_id
boundary_id
boundary_state_id
context_id
void_id
response_type
continuity_type
parent_trajectory_id
branch_point_id
orientation_signature
stability_range
deviation_pattern
dynamic_equivalence_group
current_scope_status
```

Candidate model:

```python
class TrajectoryIndex:
    by_trajectory_id: dict[str, str]
    by_process_id: dict[str, list[str]]
    by_slice_id: dict[str, list[str]]
    by_boundary_id: dict[str, list[str]]
    by_boundary_state_id: dict[str, list[str]]
    by_context_id: dict[str, list[str]]
    by_void_id: dict[str, list[str]]
    by_response_type: dict[str, list[str]]
    by_continuity_type: dict[str, list[str]]
    by_parent_trajectory_id: dict[str, list[str]]
    by_equivalence_group: dict[str, list[str]]
```

---

## 17. Resolution and Compression

Trajectory Cache follows Memory Runtime resolution levels:

```text
full
summary
vector
pointer
```

Compression may reduce payload detail while preserving:

```text
record identity
ordering
branch relations
lineage relations
continuity effects
source refs
evidence refs
reconstructability metadata
```

Incorrect:

```text
full trajectory
→ summary without lineage
→ latest state only
```

Correct:

```text
full trajectory
→ reconstructable summary
→ directional representation with lineage refs
→ external pointer with integrity metadata
```

---

## 18. Cache Lifecycle

Recommended lifecycle operations are:

```text
record
index
extend
link
branch
activate_for_scope
summarize
compress
archive
retrieve
materialize
```

Trajectory Cache does not perform these conceptual actions by itself:

```text
stabilize
continue
defer
jump
stop
```

It records and indexes the results of those Runtime responsibilities.

---

## 19. Dynamic Equivalence

Trajectory Cache provides evidence for Dynamic Equivalence, including:

```text
process lineage
Boundary changes
Stability history
Deviation history
Context transitions
Void evidence
Response transitions
continuity effects
Jump branches
current-scope and historical views
```

Trajectory similarity alone does not establish Dynamic Equivalence.

Without sufficient evidence, the safe result remains:

```text
undecidable
```

Dynamic Equivalence does not make application-specific identity or authentication decisions.

---

## 20. Local Inertia

Local Inertia may use Trajectory Cache evidence to estimate which records should remain locally available.

Candidate factors include:

```text
recent access
active-scope relevance
Re-Slice source relevance
Boundary lineage relevance
pending DEFER relation
unresolved Void evidence
branch reconstruction need
Dynamic Equivalence evidence need
```

Local Inertia influences retention priority.

It does not select Operator Response or determine Stability.

---

## 21. Cache Pressure

Possible pressure evidence includes:

```text
trajectory_count_high
hot_cache_overflow
lineage_growth
context_chain_growth
reslice_branch_growth
void_reference_accumulation
pending_relation_growth
equivalence_group_expansion
```

Trajectory Cache reports these as evidence.

It does not automatically select:

```text
DEFER
JUMP
STOP
RESLICE
```

The Loop Controller integrates pressure evidence with other Runtime evidence.

---

## 22. API Implications

Possible support endpoints include:

```text
GET  /trajectory/{trajectory_id}
GET  /trajectory/{trajectory_id}/summary
GET  /trajectory/{trajectory_id}/history
GET  /trajectory/{trajectory_id}/branches
GET  /trajectory/{trajectory_id}/boundaries
GET  /trajectory/{trajectory_id}/current-scope
GET  /trajectory/search
POST /trajectory/retrieve
POST /trajectory/materialize
POST /trajectory/compress
```

These are support endpoints.

The primary Runtime endpoint remains:

```text
POST /loop/step
```

Runtime states such as `DEFER`, `STOP`, or a `VOID` Boundary State may be returned through normal successful transport semantics.

---

## 23. Design Constraints

Trajectory Cache MUST NOT:

```text
redefine Structure → Slice → Stability
control the Loop
select Operator Response
compute Stability as a side effect
collapse Boundary State into Stability
collapse VoidEvidence into DEFER
replace Memory Runtime
silently overwrite prior records
reduce a branch graph to latest state only
silently delete Difference / Deviation evidence
make GyroAuth decisions
```

Trajectory Cache MUST:

```text
preserve process ordering and lineage
preserve branch and reconnection relations
preserve Boundary and Boundary State changes
preserve Context and Void evidence references
preserve response and continuity effects
separate current-scope view from complete history
support bounded retrieval and compression
support Re-Slice source lookup
support Dynamic Equivalence evidence
report cache pressure as evidence
```

---

## 24. Key Insight

```text
History records what happened.
Memory preserves the evidence.
Trajectory Cache preserves how readings and connections changed across Processes.
```

In short:

```text
Trajectory is not one line.
Trajectory is traceable connectability with lineage.
```

---

## 25. Summary

Trajectory Cache is a bounded continuity and lineage substrate for GyroOS.

It preserves how Slice results, Boundary readings, Stability, Operator Responses, and Runtime Continuity relate across Processes without changing the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

---

## 26. Next

```text
Priority D-8: docs/26_poc_runtime_object_graph.md Alignment
```
