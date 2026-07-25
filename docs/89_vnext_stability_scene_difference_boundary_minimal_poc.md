# 89. vNext Minimal PoC — Stability Scene, DifferenceObject, and BoundaryEvaluation

---

## 1. Purpose

This document records the first isolated implementation step derived from the Gyro Logic v4.0 / Minimal Formal Model handoff.

The implemented scope is intentionally limited to:

```text
Stability Scene
+
DifferenceObject
+
BoundaryEvaluation
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

GyroOS implements runtime representations around the Core. It does not redefine the Gyro Logic definitions.

---

## 2. Isolation Boundary

The new models are placed under:

```text
app/vnext/
```

They are not yet connected to:

```text
POST /loop/step
current Priority G/H canonical records
SQLite persistence schema
repository reconstruction registry
public HTTP response models
OperatorResponse selection
```

Importing the vNext package does not change existing Runtime behavior.

This isolation preserves the accepted Priority G/H release-candidate contract while allowing semantic model experimentation.

---

## 3. Stability Scene

Added:

```text
StabilityScene
```

The model represents a runtime reading of the provisional theoretical form:

```text
K_n = (a_n, L_n, U_n, C_n+)
```

The implementation fields are:

```text
articulation
readable_relations
unresolved_local_items
continuation_conditions
```

Supporting models:

```text
LocalArticulation
ReadableRelation
UnresolvedLocalItem
ContinuationCondition
```

A `StabilityScene` does not contain a required scalar score.

This preserves:

```text
Stability Scene
≠ Stability score
≠ Stability classification
```

An optional, separate model is provided:

```text
StabilityObservation
```

It may contain:

```text
score
classification
confidence
policy_ref
```

The observation references a scene and does not replace it.

---

## 4. DifferenceObject

Added:

```text
DifferenceObject
```

The model does not assume that Difference is distance, error, or scalar magnitude.

Supported representation tags are:

```text
SCALAR
VECTOR
TUPLE
RELATION
CATEGORY
PARTIAL_ORDER
SYMBOLIC
DISTRIBUTION
FIELD
DOMAIN_DEFINED
```

The representation payload remains typed as an open value because the internal structure is domain-specific.

The model explicitly records:

```text
defined
comparable
evaluative
slice_relative
orientation_ref
context_refs
source_refs
```

This preserves:

```text
Difference
≠ Distance
≠ Error
```

A defined Difference must contain a representation.

No universal comparison, metric, ordering, or evaluation algorithm is introduced.

---

## 5. BoundaryEvaluation

Added:

```text
BoundaryEvaluation
```

The evaluation references one explicit `DifferenceObject` through:

```text
difference_ref
```

This establishes the implementation ordering:

```text
Difference exists
→ Difference may be evaluated as a readable distinction
→ readable distinction may be usable as Boundary
```

It preserves:

```text
Difference
≠ Boundary
```

The current readability states are observational implementation states:

```text
UNREADABLE
CANDIDATE
READABLE_DISTINCTION
USABLE_BOUNDARY
```

They are not new Gyro Logic Core stages.

Consistency constraints:

```text
usable_distinction = true
→ readable_as_distinction = true

readability_state = USABLE_BOUNDARY
→ usable_distinction = true
```

A BoundaryEvaluation may remain provisional.

No fixed threshold, universal rule, learned classifier, or domain decision algorithm is implemented.

---

## 6. Test Coverage

Added:

```text
tests/vnext/test_semantic_models.py
```

The tests verify:

```text
StabilityScene exists without a scalar score
StabilityObservation references but does not replace the scene
DifferenceObject supports non-numeric relational representation
defined Difference requires representation
BoundaryEvaluation references Difference separately
usable Boundary requires readable distinction
USABLE_BOUNDARY state requires usable distinction
```

The existing GitHub Actions workflow now runs this isolated vNext test file together with the accepted Priority G/H regression suite.

---

## 7. Implemented Files

Added:

```text
app/vnext/__init__.py
app/vnext/models.py
tests/vnext/test_semantic_models.py
docs/89_vnext_stability_scene_difference_boundary_minimal_poc.md
```

Updated:

```text
.github/workflows/priority-f-poc.yml
```

---

## 8. Explicit Non-goals

This first PoC does not implement:

```text
/loop/step adapter
/gyro/realize endpoint
StabilityScene construction engine
Stability evaluation policy
Difference extraction engine
Difference comparison algorithm
Boundary decision policy
BoundaryEvidence projection
SQLite persistence
canonical record registration
Incorporated Readability
Continuity Readability
Trajectory relation graph
GyroAuth-specific risk logic
```

These omissions are intentional.

---

## 9. Next Design Decision

After workflow verification, the next step should remain small.

Recommended next choice:

```text
A. Add a pure internal builder that constructs StabilityScene from explicit inputs

or

B. Add a pure internal BoundaryEvaluator interface that consumes DifferenceObject and explicit policy input
```

Do not connect the models to `/loop/step` until the internal responsibility boundary is reviewed.

---

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

GyroOS implementation states added to Core
= NO

Stability reduced to score
= NO

Difference reduced to numeric deviation
= NO

Boundary reduced to threshold
= NO

GyroAuth requirements generalized into GyroOS
= NO

Project Cycle responsibility mixed into Runtime
= NO

Developer Toolkit responsibility mixed into Runtime
= NO
```

---

## 11. Current Decision

```text
vNext Stability Scene model
= IMPLEMENTED AS ISOLATED POC

vNext DifferenceObject model
= IMPLEMENTED AS ISOLATED POC

vNext BoundaryEvaluation model
= IMPLEMENTED AS ISOLATED POC

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```
