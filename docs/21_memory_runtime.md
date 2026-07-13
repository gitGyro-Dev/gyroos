# 21. Memory Runtime

---

## 1. Overview

This document defines the Memory Runtime model for GyroOS after the Gyro Logic v3.1 Core Definition refinement and the Priority B / Priority C Runtime alignment.

Memory Runtime preserves runtime evidence, lineage, and reconstructable relations under bounded storage resources.

It does not redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Memory Runtime is not a Core element, Runtime Stage, controller, classifier, or response owner.

---

## 2. Runtime Position

The aligned Runtime relation is:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done {
    representation
    Difference / Deviation
    Boundary evidence if readable
    Boundary State records if classifiable
    Context evidence / references
    Void evidence / references if retained
  }
}
↓
StabilityResult
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
Runtime Continuity relation
```

Memory Runtime supports this relation by retaining evidence and references before, during, and after Process transitions.

It does not decide any transition.

---

## 3. Core Principle

```text
Memory Runtime
= bounded preservation of evidence, lineage, and future reconstructability
```

Its purpose is not to keep every object at full resolution forever.

Its purpose is to preserve enough relation for later Runtime reading.

Therefore:

```text
preservation
≠ permanent full-resolution storage

compression
≠ forgetting

latest record
≠ complete history

current-scope view
≠ universal truth
```

---

## 4. Responsibility Boundary

Memory Runtime may:

```text
store
reference
index
summarize
compress
archive
retrieve
materialize
link lineage
expose current-scope views
report memory pressure
```

Memory Runtime must not:

```text
generate Boundary by itself
classify Boundary State by itself
measure Stability by itself
select Operator Response
start Re-Slice
perform Jump
Defer a relation by itself
Stop execution
make GyroAuth decisions
```

Correct relation:

```text
Runtime engine or controller produces a record or decision
↓
Memory Runtime preserves it
```

Incorrect relation:

```text
Memory record exists
↓
Memory Runtime selects next action
```

---

## 5. Canonical Memory Objects

Recommended object families:

```text
RuntimeStructureRecord
SliceDoneRecord
DeviationRecord
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityRecord
OperatorResponseRecord
ContinuityRecord
TrajectoryRecord
CompressedReference
CurrentScopeView
```

These names preserve the Priority C distinction:

```text
*_evidence
= directly retained evidence objects

*_records
= identity-bearing Runtime records with lineage

*_refs
= references to separately retained records
```

---

## 6. SliceDoneRecord

```python
class SliceDoneRecord:
    slice_id: str
    process_id: str
    process_index: int
    timestamp: float

    representation_ref: str
    deviation_ref: str

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str | None
    slice_policy_ref: str | None
    trajectory_ref: str | None

    parent_slice_ref: str | None
    source_refs: list[str]

    readability_summary: dict
    resolution_level: str
    storage_tier: str
    metadata: dict
```

A `SliceDoneRecord` stores the readable established result of Slice and the references needed to reconstruct how it became readable.

It is not a Stability record and does not contain Operator Response ownership.

---

## 7. BoundaryEvidence

```python
class BoundaryEvidence:
    boundary_id: str
    source_slice_id: str
    source_process_id: str

    relation_refs: list[str]
    evidence_refs: list[str]
    context_refs: list[str]

    orientation_ref: str | None
    slice_policy_ref: str | None

    boundary_readability: float | None
    resolution: str | None
    origin_mode: str | None

    lineage_refs: list[str]
    provisional: bool
    resolution_level: str
    storage_tier: str
    metadata: dict
```

The canonical statement remains:

```text
The distinction became readable through the current Slice.
```

`origin_mode` such as `formed`, `exposed`, `retained`, or `unknown` is optional implementation metadata.

---

## 8. BoundaryStateRecord

```python
class BoundaryStateRecord:
    boundary_state_id: str
    boundary_ref: str
    relation_ref: str | None

    slice_ref: str
    process_ref: str
    trajectory_ref: str | None

    state_type: str
    boundary_state_confidence: float | None
    relation_readability: float | None
    inferability: float | None

    evidence_refs: list[str]
    context_refs: list[str]
    orientation_ref: str | None

    provisional: bool
    lineage_relations: list[dict]
    resolution_level: str
    storage_tier: str
    metadata: dict
```

Initial candidate values:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

These are provisional relation classifications, not permanent object properties.

A later classification must not silently overwrite an earlier record.

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

## 9. ContextEvidence

```python
class ContextEvidence:
    context_id: str
    source_slice_id: str
    source_process_id: str

    relation_refs: list[str]
    evidence_refs: list[str]
    inferred_structure_ref: str | None

    source_type: str
    context_readability: float | None
    context_confidence: float | None
    inferability_score: float | None

    context_chain: list[str]
    provisional: bool
    resolution_level: str
    storage_tier: str
    metadata: dict
