# 95. vNext DifferenceObject Builder

---

## 1. Purpose

This document records the next isolated vNext implementation step after the completed initial semantic boundary review.

The implemented scope is intentionally limited to:

```text
explicit Difference representation
→ DifferenceObjectBuilder
→ DifferenceObject
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The builder is an implementation utility. It does not define Difference and is not a Difference extraction or comparison engine.

---

## 2. Added Component

Updated:

```text
app/vnext/builders.py
```

Added component:

```text
DifferenceObjectBuilder
```

Primary operation:

```text
build(...)
→ DifferenceObject
```

---

## 3. Explicit Input Contract

The builder accepts only explicit caller-supplied values:

```text
process_id
slice_ref
representation_type
representation
optional orientation_ref
optional context_refs
defined
comparable
evaluative
slice_relative
optional source_refs
metadata
optional difference_id
```

The representation may be:

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

The builder does not convert one representation type into another.

---

## 4. Builder Responsibility

The builder performs only:

```text
preserve explicit process and slice scope
preserve the supplied representation type
copy the supplied representation
copy orientation, context, and source references
preserve explicit defined/comparable/evaluative flags
copy nested metadata
create one Difference ID when not supplied
construct one DifferenceObject
```

The resulting object remains slice-relative by explicit field rather than by inferred behavior.

---

## 5. Explicit Non-responsibilities

The builder does not:

```text
extract Difference from Structure
extract Difference from LocalArticulation
compare two states
calculate distance
calculate error
normalize representation
convert a relation to a scalar
assign magnitude
assign ordering
infer comparability
infer evaluative meaning
evaluate Boundary readability
create BoundaryEvaluation
create BoundaryEvidence
create BoundaryStateRecord
select OperatorResponse
persist records
modify /loop/step
```

This preserves:

```text
Difference
≠ Distance
≠ Error
```

---

## 6. Defined / Undefined Boundary

The existing `DifferenceObject` model validation remains authoritative:

```text
defined = true
→ representation is required
```

An explicitly undefined Difference may contain:

```text
representation = null
```

The builder does not replace an undefined Difference with zero, an empty vector, UNKNOWN, VOID, or an error value.

---

## 7. Copy Boundary

Caller-owned mutable values are copied:

```text
representation
context_refs
source_refs
metadata
```

Nested representation and metadata structures are deep-copied.

Later mutation by the caller does not alter the created `DifferenceObject`.

---

## 8. Test Coverage

Added:

```text
tests/vnext/test_difference_object_builder.py
```

The tests verify:

```text
explicit non-numeric relational representation is preserved
process, slice, Orientation, Context, and source refs are preserved
undefined Difference may have no representation
defined Difference without representation is rejected by model validation
relation representation is not converted to a number
nested mutable inputs are copied
```

The existing workflow now executes this test with:

```text
Priority G regression tests
Priority H regression tests
earlier vNext semantic model and builder tests
```

---

## 9. Isolation Boundary

The builder remains isolated from:

```text
POST /loop/step
current SliceEngine
current SliceDone.deviation
current StabilityEngine
current BoundaryEvidence generation
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API models
OperatorResponse selection
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 10. Next Decision

After workflow verification, all initial isolated vNext record types will have explicit pure construction boundaries:

```text
StabilityScene
→ StabilitySceneBuilder

StabilityObservation
→ StabilityObservationBuilder

DifferenceObject
→ DifferenceObjectBuilder

BoundaryEvaluation
→ BoundaryEvaluationBuilder

SemanticRealizationBundle
→ SemanticRealizationBundleBuilder
```

The next step should remain small.

Recommended next action:

```text
review the full isolated construction pipeline
```

That review should decide whether to:

```text
add one pure orchestration facade for explicit inputs
```

or:

```text
begin Incorporated Readability model design
```

Do not connect vNext records to `/loop/step` or SQLite until that decision is complete.

---

## 11. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Difference reduced to numeric distance
= NO

Difference treated as Error
= NO

Builder treated as Difference extraction engine
= NO

Boundary evaluated by this builder
= NO

GyroAuth-specific policy introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 12. Current Decision

```text
DifferenceObjectBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

StabilitySceneBuilder
= VERIFIED

StabilityObservationBuilder
= VERIFIED

BoundaryEvaluationBuilder
= VERIFIED

SemanticRealizationBundleBuilder
= VERIFIED

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```
