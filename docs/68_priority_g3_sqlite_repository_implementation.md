# 68. Priority G-3 — SQLite Repository Implementation

---

## 1. Purpose

This document records the implementation decision and delivered scope for **G-3: SQLite Repository Implementation**.

G-1 established the storage-independent repository boundary.
G-2 established the canonical persistence envelope and reconstruction rules.
G-3 introduces the first persistent repository implementation without changing the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

SQLite remains a Runtime support implementation choice.
It does not become part of Gyro Logic and does not select OperatorResponse.

---

## 2. Delivered Implementation

The following file was added:

```text
app/sqlite_repository.py
```

It provides:

```text
SQLiteStore
schema initialization
canonical JSON serialization
SHA-256 canonical digest
closed record-type registry
typed Pydantic reconstruction
explicit record retrieval
explicit Process retrieval
current-scope persistence
idempotency persistence
atomic publication transaction
```

The implementation uses only Python standard-library `sqlite3` for storage access.

---

## 3. Repository Contract Conformance

`SQLiteStore` implements the existing executor-facing operations:

```text
get_process(process_id)
get_record(record_id)
get_current_scope(loop_id)
get_idempotent(loop_id, key)
publish(result, request_digest, idempotency_key)
```

Therefore the accepted execution relation remains:

```text
ProcessExecutor
→ repository contract
→ InMemoryStore | SQLiteStore
```

The executor does not receive or depend on:

```text
SQLite connection
SQL statement
table name
row shape
transaction cursor
```

---

## 4. SQLite Schema

The implementation creates three bounded tables.

### 4.1 runtime_records

Stores canonical Runtime records with:

```text
record_id
record_type
process_id
loop_id
canonical_payload
canonical_digest
schema_version
runtime_version
publication_id
publication_order
created_at
```

### 4.2 current_scope

Stores the explicit relation:

```text
loop_id
→ current process_id
```

This pointer does not replace or delete Process history.

### 4.3 idempotency_entries

Stores:

```text
loop_id
idempotency_key
request_digest
process_id
```

The primary identity is:

```text
(loop_id, idempotency_key)
```

---

## 5. Canonical Record Registry

The first registry supports:

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

Unknown record types are rejected.
Stored payloads are reconstructed only through the registered canonical Pydantic model.

```text
stored payload
→ digest verification
→ registry lookup
→ Pydantic validation
→ typed Runtime object
```

The implementation does not dynamically import or execute a stored type name.

---

## 6. Atomic Publication

`SQLiteStore.publish(...)` begins one immediate SQLite transaction and inserts the complete result group.

The group contains, when generated:

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
current-scope update
idempotency entry
```

Required behavior:

```text
all writes succeed
→ transaction commits
→ complete Process becomes visible

one write fails
→ transaction rolls back
→ no partial completed Process becomes visible
```

SQLite primary-key and transaction constraints provide the initial identity-collision boundary.
Detailed rollback fault-injection tests remain part of G-4.

---

## 7. Typed Retrieval

`get_record(record_id)` performs:

```text
explicit identity lookup
digest verification
schema-version verification
closed registry lookup
canonical Pydantic validation
typed object return
```

Missing behavior remains:

```text
record not found
→ None
```

It does not become:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
```

`get_process(process_id)` additionally requires the restored object to be `LoopStepResult`.

---

## 8. Restart-safe Behavior

A new `SQLiteStore` instance opened on the same database file can reconstruct:

```text
completed LoopStepResult
all created_record_refs
current-scope pointer
idempotency entry
```

The restart tests demonstrate:

```text
execute and publish Process
→ discard first store instance
→ create second store instance
→ retrieve original Process
→ retrieve supporting records
→ preserve current scope
→ replay original Process by idempotency
```

This is the minimal persistent behavior required for G-3.
Expanded recovery cases remain part of G-9.

---

## 9. Tests and Execution Evidence

The following test file was added:

```text
tests/test_sqlite_repository.py
```

It verifies:

```text
complete Process persistence
canonical typed reconstruction
supporting record retrieval
current-scope persistence after restart
idempotent replay after restart
missing record returns None
```

The GitHub Actions workflow executes:

```text
tests/test_bounded_api.py
tests/test_priority_f_poc.py
tests/test_sqlite_repository.py
```

Execution evidence:

```text
Workflow run ID
= 30071178485

Job ID
= 89412200920

Job conclusion
= success

SQLite repository test step
= completed / success
```

The run verifies that the bounded API, PoC, and SQLite repository tests pass together.

---

## 10. Deferred Work

G-3 intentionally does not yet provide:

```text
process history pagination
trajectory query pagination
repository error classes
failure-injection rollback tests
schema migration
connection pooling
multi-process writer coordination
production backup or retention policy
```

These map to later Priority G steps:

```text
G-4 atomic publication and idempotency refinement
G-5 current-scope query endpoint
G-6 Process history query endpoint
G-7 Trajectory query endpoint
G-8 typed memory retrieval refinement
G-9 restart and recovery expansion
```

---

## 11. Responsibility Review

The implementation preserves:

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
→ complete bounded result group

SQLiteStore
→ atomic persistence and explicit retrieval
```

No persistence component selects or changes Runtime meaning.

---

## 12. G-3 Decision

```text
G-3 SQLite Repository Implementation
= COMPLETE

Repository contract compatibility
= ACCEPTED

Canonical typed reconstruction
= VERIFIED

Restart-safe base retrieval
= VERIFIED

GitHub Actions execution verification
= PASS
```

The next design and implementation step is:

```text
G-4 Atomic Publication and Idempotency Persistence
```