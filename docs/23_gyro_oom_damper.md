# 23. Gyro-OOM Damper

---

## 1. Overview

This document defines the Gyro-OOM Damper after the Priority A–D Runtime alignment.

The Gyro-OOM Damper is a bounded Runtime support mechanism for reducing expansion pressure across:

```text
Memory Runtime
Trajectory Cache
Context-linked Re-Slice chains
Boundary / Void evidence retention
Dynamic Equivalence evidence
```

It does not redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The Damper is not a Loop Controller, Stability controller, Operator Response owner, or process kill switch.

---

## 2. Canonical Definition

```text
Gyro-OOM Damper
= a bounded Runtime support mechanism that reports expansion pressure
  and applies selected storage or execution-bound operations
  without erasing evidence, lineage, or future reconstructability.
```

The Damper has two separate responsibilities:

```text
1. Pressure observation and evidence production
2. Execution of explicitly selected damping operations
```

It does not select:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

That responsibility belongs to the Loop Controller / Operator Response.

---

## 3. Runtime Position

```text
Memory Runtime / Trajectory Cache / Re-Slice limits
↓
DamperPressureEvidence
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
optional selected DamperOperation
↓
Memory / Trajectory preservation result
```

A storage-level Damper operation may occur without changing the Operator Response when policy permits.

Example:

```text
OperatorResponse = CONTINUE
+
DamperOperation = COMPRESS_RECORD
```

This means that Runtime Continuity continues while storage resolution is reduced safely.

---

## 4. Pressure Evidence

Recommended pressure evidence types:

```text
memory_pressure
hot_tier_overflow
context_chain_growth
reslice_depth_limit
trajectory_count_high
trajectory_branch_growth
void_evidence_accumulation
boundary_lineage_growth
equivalence_evidence_growth
cycle_evidence
cost_budget_pressure
retrieval_cost_growth
```

Pressure evidence is descriptive.

It is not an action.

Incorrect:

```text
reslice_depth_limit → STOP
void_evidence_accumulation → DEFER
memory_pressure → JUMP
```

Correct:

```text
pressure evidence
+
SliceDone evidence
+
StabilityResult
+
Boundary / Context / Void evidence
+
Trajectory state
+
Runtime policy
↓
Loop Controller selects OperatorResponse
```

---

## 5. DamperPressureEvidence Model

```python
class DamperPressureEvidence:
    evidence_id: str
    pressure_type: str
    source_refs: list[str]
    observed_value: float | int | None
    threshold_ref: str | None
    severity: float
    scope_ref: str
    recoverable: bool | None
    metadata: dict
```

`severity` is not:

```text
Stability
response_confidence
Boundary readability
Boundary State confidence
```

These values remain separate.

---

## 6. Canonical Damper Operations

The canonical storage and bounded-execution operations are:

```text
REDUCE_RESOLUTION
COMPRESS_CONTEXT_EVIDENCE
COMPRESS_TRAJECTORY
ARCHIVE_COLD
LIMIT_NEXT_RESLICE_REQUEST
FREEZE_BRANCH_FOR_CURRENT_SCOPE
MATERIALIZE_POINTER_ONLY
EVICT_RECONSTRUCTABLE_CACHE_COPY
```

These are Damper operations, not Operator Responses.

They must not be named:

```text
DEFER_VOID
REQUEST_JUMP
REQUEST_STOP
CHANGE_ORIENTATION
```

Those names mix storage support with Runtime response responsibility.

---

## 7. REDUCE_RESOLUTION

Reduce storage resolution while preserving references and reconstructability.

```text
full
→ summary
→ vector
→ pointer
```

Required retained information includes, when applicable:

```text
record identity
source refs
parent lineage
Boundary refs
Boundary State refs
Context refs
Void refs
Trajectory refs
content hash
retrieval policy
```

Resolution reduction must not silently remove Difference / Deviation history.

---

## 8. COMPRESS_CONTEXT_EVIDENCE

Compress `ContextEvidence` while preserving:

```text
context_id
source_slice_ref
source_process_ref
relation_refs
context_readability
context_confidence
inferability_score
source_type
context lineage
```

Correct:

```text
ContextEvidence.full
→ ContextEvidence.summary
```

Incorrect:

```text
ContextEvidence
→ delete because it was not selected for RESLICE
```

Context relevance and Operator Response selection are separate concerns.

---

## 9. COMPRESS_TRAJECTORY

Trajectory compression must preserve the Runtime graph rather than only its latest summary.

Required preservation includes:

```text
Process refs
Slice refs
Boundary refs
Boundary State reclassification lineage
Context refs
Void refs
Operator Response refs
Continuity edges
RESLICE lineage
JUMP branch points
DEFER pending relations
STOP boundaries
```

Incorrect:

```text
process history
→ one final stability average
```

Correct:

