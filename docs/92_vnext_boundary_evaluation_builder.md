# 92. vNext BoundaryEvaluation Builder

---

## 1. Purpose

This document records the fourth isolated vNext implementation step after the verified Stability Scene and Stability Observation builders.

The implemented scope is intentionally limited to:

```text
existing DifferenceObject
+
explicit Boundary evaluation values
→ BoundaryEvaluation
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The builder is an implementation utility. It is not a new Core stage and does not define Difference or Boundary.

---

## 2. Added Component

Updated:

```text
app/vnext/builders.py
```

Added component:

```text
BoundaryEvaluationBuilder
```

Primary operation:

```text
build(...)
→ BoundaryEvaluation
```

---

## 3. Explicit Input Contract

The builder accepts:

```text
DifferenceObject
BoundaryReadabilityState
readable_as_distinction
usable_distinction
provisional
optional orientation_ref
optional context_refs
optional policy_ref
evidence_refs
metadata
optional boundary_evaluation_id
optional expected_difference_ref
```

The evaluation values are explicit caller-supplied outputs.

The builder does not derive them from the Difference representation.

---

## 4. Builder Responsibility

The builder performs only:

```text
reference one existing DifferenceObject
copy process_id and slice_ref from DifferenceObject
validate optional expected Difference reference
preserve explicit evaluation values
use Difference orientation/context refs as defaults when no override is supplied
copy evidence, context refs, and nested metadata
create one BoundaryEvaluation ID when not supplied
construct one BoundaryEvaluation
```

The resulting evaluation stores:

```text
difference_ref
```

This preserves:

```text
DifferenceObject
≠ BoundaryEvaluation
≠ Boundary
```

---

## 5. Explicit Non-responsibilities

The builder does not:

```text
inspect Difference representation
calculate distance
calculate error
compare Difference values
apply a universal metric
apply a threshold
infer readability
infer usability
select a Boundary policy
run a learned classifier
create BoundaryEvidence
create BoundaryStateRecord
modify DifferenceObject
persist records
modify /loop/step
```

A `CANDIDATE` evaluation may explicitly remain unreadable and unusable.

---

## 6. Reference and Consistency Boundary

When `expected_difference_ref` is supplied, it must equal:

```text
difference.difference_id
```

A mismatch is rejected.

The existing `BoundaryEvaluation` model remains responsible for internal consistency rules, including:

```text
usable_distinction = true
→ readable_as_distinction = true

readability_state = USABLE_BOUNDARY
→ usable_distinction = true
```

The builder does not bypass or duplicate these model validations.

---

## 7. Orientation and Context Boundary

By default:

```text
orientation_ref
→ inherited from DifferenceObject

context_refs
→ copied from DifferenceObject
```

A caller may explicitly provide evaluation-specific orientation and context references.

This does not mutate the referenced DifferenceObject.

---

## 8. Copy Boundary

Caller-owned:

```text
context_refs
evidence_refs
metadata
```

are copied into the evaluation, including nested metadata structures.

Later caller mutation does not change the created evaluation.

---

## 9. Test Coverage

Added:

```text
tests/vnext/test_boundary_evaluation_builder.py
```

The tests verify:

```text
BoundaryEvaluation explicitly references DifferenceObject
process and slice references are preserved from DifferenceObject
explicit readability and usability values are preserved
Difference representation does not cause implicit Boundary inference
orientation and context defaults are inherited explicitly
caller may override orientation and context refs
expected Difference reference mismatch is rejected
BoundaryEvaluation model consistency validation remains active
mutable context, evidence, and nested metadata inputs are copied
```

The existing workflow executes this test with the accepted G/H regression suite and earlier vNext tests.

Successful verification evidence:

```text
Run ID: 30148514733
Job: test-and-run-poc
Conclusion: success
```

---

## 10. Isolation Boundary

The builder remains isolated from:

```text
POST /loop/step
current SliceEngine
current BoundaryEvidence generation
current BoundaryStateRecord generation
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API response models
OperatorResponse selection
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 11. Next Decision

The original three-concept first step now has isolated typed models and pure builders for:

```text
StabilityScene
StabilityObservation
DifferenceObject
BoundaryEvaluation
```

The next decision should remain small.

Selected next step:

```text
Add an isolated vNext realization bundle that groups existing objects by reference without evaluation.
```

Do not connect these components to `/loop/step` or SQLite until the isolated model/builder responsibility review is complete.

---

## 12. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Difference reduced to numeric distance
= NO

Difference treated as Error
= NO

Boundary reduced to threshold
= NO

Builder treated as Boundary decision engine
= NO

GyroAuth-specific policy introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 13. Current Decision

```text
BoundaryEvaluationBuilder
= VERIFIED AS ISOLATED PURE BUILDER

StabilityObservationBuilder
= VERIFIED AS ISOLATED PURE BUILDER

StabilitySceneBuilder
= VERIFIED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= COMPLETE
```
