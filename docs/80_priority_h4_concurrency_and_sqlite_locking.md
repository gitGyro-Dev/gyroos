# 80. Priority H-4 — Concurrency and SQLite Locking

---

## 1. Purpose

H-4 defines the bounded write-concurrency contract for the SQLite-backed GyroOS Runtime repository.

The purpose is to distinguish temporary lock contention from persistent corruption, preserve atomic publication, and make retry behavior explicit at the API boundary.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

SQLite lock state is a repository hosting condition. It does not evaluate Stability, select OperatorResponse, or create canonical Runtime meaning.

---

## 2. Connection Configuration

Every SQLite connection now applies:

```text
PRAGMA foreign_keys = ON
PRAGMA busy_timeout = configured timeout in milliseconds
```

File-backed databases additionally apply:

```text
PRAGMA journal_mode = WAL
PRAGMA synchronous = NORMAL
```

The configured timeout remains sourced from:

```text
GYROOS_SQLITE_TIMEOUT_SECONDS
```

The Python connection timeout and SQLite `busy_timeout` use the same bounded value.

---

## 3. Write Transaction Boundary

Publication continues to use:

```sql
BEGIN IMMEDIATE
```

This obtains the SQLite write reservation before canonical records, current scope, and idempotency state are changed.

One publication remains one transaction:

```text
canonical records
+ current scope
+ idempotency entry
= one atomic publication group
```

If the write reservation cannot be obtained within the configured timeout, no partial publication is committed.

---

## 4. Repository Busy Error

Added:

```text
RepositoryBusyError
```

SQLite operational errors containing:

```text
database is locked
database is busy
```

are translated into this temporary repository error.

They are no longer classified as `RepositoryIntegrityError`.

Other SQLite database failures remain integrity failures unless a more specific repository error applies.

---

## 5. API Contract

When `/loop/step` reaches publication and the repository remains locked beyond the configured timeout:

```text
HTTP 503 Service Unavailable
error_code = GYRO_API_REPOSITORY_BUSY
category = REPOSITORY
phase = PUBLICATION
retryable = true
```

This response means the request may be retried after bounded backoff.

It does not mean:

```text
Process invalid
Stability failure
OperatorResponse STOP
BoundaryState VOID
persistent repository corruption
```

---

## 6. Read and Write Concurrency

WAL mode permits readers to continue while another connection owns a write transaction, subject to normal SQLite snapshot semantics.

SQLite still permits only one writer at a time.

H-4 does not simulate parallel writes through in-memory locks. SQLite remains the authoritative inter-process write coordinator.

The H-3 request semaphore limits admitted HTTP concurrency, while H-4 handles repository-level contention that may still occur across threads, processes, maintenance tools, or other database clients.

---

## 7. Implemented Files

Added:

```text
tests/test_sqlite_locking.py
docs/80_priority_h4_concurrency_and_sqlite_locking.md
```

Updated:

```text
app/repository_errors.py
app/sqlite_repository.py
app/main.py
.github/workflows/priority-f-poc.yml
```

---

## 8. Test Coverage

The H-4 tests verify:

```text
file-backed SQLite uses WAL
busy_timeout matches configured timeout
external BEGIN IMMEDIATE lock causes RepositoryBusyError
failed locked publication leaves no current scope
failed locked publication leaves no idempotency entry
publication succeeds after the external lock is released
```

The workflow now executes the H-4 locking test file.

---

## 9. Deferred Concurrency Work

H-4 does not yet implement:

```text
multi-process stress testing
cross-host database coordination
distributed transaction management
write queues
automatic retry loops
exponential backoff policy
connection pooling
PostgreSQL repository adapter
online checkpoint scheduling
long-running transaction telemetry
```

Automatic retry is intentionally deferred because replay policy must remain explicit and must respect request idempotency.

---

## 10. Responsibility Review

```text
ResourceLimitMiddleware
→ bounds admitted HTTP concurrency

SQLiteStore
→ owns SQLite connection and transaction behavior

SQLite
→ coordinates file-level write locks

RepositoryBusyError
→ represents temporary lock contention

API boundary
→ exposes retryable 503 without changing Runtime semantics
```

No lock state becomes part of canonical Process identity, trajectory, Stability, or memory records.

---

## 11. H-4 Decision

```text
H-4 Concurrency and SQLite Locking
= IMPLEMENTED

WAL mode
= IMPLEMENTED

Configured busy timeout
= IMPLEMENTED

Atomic BEGIN IMMEDIATE publication
= PRESERVED

Temporary lock-contention error separation
= IMPLEMENTED

Retryable API response
= IMPLEMENTED

GitHub Actions execution verification
= PENDING
```

After the updated workflow passes, H-4 may be marked:

```text
H-4
= COMPLETE
```

The next Priority H step is:

```text
H-5 Structured Logging and Operational Diagnostics
```
