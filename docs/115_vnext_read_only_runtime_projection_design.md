# 115. vNext Read-only Runtime Projection Design

---

## 1. Purpose

This document defines integration gate A:

```text
A. read-only Runtime projection
```

The goal is to expose one explicit, immutable projection from an existing Runtime result into the isolated vNext architecture without changing Runtime execution, OperatorResponse selection, persistence, or public API behavior.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The layer direction remains:

```text
Gyro Logic
↓
GyroOS
↓
GyroAuth
```

---

## 2. Design Principle

The projection is read-only and one-way:

```text
existing Runtime result snapshot
+
explicit vNext record references
↓
ReadOnlyRuntimeProjection
```

It does not feed data back into Runtime.

It does not alter:

```text
ProcessExecutor
StabilityEngine
OperatorResponse
POST /loop/step
Runtime history
SQLite schema
canonical repository records
```

---

## 3. Projection Is Not Conversion

```text
Runtime result
≠ vNext semantic record

ReadOnlyRuntimeProjection
≠ Runtime result replacement

ReadOnlyRuntimeProjection
≠ canonical cross-layer result
```

The projection records an explicit observational association only.

It does not reinterpret Runtime values as:

```text
StabilityScene
DifferenceObject
BoundaryEvaluation
ReadabilityContext
ContinuityRelationRecord
TrajectoryGraph
```

unless the caller explicitly supplies references to already constructed records.

---

## 4. Minimal Models

### 4.1 RuntimeSnapshot

```text
runtime_snapshot_id
process_id
slice_ref
runtime_contract
payload
captured_at
metadata
```

`payload` is an opaque deep-copied mapping.

The projection layer does not parse, normalize, score, validate, or mutate its internal Runtime fields.

`runtime_contract` is caller-supplied text identifying the source contract or version.

### 4.2 RuntimeProjectionReference

```text
projection_reference_id
process_id
runtime_snapshot_ref
record_ref
record_type
relation_type
provisional
evidence_refs[]
metadata
```

This is one explicit relation between the Runtime snapshot and an existing vNext record reference.

It does not establish ownership, derivation, equivalence, synchronization, causality, or authority.

### 4.3 ReadOnlyRuntimeProjection

```text
runtime_projection_id
process_id
runtime_snapshot_ref
projection_reference_refs[]
provisional
created_at
metadata
```

The projection stores references only.

It does not embed full vNext records.

---

## 5. Minimal Assembly Boundary

Proposed input models:

```text
RuntimeSnapshotSpec
RuntimeProjectionReferenceSpec
ReadOnlyRuntimeProjectionRequest
```

Proposed output model:

```text
ReadOnlyRuntimeProjectionResult
```

Proposed service:

```text
ReadOnlyRuntimeProjectionService
```

Assembly order:

```text
RuntimeSnapshotBuilder
↓
RuntimeProjectionReferenceBuilder[]
↓
ReadOnlyRuntimeProjectionBuilder
```

This is implementation order only.

It does not define theoretical, temporal, causal, continuation, or authority order.

---

## 6. Validation Boundary

The minimal implementation validates only:

```text
request process_id matches snapshot process_id
projection reference process_id matches snapshot process_id
projection reference points to the request-local snapshot
projection reference IDs are unique within the request
```

It does not resolve or validate `record_ref` against a registry or repository.

It does not validate that `record_type` matches the referenced object.

---

## 7. Explicit Non-responsibilities

The projection does not:

```text
execute Runtime
call POST /loop/step
mutate Runtime result
recalculate Stability
select or modify OperatorResponse
interpret Runtime history as Trajectory
infer Semantic records
infer Readability records
infer Continuity records
infer Trajectory nodes or edges
select current or authoritative records
persist data
publish a public API
perform GyroAuth mapping
```

---

## 8. Copy and Immutability Boundary

All supplied Runtime payloads and nested metadata must be deep-copied.

Caller mutation after projection must not rewrite:

```text
RuntimeSnapshot
RuntimeProjectionReference
ReadOnlyRuntimeProjection
ReadOnlyRuntimeProjectionResult
```

---

## 9. Failure Boundary

Invalid explicit references are rejected during assembly.

No fallback lookup, latest-record selection, repository search, inferred replacement, or partial persistence is permitted.

---

## 10. Integration Gate Decision

```text
Read-only direction
= REQUIRED

Runtime write-back
= FORBIDDEN

OperatorResponse influence
= FORBIDDEN

SQLite integration
= FORBIDDEN

Public API exposure
= FORBIDDEN

GyroAuth consumption
= OUT OF SCOPE
```

---

## 11. Implementation Plan

```text
1. add projection models
2. add pure builders
3. add isolated projection service
4. add model/builder/service tests
5. include tests in Priority F workflow
6. verify GitHub Actions
7. perform Read-only Runtime Projection Review
8. only then make B persistence design decision
```

---

## 12. Current Decision

```text
A design
= COMPLETE

Critical design blocker
= NONE IDENTIFIED

A minimal implementation
= APPROVED

Runtime integration beyond read-only projection
= NOT APPROVED

B persistence design
= DEFERRED UNTIL A REVIEW
```
