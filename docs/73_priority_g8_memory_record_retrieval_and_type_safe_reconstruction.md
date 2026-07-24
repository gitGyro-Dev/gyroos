# 73. Priority G-8 — Memory Record Retrieval and Type-safe Reconstruction

---

## 1. Purpose

This document defines and records the implementation of **G-8: Memory Record Retrieval and Type-safe Reconstruction**.

G-7 completed explicit TrajectoryEdge querying.
G-8 strengthens direct canonical record retrieval so that callers receive an explicit typed envelope rather than an untyped payload.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Memory retrieval is a Runtime observation surface.
It does not execute a new Process, evaluate Stability, select OperatorResponse, or reinterpret a stored record.

---

## 2. Endpoint

```text
GET /memory/record/{record_id}
```

The endpoint requires one explicit canonical `record_id`.
It performs no fuzzy lookup, latest-record inference, or cross-record repair.

---

## 3. Typed Response Envelope

Added:

```text
MemoryRecordEnvelope
```

Fields:

```text
record_id
record_type
record
```

The `record` field is a closed union of accepted canonical Runtime types:

```text
LoopStepResult
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
DeferredRelationRecord
TrajectoryEdge
```

`record_type` is the canonical model class name reconstructed by the repository.
The endpoint does not return an arbitrary dictionary or dynamically import a stored type name.

---

## 4. Reconstruction Pipeline

For SQLite-backed records, reconstruction remains:

```text
record_id lookup
→ schema_version verification
→ canonical_payload digest verification
→ closed record registry lookup
→ JSON decoding
→ canonical Pydantic model validation
→ typed Runtime object
→ MemoryRecordEnvelope
```

The stored payload remains authoritative only after all checks pass.

---

## 5. Missing Record Behavior

When the explicit identity is absent:

```text
HTTP 404
error_code = GYRO_API_NOT_FOUND_MEMORY_RECORD
category = NOT_FOUND
phase = MEMORY_RECORD_RETRIEVAL
```

Missing storage identity is not converted into:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
StabilityStatus.NOT_EVALUABLE
```

---

## 6. Reconstruction Failure Behavior

### 6.1 Digest mismatch

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_INTEGRITY
category = REPOSITORY
phase = MEMORY_RECORD_RECONSTRUCTION
```

### 6.2 Schema version mismatch

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_SCHEMA_MISMATCH
category = REPOSITORY
phase = MEMORY_RECORD_RECONSTRUCTION
```

### 6.3 Invalid canonical payload or registry reconstruction failure

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_RECONSTRUCTION
category = REPOSITORY
phase = MEMORY_RECORD_RECONSTRUCTION
```

These are repository failures, not Runtime outcomes.

---

## 7. Process Retrieval Alignment

`GET /process/{process_id}` now also returns a structured not-found response:

```text
HTTP 404
error_code = GYRO_API_NOT_FOUND_PROCESS
category = NOT_FOUND
phase = PROCESS_RETRIEVAL
```

Successful Process retrieval continues to return the complete typed `LoopStepResult`.

---

## 8. Implemented Files

Updated:

```text
app/models.py
app/main.py
tests/test_bounded_api.py
tests/test_sqlite_repository.py
```

Added model:

```text
MemoryRecordEnvelope
```

---

## 9. Tests

API tests verify:

```text
typed StabilityResult envelope
record_id preservation
record_type preservation
canonical record payload preservation
structured missing-record 404
```

SQLite tests verify:

```text
exact typed record reconstruction after restart
canonical digest tampering is rejected
unsupported schema version is rejected
invalid canonical payload is rejected by Pydantic reconstruction
missing record remains None at repository level
```

The existing GitHub Actions workflow runs both affected test files.

---

## 10. Responsibility Review

```text
RuntimeRepository
→ verifies and reconstructs one canonical typed record

GET /memory/record/{record_id}
→ returns explicit identity, canonical type, and typed record
```

The endpoint does not mutate memory, repair records, select current scope, infer history, or create Runtime responses.

---

## 11. G-8 Decision

```text
G-8 Memory Record Retrieval and Type-safe Reconstruction
= IMPLEMENTED

Typed response envelope
= IMPLEMENTED

Closed canonical record union
= IMPLEMENTED

Structured missing behavior
= IMPLEMENTED

Digest, schema, and payload reconstruction boundaries
= IMPLEMENTED

GitHub Actions execution verification
= PENDING
```

After the updated workflow passes, G-8 may be marked:

```text
G-8
= COMPLETE
```

The next Priority G step is:

```text
G-9 Restart and Recovery Tests
```
