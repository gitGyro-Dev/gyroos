# 101. vNext Readability Relation Bundle Review

---

## 1. Purpose

This document reviews whether the verified Incorporated Readability records should be grouped by reference:

```text
ReadabilityContext
+
IncorporationRecord
+
SceneReadabilityRelation
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

This review does not add a new Runtime model or connect Incorporated Readability to the current Runtime.

---

## 2. Reviewed Records

### ReadabilityContext

```text
explicit readability state at one runtime point
```

### IncorporationRecord

```text
explicit before/after readability-context update record
```

### SceneReadabilityRelation

```text
explicit reference relation between StabilityScene and ReadabilityContext
```

These records have distinct responsibilities and must remain separate.

---

## 3. Review Question

The question is whether to add a reference-only grouping record:

```text
ReadabilityRelationBundle
```

that may store:

```text
readability_context_refs[]
incorporation_record_refs[]
scene_readability_relation_refs[]
```

within one explicit process and slice scope.

---

## 4. Findings

A grouping record is useful for:

```text
returning one in-memory Incorporated Readability result
checking shared process/slice scope
checking that IncorporationRecord context refs are included
checking that SceneReadabilityRelation context refs are included
keeping complete records separate from grouping metadata
supporting later orchestration without adding persistence
```

The grouping record is not required by the Gyro Logic Core.

It is an implementation convenience only.

---

## 5. Required Boundary

A future `ReadabilityRelationBundle` must remain reference-only.

It must not embed complete:

```text
ReadabilityContext
IncorporationRecord
SceneReadabilityRelation
StabilityScene
```

It may only store identifiers and explicit scope metadata.

---

## 6. Required Consistency Checks

A future pure builder should verify:

```text
all ReadabilityContext records share one process_id and slice_ref
all IncorporationRecord records share that process_id and slice_ref
all SceneReadabilityRelation records share that process_id and slice_ref
```

It should also verify:

```text
IncorporationRecord.before_context_ref
→ included ReadabilityContext

IncorporationRecord.after_context_ref
→ included ReadabilityContext

SceneReadabilityRelation.readability_context_ref
→ included ReadabilityContext
```

The StabilityScene referenced by `SceneReadabilityRelation` does not need to be embedded in the bundle.

---

## 7. Explicit Non-selection Boundary

The bundle must not select:

```text
current ReadabilityContext
latest ReadabilityContext
authoritative ReadabilityContext
preferred IncorporationRecord
authoritative SceneReadabilityRelation
```

It must not infer selection from:

```text
creation time
list order
provisional flag
authoritative flag
source count
evidence count
context graph position
```

An `authoritative=true` relation remains only an explicit property of that relation.

---

## 8. Explicit Non-responsibilities

A future bundle and builder must not:

```text
learn from history
update readability context
execute IncorporationRecord
calculate before/after differences
merge contexts
resolve conflicts
detect poisoning
apply expiry
execute rollback
select a current context
select an authoritative relation
persist records
register canonical record types
modify SemanticAssemblyService
modify POST /loop/step
modify SQLite schema
```

---

## 9. Relation to SemanticRealizationBundle

A future `ReadabilityRelationBundle` must remain separate from:

```text
SemanticRealizationBundle
```

The two bundles have different grouping responsibilities:

```text
SemanticRealizationBundle
= StabilityScene / Observation / Difference / Boundary references

ReadabilityRelationBundle
= ReadabilityContext / IncorporationRecord / SceneReadabilityRelation references
```

They must not be merged at this stage.

---

## 10. Review Decision

```text
ReadabilityRelationBundle
= RECOMMENDED AS NEXT ISOLATED REFERENCE MODEL

ReadabilityRelationBundleBuilder
= RECOMMENDED AS NEXT ISOLATED PURE BUILDER

Automatic current-context selection
= REJECTED

Integration with SemanticAssemblyService
= DEFERRED

Integration with POST /loop/step
= DEFERRED

SQLite persistence
= DEFERRED
```

---

## 11. Next Minimal Implementation

```text
ReadabilityContext[]
+
IncorporationRecord[]
+
SceneReadabilityRelation[]
→ ReadabilityRelationBundleBuilder
→ ReadabilityRelationBundle
```

The implementation should remain in-memory, reference-only, and isolated from the current accepted Runtime.

---

## 12. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Incorporated Readability added to Core
= NO

Current context selected automatically
= NO

Scene and Context ownership introduced
= NO

History storage treated as incorporation
= NO

Current RC Runtime contract changed
= NO
```

---

## 13. Current Decision

```text
SceneReadabilityRelation
= VERIFIED

Incorporated Readability relation review
= COMPLETE

Critical design blocker
= NONE IDENTIFIED

Next
→ ReadabilityRelationBundle
```
