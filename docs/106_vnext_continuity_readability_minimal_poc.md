# 106. vNext Continuity Readability Minimal PoC

---

## 1. Purpose

This document records the first isolated implementation step for:

```text
Continuity Readability
```

The implemented scope is intentionally limited to:

```text
ContinuityReadabilityContext
+
ContinuityRelationRecord
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Continuity Readability is not added to the Core. It is represented as an implementation-level readability statement across explicit source and target references.

---

## 2. Added Models

Updated:

```text
app/vnext/models.py
```

Added:

```text
ContinuityReadabilityContext
ContinuityRelationRecord
```

### ContinuityReadabilityContext

Fields:

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

It records one explicit scope in which a relation across two slice references may be read.

It does not assert that continuity exists.

### ContinuityRelationRecord

Fields:

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

It records one explicit continuity-readability statement under one explicit context.

---

## 3. Added Builders

Updated:

```text
app/vnext/builders.py
```

Added:

```text
ContinuityReadabilityContextBuilder
ContinuityRelationRecordBuilder
```

The builders preserve explicit caller-supplied values and deep-copy mutable inputs.

The relation builder validates optional expected context and process references.

---

## 4. Semantic Separation

The implementation preserves:

```text
Continuity Readability
≠ history storage
≠ RuntimeContinuityResult
≠ OperatorResponse mapping
≠ Identity continuity
≠ Trajectory
≠ Incorporated Readability
```

It also preserves:

```text
continuity readability
≠ continuity success
≠ continuity guarantee
≠ continuation decision
```

and:

```text
Identity break
≠ continuity break
```

A `ContinuityRelationRecord` is not treated as a Trajectory edge.

---

## 5. Explicit Non-responsibilities

The models and builders do not:

```text
calculate a continuity score
compare trajectories
infer continuity from timestamps
infer continuity from record order
infer continuity from Identity equality
map OperatorResponse to continuity
select a continuation action
select a current relation
select an authoritative relation
resolve conflicts
merge branches
repair gaps
build a Trajectory graph
persist records
modify /loop/step
modify SQLite schema
```

`relation_type`, `continuity_state`, `readable`, `provisional`, and `authoritative` are explicit caller-supplied values only.

---

## 6. Test Coverage

Added:

```text
tests/vnext/test_continuity_readability.py
```

The tests verify:

```text
explicit source/target scope is preserved
no score, OperatorResponse, Identity, or Trajectory fields are introduced
explicit relation statements are preserved
continuity state and authority are not inferred
expected context reference is validated
expected process reference is validated
mutable inputs and nested metadata are copied
```

The Priority F workflow now executes this test together with the accepted Priority G/H regression suite and all earlier vNext tests.

---

## 7. Isolation Boundary

The new models remain isolated from:

```text
SemanticAssemblyService
IncorporatedReadabilityAssemblyService
SemanticRealizationBundle
ReadabilityRelationBundle
POST /loop/step
current ProcessExecutor
current RuntimeContinuityResult
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API models
OperatorResponse selection
Trajectory publication
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 8. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Continuity Readability added to Core
= NO

Continuity reduced to a score
= NO

OperatorResponse mapped automatically
= NO

Identity continuity inferred
= NO

Trajectory edge introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 9. Current Decision

```text
ContinuityReadabilityContext
= IMPLEMENTED AS ISOLATED MODEL

ContinuityRelationRecord
= IMPLEMENTED AS ISOLATED RELATION RECORD

ContinuityReadabilityContextBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

ContinuityRelationRecordBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```

---

## 10. Next Decision

After workflow verification, review whether the next minimal step should be:

```text
ContinuityRelationBundle
```

to group continuity context and relation references without selecting a current or authoritative relation;

or:

```text
Continuity Readability Assembly Service
```

to coordinate explicit context and relation construction without scoring, response mapping, persistence, or Trajectory generation.

Do not connect Continuity Readability to `/loop/step` or SQLite before that review is complete.
