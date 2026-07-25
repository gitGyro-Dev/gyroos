# 91. vNext StabilityObservation Builder

---

## 1. Purpose

This document records the third isolated vNext implementation step after the verified `StabilitySceneBuilder`.

The implemented scope is intentionally limited to:

```text
existing StabilityScene
+
explicit observation values
→ StabilityObservation
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

A `StabilityObservation` is an implementation-level observation of a scene. It is not Stability itself and does not replace the scene.

---

## 2. Added Component

Updated:

```text
app/vnext/builders.py
```

Added component:

```text
StabilityObservationBuilder
```

Primary operation:

```text
build(...)
→ StabilityObservation
```

---

## 3. Explicit Input Contract

The builder accepts:

```text
StabilityScene
optional score
optional classification
optional confidence
optional policy_ref
explicit evidence_refs
metadata
optional observation ID
optional expected scene reference
```

The score, classification, and confidence are all optional.

This preserves:

```text
StabilityScene
≠ StabilityObservation
≠ score
≠ classification
```

---

## 4. Builder Responsibility

The builder performs only:

```text
reference one existing StabilityScene
validate an optional expected scene reference
copy explicit observation values
copy evidence and metadata
create one StabilityObservation ID when not supplied
```

The resulting observation stores:

```text
stability_scene_ref
```

It does not embed or duplicate the complete scene.

---

## 5. Explicit Non-responsibilities

The builder does not:

```text
inspect scene content to infer a score
inspect articulation representation for a stability value
assign a classification
calculate confidence
evaluate readable relations
resolve unresolved local items
evaluate continuation conditions
replace or mutate StabilityScene
select OperatorResponse
create RuntimeContinuityResult
persist records
modify /loop/step
```

An observation with no score or classification is valid.

---

## 6. Reference Boundary

When `expected_scene_ref` is supplied, it must equal:

```text
scene.stability_scene_id
```

A mismatch is rejected.

This provides an explicit caller-side reference assertion without introducing repository lookup or canonical identity semantics.

---

## 7. Copy Boundary

Caller-owned:

```text
evidence_refs
metadata
```

are copied into the observation.

Later caller mutation does not change the created observation.

---

## 8. Test Coverage

Added:

```text
tests/vnext/test_stability_observation_builder.py
```

The tests verify:

```text
observation references but does not replace the scene
explicit score, classification, confidence, and policy are preserved
score and classification are optional
scene content does not cause implicit observation inference
expected scene reference mismatch is rejected
mutable evidence and metadata inputs are copied
```

The existing workflow now executes this test with the accepted G/H regression suite and earlier vNext tests.

---

## 9. Isolation Boundary

The builder remains isolated from:

```text
POST /loop/step
current StabilityEngine
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API response models
OperatorResponse selection
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 10. Next Decision

After workflow verification, the next small step should return to the third original concept:

```text
DifferenceObject
→ pure BoundaryEvaluation builder/interface
```

That component should consume an existing `DifferenceObject` and explicit evaluation output.

It must not introduce a universal threshold, comparison algorithm, or learned decision rule.

Do not connect it to `/loop/step` yet.

---

## 11. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Stability reduced to score
= NO

Observation treated as Stability itself
= NO

Scene content used for implicit classification
= NO

GyroAuth-specific policy introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 12. Current Decision

```text
StabilityObservationBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

StabilitySceneBuilder
= VERIFIED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```
