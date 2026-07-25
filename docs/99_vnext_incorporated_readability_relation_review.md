# 99. vNext Incorporated Readability Relation Review

---

## 1. Purpose

This review evaluates the responsibility relationship among:

```text
ReadabilityContext
IncorporationRecord
StabilityScene
```

The review is limited to the isolated vNext semantic PoC.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Incorporated Readability remains an implementation-level concept around the Core and is not added to the Core.

---

## 2. Reviewed Alternatives

### Alternative A

```text
StabilityScene directly contains or owns ReadabilityContext
```

### Alternative B

```text
StabilityScene and ReadabilityContext remain separate records
+
an adjacent relation record references both
```

### Alternative C

```text
IncorporationRecord alone implicitly establishes the active context for StabilityScene
```

---

## 3. Decision

```text
Alternative B
= ACCEPTED
```

The next minimal relation should be represented by a separate reference-only record.

Recommended name:

```text
SceneReadabilityRelation
```

Provisional relation:

```text
StabilityScene
← SceneReadabilityRelation →
ReadabilityContext
```

`IncorporationRecord` remains a separate adjacent update record.

---

## 4. Why Direct Embedding Is Rejected

Directly adding `ReadabilityContext` to `StabilityScene` would create several ambiguities:

```text
scene owns context
scene snapshots context
scene derives context
scene requires context
scene mutates when context changes
```

None of these semantics has been established.

A StabilityScene may remain valid even when:

```text
no ReadabilityContext is supplied
multiple context readings exist
context authority is unresolved
context update occurred after scene construction
```

Therefore:

```text
StabilityScene
≠ ReadabilityContext
```

and:

```text
StabilityScene existence
≠ Incorporated Readability existence
```

---

## 5. Why IncorporationRecord Alone Is Insufficient

`IncorporationRecord` represents an explicit update between two readability contexts.

It does not state which context was used when reading a particular StabilityScene.

```text
IncorporationRecord
= context update record

SceneReadabilityRelation
= scene/context reference relation
```

These responsibilities must remain separate.

A context may be related to a scene without an incorporation update occurring in the same operation.

An incorporation update may also exist without any StabilityScene relation being asserted.

---

## 6. Recommended Minimal Relation Record

The next isolated model should contain only explicit references and relation properties.

Recommended fields:

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

Recommended initial `relation_type` value:

```text
CURRENT_READABILITY_CONTEXT
```

The model should permit future relation types without claiming them now.

The `authoritative` field records an explicit caller assertion only. It must not be inferred from recency or list order.

---

## 7. Required Consistency Rules

A builder should verify:

```text
scene.process_id = context.process_id
scene.slice_ref = context.slice_ref
```

It should also optionally validate expected scene and context references.

The builder should not:

```text
select the latest context
select an authoritative context
compare contexts
calculate incorporation
infer relation_type
modify StabilityScene
modify ReadabilityContext
```

---

## 8. Relationship to Semantic Assembly

No immediate change should be made to:

```text
SemanticAssemblyRequest
SemanticAssemblyService
SemanticAssemblyResult
SemanticRealizationBundle
```

The relation model should first be implemented and verified in isolation.

After verification, a separate review should decide whether semantic assembly may optionally accept:

```text
ReadabilityContext[]
SceneReadabilityRelation[]
IncorporationRecord[]
```

No default or automatically generated relation should be introduced.

---

## 9. Incorporated Readability Boundary

The reviewed structure is:

```text
ReadabilityContext
= explicit readability state record

IncorporationRecord
= explicit readability update record

SceneReadabilityRelation
= explicit scene/context relation record
```

This preserves:

```text
history storage
≠ ReadabilityContext
≠ IncorporationRecord

StabilityScene
≠ ReadabilityContext

context update
≠ scene/context relation
```

---

## 10. Explicit Non-goals

This review does not authorize:

```text
automatic context learning
latest-context selection
authority resolution
conflict resolution
poisoning detection
expiry processing
rollback execution
context merge
SQLite persistence
/loop/step integration
canonical record registration
```

---

## 11. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Incorporated Readability added to Core
= NO

StabilityScene made dependent on ReadabilityContext
= NO

IncorporationRecord treated as scene relation
= NO

History storage treated as incorporated readability
= NO

Current RC Runtime contract changed
= NO
```

---

## 12. Review Decision

```text
ReadabilityContext responsibility
= ACCEPTED

IncorporationRecord responsibility
= ACCEPTED

Direct embedding into StabilityScene
= REJECTED

Separate scene/context relation record
= RECOMMENDED

Critical design blocker
= NONE IDENTIFIED
```

Next minimal implementation:

```text
StabilityScene
+
ReadabilityContext
→ SceneReadabilityRelationBuilder
→ SceneReadabilityRelation
```

This next step must remain isolated from semantic assembly, `/loop/step`, and SQLite.