```

Context may become a future Re-Slice source candidate.

It does not start Re-Slice by itself.

---

## 10. VoidEvidence

Void-related memory must preserve the following separation:

```text
Void as Boundary State
VoidEvidence
Void reference
retained pending relation
DEFER response
RESLICE response
JUMP response
STOP response
```

Recommended object:

```python
class VoidEvidence:
    void_id: str
    source_slice_id: str
    source_process_id: str

    boundary_ref: str | None
    relation_ref: str | None
    evidence_refs: list[str]

    reason: str
    relation_readability: float | None
    connectability: float | None
    inferability: float | None

    lineage_refs: list[str]
    resolution_level: str
    storage_tier: str
    metadata: dict
```

The following fields must not be embedded as intrinsic Void properties:

```text
deferred: bool
resolved: bool
response_type
```

Those properties belong to separate records or current-scope views.

```text
VoidEvidence
≠ DEFER
```

A Void-related relation may later be reclassified or reconnected, but the original evidence remains traceable.

---

## 11. StabilityRecord

```python
class StabilityRecord:
    stability_id: str
    process_ref: str
    slice_ref: str

    value: float | None
    status: str
    continuability: bool | None
    reason: str | None
    evidence_refs: list[str]

    resolution_level: str
    storage_tier: str
    metadata: dict
```

Memory Runtime stores Stability results.

It does not infer that:

```text
stable → CONTINUE
unstable → STOP
not_evaluable → DEFER
```

Stability remains separate from Operator Response.

---

## 12. OperatorResponseRecord

```python
class OperatorResponseRecord:
    response_id: str
    process_ref: str

    response_type: str
    reason: str

    considered_evidence_refs: list[str]
    decisive_evidence_refs: list[str]
    conflicting_evidence_refs: list[str]

    response_confidence: float | None
    next_request_ref: str | None
    continuity_effect_ref: str | None

    resolution_level: str
    storage_tier: str
    metadata: dict
```

Canonical response types:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Compatibility aliases such as `RESLICE_CONTEXT`, `CHANGE_ORIENTATION`, and `DEFER_VOID` should be normalized before long-term storage when possible.

`VOID` is not an Operator Response.

---

## 13. ContinuityRecord

```python
class ContinuityRecord:
    continuity_id: str
    process_ref: str
    response_ref: str

    source_ref: str
    target_ref: str | None
    continuity_type: str

    pending: bool
    terminated_for_current_scope: bool
    evidence_refs: list[str]

    resolution_level: str
    storage_tier: str
    metadata: dict
```

This record preserves how the current establishment or retained relation connects to the next Runtime state.

It does not decide the connection.

---

## 14. TrajectoryRecord

```python
class TrajectoryRecord:
    trajectory_id: str

    process_refs: list[str]
    structure_refs: list[str]
    slice_refs: list[str]
    deviation_refs: list[str]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    stability_refs: list[str]
    response_refs: list[str]
    continuity_refs: list[str]

    current_scope_refs: dict
    summary_refs: list[str]

    resolution_level: str
    storage_tier: str
    metadata: dict
```

TrajectoryRecord preserves how Runtime readings changed across Processes.

It must not store only the latest Boundary State or latest response.

---

## 15. Current-Scope View

Historical records remain immutable or traceable.

Runtime may still require a concise view of what is active now.

```python
class CurrentScopeView:
    scope_id: str
    trajectory_ref: str

    active_structure_ref: str | None
    active_slice_ref: str | None
    active_boundary_refs: list[str]
    active_boundary_state_refs: list[str]
    active_context_refs: list[str]
    active_void_refs: list[str]
    active_stability_ref: str | None
    active_response_ref: str | None

    updated_at: float
    metadata: dict
