# 25. Local Inertia

---

## 1. Overview

This document defines **Local Inertia** after the Priority A–D Runtime alignment.

Local Inertia explains why some Runtime records, trajectory segments, and evidence remain locally available instead of being aggressively compressed, archived, or externalized.

It is not:

```text
a new Gyro Logic element
a cache implementation
a Loop Controller
a Stability measure
an Operator Response
a permanent pin
```

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Canonical Definition

```text
Local Inertia
= a provisional Runtime retention-priority relation indicating
  how strongly a record or evidence set should remain locally available
  for current or likely near-term Runtime continuity.
```

Local Inertia is an implementation-level support value.

It does not determine theoretical identity, Stability, or the next Operator Response.

---

## 3. Runtime Position

```text
SliceDone / StabilityResult / OperatorResponse / Continuity records
↓
Memory Runtime and Trajectory Cache preserve evidence and lineage
↓
Local Inertia evaluator produces retention-priority evidence
↓
Memory tiering / retrieval / compression policy
↓
optional Gyro-OOM Damper operation
```

Local Inertia may inform storage policy.

It must not control:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

---

## 4. Objects That May Carry Local Inertia

Local Inertia may be evaluated for:

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
DeferredRelationRecord
TrajectoryRecord
TrajectoryEdge
Dynamic Equivalence evidence
ExternalStorageReference
```

The use of `VoidRecord` and `ContextRecord` as generic collapsed objects is deprecated in this document.

Preferred terms are:

```text
ContextEvidence
VoidEvidence
BoundaryStateRecord
DeferredRelationRecord
```

---

## 5. Local Inertia Is Evidence, Not Authority

A high Local Inertia value may indicate:

```text
keep locally available
reduce compression priority
increase retrieval priority
preserve offline availability
protect lineage-bearing records
```

It does not mean:

```text
record is Stable
record is correct
record is final
record must be selected for RESLICE
record must remain forever
current trajectory must CONTINUE
```

A low Local Inertia value does not authorize deletion.

---

## 6. Candidate Factors

Candidate factors include:

```text
access_frequency
recency
active_scope_relevance
trajectory_connectivity
lineage_importance
boundary_reclassification_relevance
context_source_viability
void_traceability_need
deferred_relation_revisit_need
dynamic_equivalence_relevance
retrieval_cost
offline_requirement
application_demand
storage_pressure
reconstructability
```

These factors are implementation policy inputs.

They are not Gyro Logic definitions.

---

## 7. Canonical Factor Separation

The following values must remain distinct:

```text
local_inertia_score
boundary_readability
boundary_state_confidence
context_confidence
inferability_score
stability
response_confidence
pressure_severity
```

Incorrect:

```text
high Stability = high Local Inertia
high Boundary confidence = keep forever
low Local Inertia = STOP
```

Correct:

```text
multiple retention factors
↓
Local Inertia evaluation
↓
storage-policy evidence
```

---

## 8. LocalInertiaEvidence Model

```python
class LocalInertiaEvidence:
    evidence_id: str
    target_ref: str
    target_type: str
    score: float
    factor_values: dict[str, float]
    decisive_factor_refs: list[str]
    active_scope_ref: str | None
    policy_ref: str
    calculated_at_process_ref: str
    provisional: bool
    metadata: dict
