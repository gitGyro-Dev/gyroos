# 105. vNext Continuity Readability Model Design

---

## 1. Purpose

This document defines the next isolated vNext design boundary for:

```text
Continuity Readability
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Continuity Readability is not added to the Core.

It is an implementation-level representation of what continuity relations are explicitly readable across related runtime references.

---

## 2. Required Separation

Continuity Readability must remain distinct from:

```text
history storage
RuntimeContinuityResult
OperatorResponse mapping
Identity continuity
Trajectory
current-context selection
incorporated readability
```

In particular:

```text
Identity break
≠ continuity break
```

and:

```text
continuity readability
≠ continuity success
≠ continuity guarantee
≠ continuation decision
```

A continuity relation may be readable while continuity is broken, partial, unresolved, or contested.

---

## 3. Proposed Minimal Models

The first implementation should be limited to:

```text
ContinuityReadabilityContext
+
ContinuityRelationRecord
```

### ContinuityReadabilityContext

Purpose:

Record the explicit references and conditions under which continuity may be read.

Proposed fields:

```text
continuity_readability_context_id
process_id
source_slice_ref
target_slice_ref
orientation_ref
context_refs[]
readability_context_refs[]
source_record_refs[]
target_record_refs[]
provisional
created_at
metadata
```

Meaning:

```text
source slice / target slice scope
+
explicit orientation and context references
+
explicit candidate source and target records
```

The model does not infer that a continuity relation exists.

### ContinuityRelationRecord

Purpose:

Record one explicit readability statement about continuity between source and target references.

Proposed fields:

```text
continuity_relation_id
process_id
continuity_readability_context_ref
source_ref
target_ref
relation_type
readable
continuity_state
provisional
authoritative
source_refs[]
evidence_refs[]
created_at
metadata
```

`relation_type` remains caller-supplied text in the first PoC.

`continuity_state` also remains caller-supplied text until a separate vocabulary review is complete.

---

## 4. What the Models May Express

The models may explicitly represent statements such as:

```text
relation is readable
relation is not readable
continuity appears preserved
continuity appears broken
continuity is partial
continuity is unresolved
continuity is contested
```

These are explicit records only.

The models do not calculate or infer these states.

---

## 5. Explicit Non-responsibilities

The initial models and builders must not:

```text
compare trajectories
calculate continuity score
map OperatorResponse to continuity
infer continuity from timestamps
infer continuity from record order
infer continuity from shared identity
infer continuity from matching values
select current or authoritative relation
resolve conflicting relations
merge branches
close gaps
repair continuity
select next action
persist records
modify POST /loop/step
modify SQLite schema
```

---

## 6. Relationship to Existing vNext Records

Continuity Readability may reference existing records, but must not own or redefine them.

Possible references include:

```text
StabilityScene
ReadabilityContext
IncorporationRecord
SceneReadabilityRelation
DifferenceObject
BoundaryEvaluation
SemanticRealizationBundle
ReadabilityRelationBundle
```

No one record type is mandatory in the first model.

The first PoC should therefore use generic source and target references rather than embedding or tightly coupling to one existing model.

---

## 7. Relationship to Trajectory

Continuity Readability is not yet Trajectory.

```text
ContinuityRelationRecord
= one explicit readable relation statement

Trajectory
= relation graph with trace candidates, selection, branch, merge, gap, revision, and graph-level structure
```

The initial Continuity Readability model may later become input material for Trajectory construction, but it must not be presented as a complete trajectory edge model yet.

---

## 8. Relationship to Existing Runtime Continuity

The current Runtime already contains continuity behavior primarily associated with OperatorResponse mapping.

The new design must remain isolated from that behavior.

```text
current RuntimeContinuityResult
≠ ContinuityReadabilityContext
≠ ContinuityRelationRecord
```

No compatibility projection should be added during the first model implementation.

---

## 9. Recommended First Implementation

```text
explicit continuity readability inputs
→ ContinuityReadabilityContextBuilder
→ ContinuityReadabilityContext

existing ContinuityReadabilityContext
+
explicit relation statement
→ ContinuityRelationRecordBuilder
→ ContinuityRelationRecord
```

The builders should be pure and perform only:

```text
scope preservation
reference preservation
expected-reference validation
explicit flag preservation
deep copy
ID generation
```

---

## 10. Required Validation Boundary

The first builder implementation should verify:

```text
source_slice_ref and target_slice_ref are explicitly present
source_ref and target_ref are distinct unless explicitly allowed later
relation context reference matches the supplied ContinuityReadabilityContext
process scope is preserved
```

The first version should reject identical source and target references to avoid silently treating self-reference as continuity.

A later review may add an explicit self-relation type if needed.

---

## 11. Current Decision

```text
Continuity Readability model design
= COMPLETE

Recommended minimal models
= ContinuityReadabilityContext + ContinuityRelationRecord

Recommended minimal builders
= ContinuityReadabilityContextBuilder + ContinuityRelationRecordBuilder

Compatibility projection to current RuntimeContinuityResult
= DEFERRED

Trajectory integration
= DEFERRED

Critical design blocker
= NONE IDENTIFIED
```

---

## 12. Next Step

Proceed with the isolated model and pure builder implementation:

```text
Next
→ ContinuityReadabilityContext
+
ContinuityRelationRecord
```

Do not add an assembly service, bundle, Runtime projection, persistence, or Trajectory integration in the first implementation step.
