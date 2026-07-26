# 116. vNext Read-only Runtime Projection Minimal PoC

---

## 1. Purpose

This document records the isolated implementation of integration gate A:

```text
existing Runtime result payload
+
explicit vNext record references
↓
ReadOnlyRuntimeProjectionService
↓
ReadOnlyRuntimeProjectionResult
```

The implementation is read-only and one-way.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Added Models

Updated:

```text
app/vnext/models.py
```

Added:

```text
RuntimeSnapshot
RuntimeProjectionReference
ReadOnlyRuntimeProjection
RuntimeSnapshotSpec
RuntimeProjectionReferenceSpec
ReadOnlyRuntimeProjectionRequest
ReadOnlyRuntimeProjectionResult
```

---

## 3. Added Builders

Updated:

```text
app/vnext/builders.py
```

Added:

```text
RuntimeSnapshotBuilder
RuntimeProjectionReferenceBuilder
ReadOnlyRuntimeProjectionBuilder
```

### RuntimeSnapshotBuilder

Performs only:

```text
copy process and slice scope
copy caller-supplied Runtime contract label
deep-copy opaque Runtime payload
deep-copy metadata
create snapshot ID when absent
```

It does not parse, normalize, score, or interpret Runtime fields.

### RuntimeProjectionReferenceBuilder

Performs only:

```text
verify optional expected snapshot ref
verify optional expected process ID
copy explicit record ref, record type, and relation type
copy evidence and metadata
create reference ID when absent
```

It does not resolve the referenced vNext record.

### ReadOnlyRuntimeProjectionBuilder

Performs only:

```text
verify reference process scope
verify references point to the projected snapshot
reject duplicate reference IDs
copy reference IDs
copy metadata
create projection ID when absent
```

---

## 4. Added Service

Added:

```text
app/vnext/runtime_projection.py
ReadOnlyRuntimeProjectionService
```

Primary operation:

```text
project(request)
→ ReadOnlyRuntimeProjectionResult
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

---

## 5. Read-only Boundary

The service does not:

```text
execute Runtime
call POST /loop/step
mutate Runtime result
recalculate Stability
modify OperatorResponse
select OperatorResponse
write back to Runtime history
persist records
```

The Runtime payload is retained as an opaque mapping.

---

## 6. Projection Boundary

```text
RuntimeSnapshot
≠ StabilityScene

RuntimeSnapshot
≠ Runtime history

ReadOnlyRuntimeProjection
≠ canonical Runtime result

RuntimeProjectionReference
≠ ownership or derivation relation
```

A caller may explicitly reference:

```text
StabilityScene
ReadabilityContext
ContinuityRelationRecord
TrajectoryGraph
```

but the projection does not infer or construct those records.

---

## 7. Explicit Non-responsibilities

The implementation does not:

```text
infer Semantic records from Runtime payload
infer Readability records from Runtime payload
infer Continuity records from Runtime payload
infer Trajectory nodes or edges from Runtime history
resolve record refs
validate record types against a registry
select current or authoritative records
publish a public API
create persistence semantics
perform GyroAuth mapping
```

---

## 8. Test Coverage

Added:

```text
tests/vnext/test_read_only_runtime_projection.py
```

Coverage includes:

```text
opaque Runtime payload preservation
nested payload deep-copy
explicit projection reference preservation
reference-only projection grouping
external snapshot reference rejection
snapshot / reference / projection service assembly
empty reference list
projection reference ID duplicate rejection
no Runtime or vNext semantic inference
nested metadata deep-copy
```

The Priority F workflow now executes this test with all accepted Runtime and earlier vNext regression tests.

---

## 9. Isolation Boundary

The implementation remains isolated from:

```text
POST /loop/step
ProcessExecutor
StabilityEngine
OperatorResponse selection
SemanticAssemblyService
IncorporatedReadabilityAssemblyService
ContinuityReadabilityAssemblyService
TrajectoryAssemblyService
SQLite schema
repository reconstruction registry
public API models
GyroAuth
```

---

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Read-only projection added to Core
= NO

Runtime payload interpreted as semantic records
= NO

OperatorResponse behavior changed
= NO

Runtime write-back introduced
= NO

Persistence introduced
= NO

Current RC Runtime contract changed
= NO
```

---

## 11. Current Decision

```text
RuntimeSnapshot
= IMPLEMENTED AS OPAQUE READ-ONLY MODEL

RuntimeProjectionReference
= IMPLEMENTED AS EXPLICIT REFERENCE MODEL

ReadOnlyRuntimeProjection
= IMPLEMENTED AS REFERENCE-ONLY PROJECTION MODEL

RuntimeSnapshotBuilder
= IMPLEMENTED AS PURE BUILDER

RuntimeProjectionReferenceBuilder
= IMPLEMENTED AS PURE BUILDER

ReadOnlyRuntimeProjectionBuilder
= IMPLEMENTED AS PURE BUILDER

ReadOnlyRuntimeProjectionService
= IMPLEMENTED AS ISOLATED ORCHESTRATION FACADE

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```

---

## 12. Review Gate

After workflow verification, perform:

```text
Read-only Runtime Projection Review
```

The review must confirm:

```text
read-only direction
opaque payload boundary
request / record separation
reference-only projection
no semantic inference
no OperatorResponse influence
no persistence coupling
no public API coupling
copy / mutation safety
regression verification
```

Only after that review may B persistence design be considered.
