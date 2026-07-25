# 113. vNext Cross-layer Semantic / Readability / Continuity / Trajectory Composition Review

---

## 1. Purpose

This document reviews whether the isolated vNext layers can compose without collapsing their distinct responsibilities:

```text
Semantic realization
+
Incorporated Readability
+
Continuity Readability
+
Trajectory
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

This review does not create a fourth Core stage, unified Runtime result, persistence transaction, canonical aggregate, or automatic cross-layer pipeline.

---

## 2. Reviewed Layers

### Semantic realization

```text
StabilityScene
StabilityObservation
DifferenceObject
BoundaryEvaluation
SemanticRealizationBundle
SemanticAssemblyService
```

### Incorporated Readability

```text
ReadabilityContext
IncorporationRecord
SceneReadabilityRelation
ReadabilityRelationBundle
IncorporatedReadabilityAssemblyService
```

### Continuity Readability

```text
ContinuityReadabilityContext
ContinuityRelationRecord
ContinuityRelationBundle
ContinuityReadabilityAssemblyService
```

### Trajectory

```text
TrajectoryNode
TrajectoryEdge
TrajectoryGraph
TrajectoryAssemblyService
```

---

## 3. Composition Principle

Composition is allowed only through explicit references.

```text
complete record ownership
≠
cross-layer reference
```

Each layer owns only its own records. A later layer may reference an earlier record, but it does not rewrite, merge, replace, canonicalize, or automatically synchronize that record.

Decision:

```text
Cross-layer composition by explicit reference
= ACCEPTED

Cross-layer composition by shared ownership
= REJECTED
```

---

## 4. Semantic to Readability Boundary

`SceneReadabilityRelation` explicitly links:

```text
StabilityScene
↔
ReadabilityContext
```

This relation does not imply:

```text
scene owns context
context derives from scene
context must update with scene
scene must update with context
```

`ReadabilityRelationBundle` groups readability records by reference but remains separate from `SemanticRealizationBundle`.

Decision:

```text
Semantic / Incorporated Readability reference boundary
= ACCEPTED
```

---

## 5. Readability to Continuity Boundary

`ContinuityReadabilityContext` may explicitly reference:

```text
readability_context_refs[]
source_record_refs[]
target_record_refs[]
```

It does not automatically select:

```text
current ReadabilityContext
latest ReadabilityContext
authoritative ReadabilityContext
canonical before/after chain
```

`ContinuityRelationRecord` is an explicit statement within one continuity-readability scope. It does not prove continuation, continuity success, Identity continuity, or next action.

Decision:

```text
Incorporated Readability / Continuity Readability boundary
= ACCEPTED
```

---

## 6. Continuity to Trajectory Boundary

The following remains explicit:

```text
ContinuityRelationRecord
≠
TrajectoryEdge
```

A `TrajectoryEdge` may carry a caller-supplied `relation_ref` that points to a continuity relation. This is evidence linkage only.

No automatic mapping is performed from:

```text
continuity relation existence
continuity_state
readable
created_at
source / target references
```

into Trajectory edge type, authority, root, terminal, branch, merge, or gap semantics.

Decision:

```text
Continuity Readability / Trajectory boundary
= ACCEPTED
```

---

## 7. Semantic Records as Trajectory Nodes

`TrajectoryNode.record_ref` and `record_type` allow explicit references to records such as:

```text
StabilityScene
DifferenceObject
BoundaryEvaluation
ReadabilityContext
IncorporationRecord
ContinuityRelationRecord
```

The Trajectory layer does not resolve or validate the referenced record against a registry.

Therefore:

```text
TrajectoryNode
= reference wrapper

TrajectoryNode
≠ copied semantic/readability/continuity record
```

Decision:

```text
Cross-layer record referencing from Trajectory
= ACCEPTED
```

---

## 8. No Unified Canonical Aggregate

The following bundles remain separate:

```text
SemanticRealizationBundle
ReadabilityRelationBundle
ContinuityRelationBundle
TrajectoryGraph
```

This review does not introduce:

```text
VNextCanonicalResult
UnifiedSemanticState
CrossLayerRuntimeResult
AtomicCrossLayerPublication
```

Reason:

- each layer has a different scope;
- optional records may be absent;
- authority/current-selection semantics remain intentionally undefined;
- persistence and publication semantics are not yet defined;
- a unified aggregate would risk implying a canonical order or ownership relation.

Decision:

```text
Unified canonical aggregate
= NOT ADOPTED
```

---

## 9. Assembly Service Independence

The assembly services remain independent:

```text
SemanticAssemblyService
IncorporatedReadabilityAssemblyService
ContinuityReadabilityAssemblyService
TrajectoryAssemblyService
```

No service calls another service automatically.

Composition must be performed explicitly by a caller that supplies already-constructed references.

This avoids introducing an implicit pipeline such as:

```text
Semantic
→ Readability
→ Continuity
→ Trajectory
```

as a mandatory theoretical, temporal, causal, or Runtime order.

Decision:

```text
Assembly service independence
= ACCEPTED
```

---

## 10. Cross-layer Order Boundary

The visible implementation sequence does not define:

```text
theoretical establishment order
time order
causal order
importance order
canonical publication order
continuation order
Identity order
```

The only fixed Core sequence remains:

```text
Structure
↓
Slice
↓
Stability
```

All later vNext records are implementation-level descriptions, observations, readability scopes, relations, and groupings around explicit references.

Decision:

```text
Core order preservation
= ACCEPTED
```

---

## 11. Cross-layer Identity Boundary

The following remain distinct:

```text
same process_id
connected TrajectoryGraph
readable continuity relation
same record_type
same source / target chain
```

None of these alone prove Identity continuity.

Likewise:

```text
Identity break
≠ Trajectory break
≠ continuity break
≠ unreadable relation
```

Decision:

```text
Cross-layer Identity non-inference
= ACCEPTED
```

---

## 12. Runtime and Persistence Boundary

No cross-layer composition is connected to:

```text
POST /loop/step
ProcessExecutor
StabilityEngine
OperatorResponse selection
SQLite schema
repository reconstruction registry
public API models
Priority G/H canonical records
GyroAuth decisions
```

No atomic persistence or reconstruction semantics exist across the four layers.

Decision:

```text
Runtime isolation
= ACCEPTED

Persistence isolation
= ACCEPTED
```

---

## 13. Findings

No critical cross-layer contradiction was identified.

The architecture composes through explicit reference without requiring:

```text
shared ownership
record rewriting
automatic synchronization
canonical current-state selection
canonical authority selection
mandatory layer execution order
unified persistence transaction
```

Open areas remain intentionally outside this review:

```text
record registry / resolution
cross-layer persistence
public API exposure
Runtime production mapping
cross-layer publication semantics
migration / versioning
```

---

## 14. Final Decision

```text
Cross-layer Semantic / Readability / Continuity / Trajectory composition review
= COMPLETE

Semantic / Readability boundary
= ACCEPTED

Readability / Continuity boundary
= ACCEPTED

Continuity / Trajectory boundary
= ACCEPTED

Trajectory cross-record reference boundary
= ACCEPTED

Unified canonical aggregate
= NOT ADOPTED

Assembly service independence
= ACCEPTED

Core order preservation
= ACCEPTED

Runtime isolation
= ACCEPTED

Persistence isolation
= ACCEPTED

Critical design blocker
= NONE IDENTIFIED
```

---

## 15. Next

Proceed to:

```text
vNext isolated architecture completion review
```

That review should determine whether the isolated architecture is complete as a bounded PoC and identify the explicit gate before any Runtime, persistence, registry, or public API integration.