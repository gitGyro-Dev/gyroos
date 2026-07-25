# 90. vNext StabilityScene Builder

---

## 1. Purpose

This document records the second isolated vNext implementation step after the verified semantic model PoC.

The implemented scope is intentionally limited to:

```text
explicit typed inputs
→ pure StabilityScene construction
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The builder is an implementation utility. It is not a new Core stage and does not define Stability.

---

## 2. Added Component

Added:

```text
app/vnext/builders.py
```

Primary component:

```text
StabilitySceneBuilder
```

Primary operation:

```text
build(...)
→ StabilityScene
```

---

## 3. Explicit Input Contract

The builder accepts only explicit typed inputs:

```text
process_id
slice_ref
LocalArticulation
ReadableRelation[]
UnresolvedLocalItem[]
ContinuationCondition[]
evidence_refs[]
metadata
optional stability_scene_id
```

The builder does not inspect current `/loop/step` payload dictionaries and does not infer data from existing Runtime records.

---

## 4. Builder Responsibility

The builder performs only:

```text
process and slice reference consistency checks
safe ID generation when an ID is not supplied
deep copying of typed input models
construction of one StabilityScene
```

The articulation must belong to the same:

```text
process_id
slice_ref
```

as the resulting scene.

---

## 5. Explicit Non-responsibilities

The builder does not:

```text
calculate Stability
produce a StabilityObservation
assign a score
assign a classification
infer readable relations
resolve unresolved items
evaluate continuation conditions
extract Difference
compare Difference
evaluate Boundary
create BoundaryEvidence
select OperatorResponse
build Continuity
build Trajectory
persist records
modify /loop/step
```

Missing lists remain empty. They are not inferred or synthesized.

---

## 6. Copy Boundary

Mutable input data is copied into the scene.

Later mutation of caller-owned:

```text
model metadata
list inputs
metadata dictionaries
```

does not mutate the constructed `StabilityScene`.

This keeps the builder output stable after construction without introducing persistence or canonical identity semantics.

---

## 7. Test Coverage

Added:

```text
tests/vnext/test_stability_scene_builder.py
```

The tests verify:

```text
explicit inputs are preserved
scene construction does not require score or classification
empty relation and condition lists remain explicit empty lists
articulation process mismatch is rejected
articulation slice mismatch is rejected
mutable caller inputs are copied
```

The existing workflow now executes the builder tests together with:

```text
Priority G regression tests
Priority H regression tests
vNext semantic model tests
```

---

## 8. Isolation Boundary

The builder remains isolated from:

```text
POST /loop/step
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public response models
OperatorResponse selection
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 9. Next Decision

After workflow verification, the next step should remain small.

Recommended next choice:

```text
Add a pure StabilityObservation builder/evaluator interface
```

That next component should accept an existing `StabilityScene` and explicit observation input or policy output.

It must not replace the scene or assume that a score is always available.

An alternative next step is a pure `BoundaryEvaluator` interface that consumes an existing `DifferenceObject` and explicit policy result.

Do not connect either component to `/loop/step` yet.

---

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Stability reduced to score
= NO

Builder treated as Core stage
= NO

Missing scene content inferred automatically
= NO

Difference or Boundary evaluated by this builder
= NO

GyroAuth requirements generalized into GyroOS
= NO

Current RC Runtime contract changed
= NO
```

---

## 11. Current Decision

```text
StabilitySceneBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```