```text
high-resolution trajectory graph
→ reduced graph with recoverable identity and lineage
```

---

## 10. Void-related Pressure

The Damper must preserve the separation among:

```text
Void as Boundary State
VoidEvidence
Void reference
DeferredRelationRecord
DEFER response
```

`VoidEvidence` must not contain:

```python
deferred: bool
resolved: bool
```

A Void-related relation becomes pending only when the Loop Controller selects `DEFER`, after which a separate `DeferredRelationRecord` is created.

The Damper may compress or archive Void evidence only when traceability and retrieval remain sufficient.

---

## 11. LIMIT_NEXT_RESLICE_REQUEST

This operation constrains execution resources available to a future selected Re-Slice.

It may set or tighten:

```text
max_reslice_depth
max_source_chain_length
max_branch_count
max_materialized_records
max_execution_cost
max_runtime_duration
```

It does not select `RESLICE`, `DEFER`, `JUMP`, or `STOP`.

If no safe Re-Slice execution remains possible, the Damper emits evidence such as:

```text
reslice_not_executable_under_current_limits
```

The Loop Controller then selects the response.

---

## 12. FREEZE_BRANCH_FOR_CURRENT_SCOPE

A branch may be removed from the active current-scope view without deleting it from trajectory history.

```text
freeze for current scope
≠ delete
≠ universal invalidation
≠ STOP response
```

The operation should preserve:

```text
branch_ref
freeze_reason
pressure_evidence_refs
prior_current_scope_ref
retrieval_policy
```

A frozen branch may be restored or reconsidered by a later Process.

---

## 13. ARCHIVE_COLD

Move records to cold or external storage while retaining local references.

```text
full / summary
→ pointer
```

Required pointer data may include:

```text
external_uri
content_hash
record_type
trajectory_ref
retrieval_policy
resolution_level
```

Archive status must not be interpreted as low Stability, STOP, or loss of identity.

---

## 14. DamperOperation Model

```python
class DamperOperation:
    operation_id: str
    operation_type: str
    target_refs: list[str]
    selected_by_policy_ref: str | None
    related_response_ref: str | None
    pressure_evidence_refs: list[str]
    reason: str
    reversible: bool
    preserves_lineage: bool
    result_refs: list[str]
    metadata: dict
```

`related_response_ref` may be absent for storage-only operations.

The Damper operation remains subordinate to Runtime policy and Operator Response responsibility.

---

## 15. Damper Policy Model

```python
class DamperPolicy:
    max_reslice_depth: int
    max_context_chain_length: int
    max_hot_entries: int
    max_active_branches: int
    max_void_evidence_records: int
    max_boundary_lineage_records: int
    memory_pressure_threshold: float
    cold_archive_enabled: bool
    pointer_eviction_enabled: bool
    preserve_active_scope_records: bool
    metadata: dict
```

A policy threshold produces pressure evidence or permits a storage operation.

It does not define a universal Operator Response mapping.

---

## 16. Runtime Flow

```text
Runtime records and execution counters
↓
Gyro-OOM Damper observes pressure
↓
DamperPressureEvidence
↓
Loop Controller / Operator Response
↓
selected Runtime response
+
optional DamperOperation
↓
Memory Runtime / Trajectory Cache apply bounded preservation change
↓
operation result and lineage retained
```

---

## 17. API Implications

Possible support endpoints:

```text
GET  /damper/state
GET  /damper/pressure
GET  /damper/operations/{operation_id}
POST /damper/operations/apply
POST /damper/policy
```

`POST /damper/operations/apply` executes an already authorized Damper operation.

It must not become a second Loop Controller.

The main Runtime endpoint remains:

```text
POST /loop/step
```

---

## 18. Design Constraints

The Gyro-OOM Damper MUST NOT:

```text
redefine Structure → Slice → Stability
select OperatorResponse
act as Stability controller
treat pressure severity as Stability
encode Void as an action
store DEFER state inside VoidEvidence
execute JUMP or STOP
silently delete Difference / Deviation
erase Boundary State reclassification history
erase trajectory branches
make application or authentication decisions
```

The Gyro-OOM Damper MUST:

```text
produce traceable pressure evidence
preserve identity and lineage
prefer resolution reduction over destructive deletion
preserve current-scope and historical views separately
support retrieval and reconstructability
remain subordinate to Loop Controller and Memory Runtime responsibilities
keep bounded execution limits explicit
```

---

## 19. Key Insight

```text
Damping is not a response.
Damping is bounded preservation under pressure.
```

The Damper reduces expansion cost without deciding how Runtime Continuity should connect.

---

## 20. Summary

The Gyro-OOM Damper is a Runtime support mechanism that:

```text
observes pressure
produces evidence
applies selected bounded preservation operations
preserves lineage and reconstructability
```

It does not choose:

```text
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
```

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```
