# 98. vNext Incorporated Readability Minimal PoC

---

## 1. Purpose

This document records the first isolated implementation step for:

```text
Incorporated Readability
```

The implemented scope is intentionally limited to:

```text
ReadabilityContext
+
IncorporationRecord
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Incorporated Readability is not added to the Core. It is represented as an implementation-level readability update record around the Core.

---

## 2. Added Models

Updated:

```text
app/vnext/models.py
```

Added:

```text
ReadabilityContext
IncorporationRecord
```

### ReadabilityContext

A `ReadabilityContext` records which references are explicitly available as readable, unresolved, or excluded at one runtime point.

Fields:

```text
readability_context_id
process_id
slice_ref
readable_item_refs[]
unresolved_item_refs[]
excluded_item_refs[]
source_context_refs[]
provisional
created_at
metadata
```

It is not:

```text
raw history storage
complete Context
model training state
learned parameter set
canonical memory
```

### IncorporationRecord

An `IncorporationRecord` references two distinct readability contexts and records an explicit update decision.

Fields:

```text
incorporation_record_id
process_id
slice_ref
before_context_ref
after_context_ref
incorporated_item_refs[]
rejected_item_refs[]
update_reason
provisional
reversible
evidence_refs[]
created_at
metadata
```

It preserves:

```text
history storage
≠ incorporated readability
```

The record states that a readability-context update was explicitly represented. It does not infer that update from stored events.

---

## 3. Added Builders

Updated:

```text
app/vnext/builders.py
```

Added:

```text
ReadabilityContextBuilder
IncorporationRecordBuilder
```

### ReadabilityContextBuilder

The builder performs only:

```text
preserve explicit process and slice scope
copy readable/unresolved/excluded refs
copy source context refs
copy provisional flag
copy nested metadata
create an ID when not supplied
```

It does not derive readability from a StabilityScene, DifferenceObject, BoundaryEvaluation, history record, or policy.

### IncorporationRecordBuilder

The builder performs only:

```text
reference one explicit before context
reference one explicit after context
verify common process and slice scope
verify before and after context IDs are distinct
validate optional expected context references
copy incorporated and rejected item refs
copy update reason and flags
copy evidence and nested metadata
create an ID when not supplied
```

The builder does not calculate the difference between the before and after contexts.

---

## 4. Consistency Rules

The following rules are enforced:

```text
before.process_id = after.process_id
before.slice_ref = after.slice_ref
before.context_id ≠ after.context_id
```

An item cannot be present in both:

```text
incorporated_item_refs[]
rejected_item_refs[]
```

The model does not require either list to be non-empty.

This permits an explicit record stating that no incorporation or rejection decision was supplied.

---

## 5. Explicit Non-responsibilities

The models and builders do not:

```text
learn from history
automatically update context
infer incorporated items from context differences
resolve conflicts
rank candidate items
detect poisoning
apply expiry
execute rollback
merge contexts
select authoritative context
persist records
modify /loop/step
modify SQLite schema
```

The `reversible` flag records an explicit property. It does not implement rollback behavior.

---

## 6. Test Coverage

Added:

```text
tests/vnext/test_incorporated_readability.py
```

The tests verify:

```text
ReadabilityContext stores explicit current readability only
history/events/learned-state fields are not introduced
IncorporationRecord references distinct before and after contexts
explicit incorporated and rejected refs are preserved
context differences do not cause implicit incorporation inference
the same item cannot be incorporated and rejected
before and after process/slice scope must match
optional expected context refs are validated
mutable inputs and nested metadata are copied
```

The existing Priority F workflow executes this test with the accepted Priority G/H regression suite and all earlier vNext tests.

Verification evidence:

```text
GitHub Actions run 30150037704 = success
GitHub Actions run 30150071531 = success
GitHub Actions run 30150092777 = success
GitHub Actions run 30150114429 = success
```

---

## 7. Isolation Boundary

The new models remain isolated from:

```text
SemanticAssemblyService
SemanticRealizationBundle
POST /loop/step
current ProcessExecutor
current StabilityEngine
current BoundaryEvidence generation
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

Incorporated Readability added to Core
= NO

History storage treated as incorporation
= NO

Automatic learning introduced
= NO

Rollback execution introduced
= NO

GyroAuth-specific policy introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 9. Current Decision

```text
ReadabilityContext
= VERIFIED AS ISOLATED MODEL

IncorporationRecord
= VERIFIED AS ISOLATED UPDATE RECORD

ReadabilityContextBuilder
= VERIFIED AS ISOLATED PURE BUILDER

IncorporationRecordBuilder
= VERIFIED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= COMPLETE
```

---

## 10. Next Decision

The next step is a responsibility review before connecting Incorporated Readability to semantic assembly.

Recommended review:

```text
ReadabilityContext
+
IncorporationRecord
+
StabilityScene
```

The review should determine whether the next minimal relation is:

```text
StabilityScene references current ReadabilityContext
```

or:

```text
IncorporationRecord remains a separate adjacent record
```

No automatic context update service should be introduced before that review.