```

A current-scope pointer does not erase prior records.

```text
supersedes_for_current_scope
≠ universal invalidation
```

---

## 16. Storage Tiers

Recommended tiers:

```text
hot
warm
cold
external
```

### hot

High-resolution evidence needed by the active Process or immediate next decision.

### warm

Recently used or likely to be retrieved for Re-Slice, comparison, or trajectory reading.

### cold

Compressed summaries and lineage-preserving records not required for immediate execution.

### external

External storage with retained identifiers, hashes, retrieval rules, and lineage pointers.

---

## 17. Resolution Levels

Recommended levels:

```text
full
structured_summary
evidence_vector
lineage_pointer
external_reference
```

Safe decay:

```text
full
→ structured summary
→ evidence vector
→ lineage pointer
→ archived external reference
```

The requirement is reconstructability appropriate to the retained relation.

Incorrect:

```text
full → delete latest-except
```

when that deletion destroys lineage, conflict evidence, or reclassification history.

---

## 18. Resolution Decay Rules

Resolution decay may consider:

```text
age
access frequency
active trajectory relevance
Boundary lineage relevance
Context relevance
Void reconnectability
response audit relevance
reconstruction cost
external retrieval availability
memory pressure
policy
```

The decay mechanism must not make semantic decisions such as:

```text
old record → irrelevant
low confidence → delete
superseded for current scope → universally invalid
Void unresolved → permanent
```

---

## 19. Memory Lifecycle

Recommended storage lifecycle:

```text
record
index
activate_for_scope
summarize
compress
archive
retrieve
materialize
link_new_evidence
```

### record

Persist a Runtime-produced evidence or decision record.

### index

Create lookup relations across Process, Slice, Boundary, Context, Void, Trajectory, Stability, Response, and Continuity.

### activate_for_scope

Point the current Runtime scope to selected retained records without rewriting history.

### summarize / compress

Reduce resolution while preserving required meaning and lineage.

### archive

Move data to cold or external storage while retaining reconstructable references.

### retrieve / materialize

Restore sufficient evidence for Re-Slice, trajectory reading, Dynamic Equivalence, audit, or later classification.

### link_new_evidence

Append lineage or conflict relations without silently overwriting prior records.

The storage lifecycle must not use `stabilize` or `defer` as Memory-owned semantic actions.

Stability and DEFER belong to other Runtime responsibilities.

---

## 20. Interaction with Re-Slice

Correct relation:

```text
Loop Controller selects RESLICE
↓
SliceRequest identifies retained source refs
↓
Memory Runtime retrieves or materializes source evidence
↓
Re-Slice Engine executes another Slice
```

Memory Runtime does not decide to Re-Slice.

Possible source refs include:

```text
SliceDoneRecord
ContextEvidence
BoundaryEvidence
BoundaryStateRecord
VoidEvidence
Trajectory segment
prior Process result
retained relation
```

---

## 21. Interaction with DEFER

DEFER is an Operator Response.

Memory Runtime supports DEFER by preserving:

```text
pending source relation
reason evidence
revisit conditions
current-scope pending pointer
future retrieval references
```

Recommended separate record:

```python
class DeferredRelationRecord:
    deferred_relation_id: str
    source_ref: str
    response_ref: str
    deferred_at_process_ref: str
    revisit_condition: dict | None
    evidence_refs: list[str]
    pending: bool
    metadata: dict
```

This record references Void evidence when relevant, but it is not part of `VoidEvidence` itself.

---

## 22. Interaction with Dynamic Equivalence

Dynamic Equivalence may consume:

```text
TrajectoryRecord
SliceDoneRecord
DeviationRecord
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityRecord
OperatorResponseRecord
ContinuityRecord
```

Memory Runtime provides evidence only.

It does not decide equivalence.

When evidence is insufficient, the consuming runtime may return:

```text
undecidable
```

---

## 23. Memory Pressure and Gyro-OOM

Memory Runtime may report:

```text
memory_pressure
hot_tier_overflow
lineage_growth
reslice_depth_growth
context_chain_growth
void_evidence_accumulation
trajectory_branch_growth
retrieval_cost_growth
```

These are evidence inputs.

They do not directly select:

```text
DEFER
JUMP
STOP
RESLICE
```

The Loop Controller remains the response owner.

---

## 24. API Implications

Possible support endpoints:

```text
GET  /memory/state
GET  /memory/record/{record_id}
GET  /memory/trajectory/{trajectory_id}
GET  /memory/boundary/{boundary_id}
GET  /memory/context/{context_id}
GET  /memory/void/{void_id}
POST /memory/retrieve
POST /memory/materialize
POST /memory/compress
```

These endpoints expose or transform stored representations.

They do not create Operator Responses.

The primary Runtime endpoint remains:

```text
POST /loop/step
```

---

## 25. Design Constraints

Memory Runtime MUST NOT:

```text
redefine Structure → Slice → Stability
control the Loop
store only the latest classification
silently overwrite Boundary State history
embed DEFER state inside VoidEvidence
treat compression as forgetting
treat current-scope selection as universal truth
automatically start Re-Slice
automatically Jump or Stop
make GyroAuth decisions
```

Memory Runtime MUST:

```text
preserve SliceDone lineage
preserve Difference / Deviation references
preserve Boundary and Boundary State history
preserve Context and Void evidence separately
preserve Stability and Operator Response separately
support current-scope views without deleting history
support bounded resolution decay
support reconstruction and retrieval
report memory pressure as evidence
```

---

## 26. Key Insight

Memory Runtime is not storage accumulation.

It is controlled preservation of how Runtime relations became readable and how those readings changed.

```text
Memory preserves evidence.
Trajectory preserves change.
Current scope selects a view.
Operator Response selects what happens next.
```

---

## 27. Summary

Memory Runtime preserves evidence, lineage, and reconstructability across Gyro Processes while controlling storage cost.

It keeps the following distinct:

```text
SliceDone
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityRecord
OperatorResponseRecord
ContinuityRecord
TrajectoryRecord
```

It supports Runtime Continuity without changing the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

---

## Next

```text
docs/22_trajectory_cache.md
```
