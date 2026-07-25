# 103. vNext Incorporated Readability Assembly Service

---

## 1. Purpose

This document records the isolated orchestration step for Incorporated Readability:

```text
explicit readability inputs
→ IncorporatedReadabilityAssemblyRequest
→ IncorporatedReadabilityAssemblyService
→ IncorporatedReadabilityAssemblyResult
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

The service is an implementation facade. It is not a new Core stage, learning engine, current-context selector, continuity evaluator, canonical Runtime executor, or persistence transaction.

---

## 2. Added Components

Updated:

```text
app/vnext/models.py
```

Added input models:

```text
ReadabilityContextSpec
IncorporationSpec
SceneReadabilityRelationSpec
IncorporatedReadabilityAssemblyRequest
```

Added output model:

```text
IncorporatedReadabilityAssemblyResult
```

Added service:

```text
app/vnext/readability_assembly.py
IncorporatedReadabilityAssemblyService
```

Primary operation:

```text
assemble(request)
→ IncorporatedReadabilityAssemblyResult
```

---

## 3. Assembly Sequence

The service coordinates existing builders in this implementation order:

```text
ReadabilityContextBuilder[]
↓
IncorporationRecordBuilder[]
↓
SceneReadabilityRelationBuilder[]
↓
ReadabilityRelationBundleBuilder
```

This is an orchestration order only.

It does not define a theoretical establishment order, continuity order, learning order, canonical publication order, or precedence relation.

---

## 4. Scene Input Boundary

The service accepts one existing:

```text
StabilityScene
```

as an explicit input.

It does not reconstruct, modify, calculate, or replace that scene.

The request process and slice scope must match the supplied scene.

The result returns a deep copy of the scene so caller mutation does not alter the assembled result.

---

## 5. Request / Record Separation

The request contains explicit specification models:

```text
ReadabilityContextSpec
IncorporationSpec
SceneReadabilityRelationSpec
```

These are not constructed readability records.

The service uses them to create:

```text
ReadabilityContext
IncorporationRecord
SceneReadabilityRelation
```

This preserves:

```text
caller construction specification
≠
constructed runtime record
```

---

## 6. Service Responsibility

The service performs only:

```text
validate request scope against the supplied StabilityScene
construct zero or more explicit ReadabilityContext records
ensure ReadabilityContext IDs are unique within the request
resolve IncorporationSpec context refs within the same request
construct zero or more IncorporationRecord records
resolve SceneReadabilityRelationSpec context refs within the same request
construct zero or more SceneReadabilityRelation records
construct one reference-only ReadabilityRelationBundle
return all constructed records in memory
```

The service delegates copy behavior and record validation to the existing pure builders and models.

---

## 7. Reference Boundary

Each incorporation specification must reference contexts assembled in the same request:

```text
before_context_ref
→ one assembled ReadabilityContext

after_context_ref
→ one assembled ReadabilityContext
```

Each scene-relation specification must reference a context assembled in the same request:

```text
readability_context_ref
→ one assembled ReadabilityContext
```

A missing reference is rejected.

The service does not search a repository, resolve a latest context, import an external context, or infer a replacement context.

---

## 8. Explicit Non-responsibilities

The service does not:

```text
infer readable items
infer unresolved items
infer excluded items
learn from history
calculate context differences
infer incorporated or rejected items
execute context updates
select a current context
select a latest context
select an authoritative context
infer authoritative SceneReadabilityRelation
order contexts by time
interpret list order as precedence
merge contexts
resolve conflicts
detect poisoning
apply expiry
execute rollback
calculate continuity readability
select OperatorResponse
persist records
register canonical record types
modify SemanticAssemblyService
modify POST /loop/step
modify SQLite schema
```

The service assembles explicit records only.

---

## 9. Optional Records

A valid request may contain:

```text
zero ReadabilityContext specs
zero Incorporation specs
zero SceneReadabilityRelation specs
```

The resulting bundle remains valid and empty.

The service does not synthesize missing contexts, incorporations, or relations.

---

## 10. Test Coverage

Added:

```text
tests/vnext/test_incorporated_readability_assembly_service.py
```

The tests verify:

```text
explicit contexts, incorporations, scene relations, and bundle are assembled
optional record groups may remain empty
current or authoritative context is not inferred
references outside the same request are rejected
duplicate context IDs are rejected
scene and request scope mismatch is rejected
nested request inputs and the supplied scene are copied
```

The Priority F workflow now executes this test with:

```text
Priority G regression tests
Priority H regression tests
all earlier vNext semantic and readability tests
```

Verified workflow runs:

```text
30151364173 = success
30151382562 = success
```

---

## 11. Isolation Boundary

The service remains isolated from:

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

## 12. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Incorporated Readability added to Core
= NO

Assembly order treated as theoretical order
= NO

History storage treated as incorporation
= NO

Automatic learning introduced
= NO

Current context selected automatically
= NO

Continuity Readability calculated
= NO

Current RC Runtime contract changed
= NO
```

---

## 13. Current Decision

```text
ReadabilityRelationBundle
= VERIFIED AS ISOLATED REFERENCE MODEL

ReadabilityRelationBundleBuilder
= VERIFIED AS ISOLATED PURE BUILDER

IncorporatedReadabilityAssemblyRequest
= VERIFIED AS ISOLATED INPUT MODEL

IncorporatedReadabilityAssemblyService
= VERIFIED AS ISOLATED ORCHESTRATION FACADE

IncorporatedReadabilityAssemblyResult
= VERIFIED AS ISOLATED IN-MEMORY RESULT

SemanticAssemblyService
= UNCHANGED

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= VERIFIED
```

---

## 14. Next Decision

Perform:

```text
Incorporated Readability Assembly Review
```

If that review identifies no critical blocker, proceed to:

```text
Continuity Readability model design
```

Do not connect the readability assembly to `SemanticAssemblyService`, `/loop/step`, or SQLite before that review is complete.
