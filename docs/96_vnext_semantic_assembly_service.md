# 96. vNext Semantic Assembly Service

---

## 1. Purpose

This document records the first isolated orchestration step after verification of all initial vNext pure builders.

The implemented scope is intentionally limited to:

```text
explicit semantic inputs
→ SemanticAssemblyRequest
→ SemanticAssemblyService
→ SemanticAssemblyResult
→ SemanticRealizationBundle
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The assembly service is an implementation facade. It is not a new Core stage, semantic decision engine, canonical Process executor, or persistence transaction.

---

## 2. Added Components

Updated:

```text
app/vnext/models.py
```

Added input models:

```text
StabilityObservationSpec
DifferenceSpec
BoundaryEvaluationSpec
SemanticAssemblyRequest
```

Added output model:

```text
SemanticAssemblyResult
```

Added service:

```text
app/vnext/assembly.py
SemanticAssemblyService
```

Primary operation:

```text
assemble(request)
→ SemanticAssemblyResult
```

---

## 3. Assembly Sequence

The service coordinates existing builders in the following implementation order:

```text
StabilitySceneBuilder
↓
StabilityObservationBuilder[]
↓
DifferenceObjectBuilder[]
↓
BoundaryEvaluationBuilder[]
↓
SemanticRealizationBundleBuilder
```

This is an orchestration order only.

It does not establish a new Gyro Logic theoretical sequence, causal order, universal evaluation order, or canonical Runtime publication order.

---

## 4. Request / Record Separation

Assembly input is represented as explicit specification models:

```text
StabilityObservationSpec
DifferenceSpec
BoundaryEvaluationSpec
```

These specification models are not constructed semantic records.

The service uses them to create:

```text
StabilityObservation
DifferenceObject
BoundaryEvaluation
```

This preserves the distinction between:

```text
caller-supplied construction specification
≠
constructed semantic record
```

---

## 5. Service Responsibility

The service performs only:

```text
construct one StabilityScene from explicit typed inputs
construct zero or more StabilityObservation records
construct zero or more DifferenceObject records
resolve BoundaryEvaluationSpec.difference_ref within the same request
construct zero or more BoundaryEvaluation records
construct one reference-only SemanticRealizationBundle
return all in-memory constructed records
```

The service delegates semantic record validation and copy behavior to the existing pure builders and models.

---

## 6. Explicit Non-responsibilities

The service does not:

```text
infer readable relations
infer unresolved items
calculate Stability
infer a score
assign a Stability classification
select a preferred StabilityObservation
extract Difference from Structure
extract Difference from LocalArticulation
compare DifferenceObject records
calculate distance or error
normalize or scalarize Difference
infer Boundary readability
apply thresholds
select a Boundary policy
create BoundaryEvidence
create BoundaryStateRecord
select OperatorResponse
build RuntimeContinuityResult
build Trajectory
persist records
create an atomic publication group
register canonical record types
modify POST /loop/step
modify SQLite schema
```

A service result is not a current Runtime Process result.

---

## 7. Reference Boundary

Each `BoundaryEvaluationSpec` must reference a `DifferenceSpec` assembled in the same request.

```text
BoundaryEvaluationSpec.difference_ref
→ one assembled DifferenceObject.difference_id
```

A missing reference is rejected.

The service does not search a repository, infer an external latest record, or import a Difference from another request.

---

## 8. Optional Records

A valid request may contain:

```text
zero StabilityObservation specs
zero Difference specs
zero BoundaryEvaluation specs
```

The resulting scene and bundle remain valid.

The service does not synthesize missing observations, Differences, or Boundary evaluations.

---

## 9. Test Coverage

Added:

```text
tests/vnext/test_semantic_assembly_service.py
```

The tests verify:

```text
existing builders are assembled into one reference bundle
optional record groups may remain empty
scene content does not cause implicit Stability observation inference
explicit undefined Difference remains undefined
BoundaryEvaluationSpec outside the assembled Difference set is rejected
nested request inputs remain isolated through builder copy boundaries
```

The existing workflow executes this end-to-end isolated assembly test together with:

```text
Priority G regression tests
Priority H regression tests
all earlier vNext model and builder tests
```

Verified successful workflow runs:

```text
30149667186
30149679505
30149695400
30149713689
```

---

## 10. Isolation Boundary

The assembly service remains isolated from:

```text
POST /loop/step
current ProcessExecutor
current SliceEngine
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

## 11. Next Decision

The initial vNext semantic construction pipeline is complete as an isolated in-memory PoC.

The next decision is a review, not an immediate Runtime connection.

```text
vNext Semantic Assembly Review
```

That review determines whether the next concept is:

```text
Incorporated Readability
```

or whether a compatibility projection experiment is needed before further semantic expansion.

No `/loop/step` or SQLite integration begins before that review is complete.

---

## 12. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Assembly order treated as theoretical Core sequence
= NO

Stability reduced to score
= NO

Difference reduced to numeric distance
= NO

Boundary inferred automatically
= NO

GyroAuth-specific policy introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 13. Current Decision

```text
DifferenceObjectBuilder
= VERIFIED AS ISOLATED PURE BUILDER

SemanticAssemblyRequest
= VERIFIED AS ISOLATED INPUT MODEL

SemanticAssemblyService
= VERIFIED AS ISOLATED ORCHESTRATION FACADE

SemanticAssemblyResult
= VERIFIED AS ISOLATED IN-MEMORY RESULT

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= COMPLETE
```
