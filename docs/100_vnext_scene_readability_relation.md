# 100. vNext SceneReadabilityRelation

---

## 1. Purpose

This document records the next isolated implementation step for Incorporated Readability:

```text
StabilityScene
+
ReadabilityContext
→ SceneReadabilityRelationBuilder
→ SceneReadabilityRelation
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

`SceneReadabilityRelation` is an implementation-level reference record. It is not a new Core stage and does not redefine Stability, Context, or Incorporated Readability.

---

## 2. Added Model

Updated:

```text
app/vnext/models.py
```

Added:

```text
SceneReadabilityRelation
```

Fields:

```text
scene_readability_relation_id
process_id
slice_ref
stability_scene_ref
readability_context_ref
relation_type
provisional
authoritative
source_refs[]
evidence_refs[]
created_at
metadata
```

The model stores references only. It does not embed a complete `StabilityScene` or `ReadabilityContext`.

---

## 3. Relation Meaning

The relation states only that one explicit Stability Scene is related to one explicit readability context under a caller-supplied relation type.

It does not imply:

```text
StabilityScene owns ReadabilityContext
ReadabilityContext generated StabilityScene
StabilityScene snapshots ReadabilityContext
ReadabilityContext is mandatory for every StabilityScene
ReadabilityContext changes automatically update StabilityScene
StabilityScene changes automatically update ReadabilityContext
```

This preserves:

```text
StabilityScene
≠ ReadabilityContext
≠ IncorporationRecord
≠ SceneReadabilityRelation
```

---

## 4. Added Builder

Updated:

```text
app/vnext/builders.py
```

Added:

```text
SceneReadabilityRelationBuilder
```

The builder performs only:

```text
reference one StabilityScene
reference one ReadabilityContext
verify common process_id
verify common slice_ref
validate optional expected references
preserve explicit relation_type
preserve explicit provisional flag
preserve explicit authoritative flag
copy source/evidence refs
copy nested metadata
create an ID when not supplied
```

---

## 5. Authoritative Boundary

`authoritative` is an explicit input only.

The builder does not infer authority from:

```text
creation time
list order
latest context
non-provisional state
relation type
source count
evidence count
```

Therefore:

```text
authoritative = true
```

means only that the caller explicitly supplied that value.

It does not establish canonical ownership or repository selection semantics.

---

## 6. Explicit Non-responsibilities

The model and builder do not:

```text
derive ReadabilityContext from StabilityScene
derive StabilityScene from ReadabilityContext
calculate readability
select a current context
select an authoritative relation
update context
update scene
create IncorporationRecord
infer incorporated items
merge contexts
resolve conflicts
execute rollback
persist records
modify SemanticAssemblyService
modify /loop/step
modify SQLite schema
```

The relation does not replace `IncorporationRecord`.

```text
IncorporationRecord
= explicit context update

SceneReadabilityRelation
= explicit scene/context association
```

---

## 7. Consistency Rules

The builder requires:

```text
StabilityScene.process_id
=
ReadabilityContext.process_id
```

and:

```text
StabilityScene.slice_ref
=
ReadabilityContext.slice_ref
```

Optional expected references are validated against:

```text
scene.stability_scene_id
readability_context.readability_context_id
```

The builder does not query a repository or resolve an external latest context.

---

## 8. Test Coverage

Added:

```text
tests/vnext/test_scene_readability_relation.py
```

The tests verify:

```text
relation stores references instead of complete objects
authoritative remains false unless explicitly supplied
explicit authoritative/provisional flags are preserved
process mismatch is rejected
slice mismatch is rejected
expected scene/context refs are validated
source/evidence refs and nested metadata are copied
```

The Priority F workflow now runs this test with the accepted Priority G/H regression suite and all earlier vNext tests.

---

## 9. Isolation Boundary

The new model remains isolated from:

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

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

SceneReadabilityRelation added to Core
= NO

ReadabilityContext embedded into StabilityScene
= NO

Context update confused with scene/context relation
= NO

Authority inferred automatically
= NO

Automatic context synchronization introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 11. Current Decision

```text
SceneReadabilityRelation
= IMPLEMENTED AS ISOLATED REFERENCE MODEL

SceneReadabilityRelationBuilder
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

## 12. Next Decision

After workflow verification, review whether Incorporated Readability should next add:

```text
ReadabilityRelationBundle
```

to group:

```text
ReadabilityContext refs
IncorporationRecord refs
SceneReadabilityRelation refs
```

without adding persistence or automatic context selection.

Do not connect Incorporated Readability to `SemanticAssemblyService`, `/loop/step`, or SQLite until that review is complete.
