# 69. Priority G-4 — Atomic Publication and Idempotency Persistence

---

## 1. Purpose

This document records the design and implementation of **G-4: Atomic Publication and Idempotency Persistence**.

G-3 introduced the first SQLite-backed Runtime repository.
G-4 strengthens that implementation so that publication failure, record identity collision, and idempotency conflict remain explicit repository concerns rather than becoming partial Runtime state.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Persistence does not execute Slice, evaluate Stability, or select OperatorResponse.

---

## 2. G-4 Goal

G-4 establishes:

```text
complete publication transaction
+
explicit repository-level error categories
+
restart-safe idempotency persistence
+
conflict detection before publication
+
fault-injection rollback verification
```

The canonical visibility rule is:

```text
all required writes succeed
→ complete Process becomes visible

any required write fails
→ no part of the new Process becomes visible
```

---

## 3. Repository Error Boundary

The following storage-independent repository errors were added in:

```text
app/repository_errors.py
```

```text
RepositoryError
RecordIdentityCollision
IdempotencyConflict
RepositoryIntegrityError
RepositorySerializationError
RepositorySchemaMismatch
```

These errors are repository failures.
They are not Runtime outcomes.

```text
RepositoryError
≠ StabilityStatus
≠ Boundary State
≠ OperatorResponse
≠ RuntimeContinuityType
≠ VoidEvidence
```

SQLite-specific exceptions are translated before they leave `SQLiteStore`.

---

## 4. Atomic Publication Boundary

`SQLiteStore.publish(...)` remains the single persistent transaction boundary.

The transaction contains, when generated:

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
current-scope pointer update
idempotency entry
```

The transaction begins with:

```text
BEGIN IMMEDIATE
```

The Python SQLite context manager commits only after the complete publication method exits successfully.
Any exception causes rollback.

No successful publication may expose:

```text
Process without supporting Runtime records
current-scope pointer to an unpublished Process
idempotency entry referencing an unpublished Process
partial evidence records
partial TrajectoryEdge publication
```

---

## 5. Record Identity Collision

Canonical record identity remains type-specific:

```text
LoopStepResult            → process_id
SliceDone                 → slice_id
StabilityResult           → stability_result_id
OperatorResponse          → operator_response_id
RuntimeContinuityResult   → continuity_result_id
BoundaryEvidence          → boundary_evidence_id
BoundaryStateRecord       → boundary_state_record_id
ContextEvidence           → context_evidence_id
VoidEvidence              → void_evidence_id
DeferredRelationRecord    → deferred_relation_record_id
TrajectoryEdge            → trajectory_edge_id
```

Two collision boundaries are enforced:

```text
publication group contains duplicate canonical IDs
→ RecordIdentityCollision before transaction

SQLite primary-key collision during transaction
→ RecordIdentityCollision and rollback
```

The repository does not silently overwrite canonical records.

---

## 6. Idempotency Persistence

Idempotency scope remains:

```text
(loop_id, idempotency_key)
```

The persistent entry contains:

```text
request_digest
process_id
```

Required behavior:

```text
same loop_id
+
same idempotency_key
+
same request_digest
→ original completed Process is replayed

same loop_id
+
same idempotency_key
+
different request_digest
→ IdempotencyConflict

idempotency entry references missing Process
→ RepositoryIntegrityError
```

The `ProcessExecutor` continues to detect normal replay before executing a new Process.
`SQLiteStore.publish(...)` independently protects the persistent transaction against direct or concurrent conflicting publication.

Idempotency lookup does not create or mutate Runtime records.

---

## 7. Fault Injection Boundary

`SQLiteStore` now accepts an optional test-only failure injector:

```python
SQLiteStore(database_path, failure_injector=...)
```

Supported injection phases include:

```text
before_record_insert
before_current_scope
before_idempotency
```

The injector is not Runtime policy and is not used in normal application execution.
It exists only to verify transaction rollback at deterministic positions.

The main rollback scenario injects a database failure after canonical records have been inserted but before the current-scope update.

Expected result:

```text
runtime_records count = 0
current_scope count = 0
idempotency_entries count = 0
```

This verifies that inserted records are not visible after a later transaction failure.

---

## 8. Implemented Tests

`tests/test_sqlite_repository.py` now verifies:

```text
complete Process persistence and typed reconstruction
restart-safe current scope
restart-safe idempotent replay
missing record remains None
rollback after injected mid-publication failure
no Runtime records remain after rollback
no current-scope pointer remains after rollback
no idempotency entry remains after rollback
same key with changed request digest is rejected
repository-level direct idempotency conflict is rejected
record identity collision is translated to RecordIdentityCollision
```

The tests preserve the distinction:

```text
failed publication
≠ completed Process

idempotency conflict
≠ STOP
≠ DEFER
≠ VOID
```

---

## 9. Responsibility Review

The responsibility chain remains:

```text
SliceEngine
→ SliceDone and evidence

StabilityEngine
→ StabilityResult

LoopController
→ OperatorResponse

ContinuityBuilder
→ RuntimeContinuityResult

ProcessExecutor
→ one complete bounded result group

SQLiteStore
→ atomic persistence, conflict detection, and explicit retrieval
```

The repository does not repair, reinterpret, or partially publish Runtime objects.

---

## 10. Deferred Work

G-4 does not yet implement:

```text
HTTP mapping for repository-level errors
multi-process writer coordination beyond SQLite transaction semantics
history query pagination
Trajectory query pagination
schema migration
production retry policy
backup and restore operations
```

These remain later Priority G work.

---

## 11. G-4 Decision

```text
G-4 Atomic Publication and Idempotency Persistence
= IMPLEMENTED

Repository-level error boundary
= IMPLEMENTED

Atomic rollback fault injection
= IMPLEMENTED

Persistent idempotency conflict protection
= IMPLEMENTED

GitHub Actions execution verification
= PENDING RUN CONFIRMATION
```

After the updated workflow passes, G-4 may be marked:

```text
G-4
= COMPLETE
```

The next Priority G step is:

```text
G-5 Current-scope Query Endpoint
```
