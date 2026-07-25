# 85. Priority H-9 — Load and Stress Tests

---

## 1. Purpose

H-9 adds bounded load and stress tests for the GyroOS Runtime API and SQLite repository.

The purpose is to verify that concurrent and sustained execution completes without partial Process publication, duplicate Process identity, repository corruption, or loss of restart reconstruction.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Load testing observes execution and hosting behavior. It does not redefine Stability, OperatorResponse, Process identity, or canonical Runtime meaning.

---

## 2. Bounded CI Scope

H-9 is designed for deterministic GitHub Actions execution rather than capacity benchmarking.

The tests use bounded request counts, worker counts, and elapsed-time ceilings.

Pass/fail is based primarily on:

```text
all operations complete
all expected Process identities are unique
all Process results remain reconstructable
SQLite integrity_check returns ok
current scope and idempotency counts remain consistent
```

Elapsed-time checks are broad deadlock and runaway guards, not production service-level objectives.

---

## 3. Concurrent HTTP Execution

The HTTP load test submits:

```text
24 POST /loop/step requests
8 worker threads
one independent TestClient per worker
```

Each request uses a unique:

```text
request_id
loop_id
idempotency_key
structure_id
```

The test verifies:

```text
all responses return HTTP 200
all returned process_id values are present
all process_id values are unique
execution completes within the bounded CI ceiling
```

This validates concurrent entry through middleware, request validation, Runtime execution, and response handling.

---

## 4. Concurrent SQLite Publication

The repository stress test uses:

```text
20 independent publications
6 worker threads
one SQLiteStore connection boundary per worker
one shared file-backed database
10-second SQLite busy timeout
```

Each worker executes one complete Process publication through `ProcessExecutor`.

After completion, a restarted store verifies:

```text
all Process records are reconstructable
all process_id values are unique
database schema version remains 1
PRAGMA integrity_check = ok
LoopStepResult count = publication count
current_scope count = publication count
idempotency_entries count = publication count
```

SQLite remains the authoritative write coordinator.

---

## 5. Sustained Sequential Publication

The sustained test executes:

```text
100 Process publications
one persistent SQLiteStore
one shared loop_id
unique request and idempotency identities
```

After restarting the store, the test verifies:

```text
100 unique Process identities
100 history items
no additional history cursor
all Process records reconstruct successfully
```

This covers cumulative repository growth, history reconstruction, and restart continuity within a bounded test volume.

---

## 6. Implemented Files

Added:

```text
tests/test_load_stress.py
docs/85_priority_h9_load_and_stress_tests.md
```

Updated:

```text
.github/workflows/priority-f-poc.yml
```

---

## 7. Test Coverage

The H-9 tests verify:

```text
concurrent HTTP request completion
unique Process identity under concurrent HTTP execution
bounded HTTP execution time
concurrent SQLite publication
SQLite WAL write coordination
post-load Process reconstruction
post-load schema metadata preservation
post-load integrity_check
post-load current scope consistency
post-load idempotency consistency
100-publication sustained history reconstruction
```

The workflow executes the H-9 load and stress test file with the existing production-hardening suite.

Verified GitHub Actions run:

```text
Run ID: 30146453552
Job: test-and-run-poc
Conclusion: success
```

---

## 8. Non-goals and Deferred Work

H-9 does not establish:

```text
production throughput targets
requests-per-second guarantees
latency percentiles
multi-process load behavior
multi-host load behavior
network proxy performance
large request-body performance
long-duration soak testing
memory-leak measurement
CPU profiling
connection-pool sizing
external load-generator integration
```

These require a deployed environment and explicit service-level objectives.

---

## 9. Responsibility Review

```text
HTTP load test
→ validates bounded concurrent API execution

SQLite publication stress test
→ validates repository write coordination and atomic publication

sustained publication test
→ validates cumulative persistence and restart reconstruction

production deployment
→ must define actual capacity targets and performance budgets
```

Load-test observations do not become canonical Runtime records or Gyro Logic definitions.

---

## 10. H-9 Decision

```text
H-9 Load and Stress Tests
= COMPLETE

Concurrent HTTP load test
= IMPLEMENTED

Concurrent SQLite publication stress test
= IMPLEMENTED

Sustained publication and restart test
= IMPLEMENTED

GitHub Actions execution verification
= COMPLETE
```

The next Priority H step is:

```text
H-10 Production Readiness Review
```