```

The evidence should preserve how the score was produced.

A score without factor traceability should not be treated as authoritative.

---

## 9. Current Scope and Historical Scope

Local Inertia is scope-relative.

```text
high inertia in current scope
≠ permanent global importance
```

Recommended distinction:

```text
current_scope_inertia
historical_relevance
retrieval_priority
archive_resistance
```

A record may lose current-scope inertia while remaining historically important.

Historical records and lineage must not be deleted merely because their current-scope score decays.

---

## 10. Storage Tier Impact

Local Inertia may influence storage tier policy.

Possible high-inertia effects:

```text
hot or warm placement
reduced compression rate
local materialization
faster retrieval
preserved offline copy
```

Possible low-inertia effects:

```text
summary representation
vector representation
pointer-only local representation
cold archive candidacy
external materialization on demand
```

These are policy possibilities, not direct universal mappings.

Incorrect:

```text
score < threshold → archive automatically
```

Safer:

```text
Local Inertia evidence
+
active-scope requirements
+
lineage requirements
+
reconstructability
+
Gyro-OOM pressure
+
storage policy
↓
selected storage operation
```

---

## 11. Relation to Boundary Evidence

Boundary evidence may gain Local Inertia when it is important for:

```text
current Slice interpretation
Boundary State reclassification lineage
conflicting Boundary comparison
current-scope selection
future Re-Slice source reconstruction
Dynamic Equivalence evaluation
```

A prior Boundary State record may retain high historical relevance even after another record:

```text
supersedes_for_current_scope
```

This relation does not erase the earlier record.

---

## 12. Relation to ContextEvidence

`ContextEvidence` may gain Local Inertia when it is:

```text
repeatedly referenced
selected as a RESLICE source
important to Boundary readability
needed to reconstruct a prior Slice
part of an active context-linked lineage
required for offline continuity
```

However:

```text
high Context inertia
≠ automatic RESLICE
```

The Loop Controller still owns Operator Response selection.

---

## 13. Relation to VoidEvidence and Deferred Relations

The following must remain separate:

```text
Void as Boundary State
VoidEvidence
Void reference
DeferredRelationRecord
DEFER response
```

`VoidEvidence` may gain Local Inertia when its traceability is needed for:

```text
future classification
Boundary-relative reconstruction
pending relation revisit
trajectory explanation
safety or audit requirements
```

A `DeferredRelationRecord` may independently gain Local Inertia when its revisit condition is near or its source evidence remains active.

`VoidEvidence` must not contain:

```python
deferred: bool
resolved: bool
```

---

## 14. Relation to Trajectory Cache

Trajectory Cache may store Local Inertia evidence and indexes.

Recommended relation:

```text
TrajectoryRecord / TrajectoryEdge
↓
LocalInertiaEvidence
↓
current-scope cache and retrieval policy
```

High trajectory inertia may arise from:

```text
active continuity
important branch point
RESLICE lineage
JUMP reconnection
DEFER pending relation
STOP boundary auditability
Boundary State transition history
```

Trajectory similarity alone must not determine inertia or Dynamic Equivalence.

---

## 15. Relation to Runtime Continuity

Local Inertia may preserve records needed to explain the continuity effect of:

```text
CONTINUE = direct connection
ADJUST   = bounded continuous modification
RESLICE  = new Slice from retained source
JUMP     = non-continuous reconnection
DEFER    = pending relation
STOP     = current-scope execution boundary
```

It does not select any of these responses.

---

## 16. Relation to Gyro-OOM Damper

Gyro-OOM pressure may reduce the practical effect of Local Inertia.

```text
Local Inertia evidence
+
DamperPressureEvidence
+
lineage and reconstructability requirements
↓
storage-operation policy
```

The Gyro-OOM Damper may apply:

```text
REDUCE_RESOLUTION
COMPRESS_CONTEXT_EVIDENCE
COMPRESS_TRAJECTORY
ARCHIVE_COLD
FREEZE_BRANCH_FOR_CURRENT_SCOPE
```

High Local Inertia resists aggressive reduction but does not absolutely prevent it.

The Damper and Local Inertia evaluator do not choose Operator Responses.

---

## 17. Offline and Degraded-network Continuity

Local Inertia may support bounded offline continuity by prioritizing local availability of:

```text
active Runtime Structure records
current Slice lineage
active Boundary and Boundary State records
recent ContextEvidence
required VoidEvidence and DeferredRelation records
active trajectory segments
retrieval indexes
```

Offline continuity does not mean complete replication.

It means preserving a bounded set of records sufficient for limited Runtime continuity or safe deferral.

---

## 18. Inertia Decay

Local Inertia is provisional and should be recalculated.

Possible decay factors:

```text
time since last access
current-scope transition
reduced source viability
completed retrieval or reconstruction
archived but reconstructable copy
closed application session
resolved pending relation
reduced Dynamic Equivalence relevance
```

A Boundary State reclassification or pending-relation resolution does not justify deleting prior evidence.

Decay changes retention priority, not historical truth.

---

## 19. Local Inertia Policy

```python
class LocalInertiaPolicy:
    factor_weights: dict[str, float]
    hot_threshold: float
    warm_threshold: float
    pointer_threshold: float
    offline_threshold: float
    lineage_floor: float
    unresolved_relation_floor: float
    active_scope_floor: float
    decay_rate: float
    metadata: dict
```

Thresholds guide storage policy.

They do not directly execute archive, compression, RESLICE, DEFER, JUMP, or STOP.

---

## 20. API Implications

Possible support endpoints:

```text
GET  /inertia/state
GET  /inertia/evidence/{evidence_id}
GET  /inertia/object/{object_id}
POST /inertia/evaluate
POST /inertia/policy
```

`POST /inertia/evaluate` returns retention-priority evidence.

It must not mutate Runtime Continuity or choose Operator Response.

The main Runtime endpoint remains:

```text
POST /loop/step
```

---

## 21. Design Constraints

Local Inertia MUST NOT:

```text
redefine Structure → Slice → Stability
control the Loop
select OperatorResponse
substitute for Stability
substitute for Boundary readability or confidence
be treated as permanent memory
encode DEFER state inside VoidEvidence
automatically trigger RESLICE
silently authorize deletion
make application or authentication decisions
```

Local Inertia MUST:

```text
produce traceable retention-priority evidence
remain scope-relative and provisional
preserve historical and current-scope views separately
support Memory Runtime and Trajectory Cache
protect identity and lineage-bearing records
cooperate with Gyro-OOM pressure policy
support bounded offline continuity when applicable
```

---

## 22. Key Insight

```text
Local Inertia is not persistence authority.
It is evidence for bounded local retention.
```

Repeated or current relevance may create local persistence pressure, but Runtime responsibility boundaries remain unchanged.

---

## 23. Summary

Local Inertia provides a traceable, provisional indication of which Runtime records should remain locally available.

It supports:

```text
Memory Runtime
Trajectory Cache
Boundary and Context lineage
Void and deferred-relation traceability
Gyro-OOM damping
bounded offline continuity
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
