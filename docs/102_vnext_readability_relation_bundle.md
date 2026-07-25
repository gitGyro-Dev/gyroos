# 102. vNext ReadabilityRelationBundle

---

## 1. Purpose

This document records the next isolated implementation step for Incorporated Readability:

```text
ReadabilityContext[]
+
IncorporationRecord[]
+
SceneReadabilityRelation[]
→ ReadabilityRelationBundleBuilder
→ ReadabilityRelationBundle
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

`ReadabilityRelationBundle` is an implementation-level reference grouping record. It is not a new Core stage, canonical memory, current-context selector, or persistence transaction.

---

## 2. Added Model

Updated:

```text
app/vnext/models.py
```

Added:

```text
ReadabilityRelationBundle
```

Fields:

```text
readability_relation_bundle_id
process_id
slice_ref
readability_context_refs[]
incorporation_record_refs[]
scene_readability_relation_refs[]
created_at
metadata
```

The model stores references only. It does not embed complete readability records.

---

## 3. Added Builder

Updated:

```text
app/vnext/builders.py
```

Added:

```text
ReadabilityRelationBundleBuilder
```

The builder performs only:

```text
accept one explicit process/slice scope
verify all ReadabilityContext records match that scope
verify all IncorporationRecord records match that scope
verify all SceneReadabilityRelation records match that scope
verify IncorporationRecord before/after refs point to bundled contexts
verify SceneReadabilityRelation context refs point to bundled contexts
copy record identifiers into reference lists
copy nested metadata
create a bundle ID when not supplied
```

Optional record groups may remain empty.

---

## 4. Reference Integrity

For each `IncorporationRecord`:

```text
before_context_ref
→ bundled ReadabilityContext

after_context_ref
→ bundled ReadabilityContext
```

For each `SceneReadabilityRelation`:

```text
readability_context_ref
→ bundled ReadabilityContext
```

The builder does not require the referenced StabilityScene itself to be embedded in this bundle. Scene ownership remains outside the Incorporated Readability grouping boundary.

---

## 5. Explicit Non-responsibilities

The model and builder do not:

```text
select a current ReadabilityContext
select a latest ReadabilityContext
select an authoritative ReadabilityContext
select an authoritative SceneReadabilityRelation
order contexts by time
interpret list order as precedence
execute context updates
merge contexts
resolve conflicts
execute rollback
persist records
create an atomic publication group
modify SemanticAssemblyService
modify /loop/step
modify SQLite schema
```

The bundle does not infer selection from:

```text
created_at
list order
provisional
reversible
authoritative
relation_type
```

---

## 6. Separation from SemanticRealizationBundle

```text
SemanticRealizationBundle
= Stability Scene / Observation / Difference / Boundary reference grouping

ReadabilityRelationBundle
= Readability Context / Incorporation / Scene-Context relation reference grouping
```

The two bundles remain separate.

This implementation does not define a unified canonical Runtime result.

---

## 7. Test Coverage

Added:

```text
tests/vnext/test_readability_relation_bundle.py
```

The tests verify:

```text
bundle stores references rather than complete records
optional record groups may remain empty
ReadabilityContext scope mismatch is rejected
IncorporationRecord requires both referenced contexts in the bundle
SceneReadabilityRelation requires its context in the bundle
no current or authoritative record is selected
nested metadata is copied
```

The Priority F workflow now runs this test with the accepted Priority G/H regression suite and all earlier vNext tests.

---

## 8. Isolation Boundary

The bundle remains isolated from:

```text
SemanticAssemblyService
SemanticRealizationBundle
POST /loop/step
current ProcessExecutor
current StabilityEngine
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API models
OperatorResponse selection
Trajectory publication
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 9. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

ReadabilityRelationBundle added to Core
= NO

Current context selected automatically
= NO

Authoritative relation selected automatically
= NO

History storage treated as Incorporated Readability
= NO

Automatic learning introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 10. Current Decision

```text
ReadabilityRelationBundle
= IMPLEMENTED AS ISOLATED REFERENCE MODEL

ReadabilityRelationBundleBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

SemanticAssemblyService
= UNCHANGED

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```

---

## 11. Next Decision

After workflow verification, review whether the next minimal step should be:

```text
A. Incorporated Readability Assembly Service
```

that coordinates explicit context, incorporation, relation, and bundle builders without selection or persistence;

or:

```text
B. Continuity Readability model design
```

Do not connect either bundle to `/loop/step` or SQLite until that review is complete.
