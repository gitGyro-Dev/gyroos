# 75. Priority G-10 — Cross-document Review and Refinement

---

## 1. Purpose

This document records the cross-document review of Priority G after completion of G-1 through G-9.

The review checks whether implementation, tests, workflow, README, and Priority G design documents describe the same bounded Runtime contract.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Priority G remains an implementation and persistence boundary. It does not redefine Gyro Logic.

---

## 2. Reviewed Scope

Reviewed implementation surfaces:

```text
app/models.py
app/runtime.py
app/repositories.py
app/repository_errors.py
app/sqlite_repository.py
app/main.py
```

Reviewed tests:

```text
tests/test_bounded_api.py
tests/test_priority_f_poc.py
tests/test_sqlite_repository.py
tests/test_restart_recovery.py
```

Reviewed workflow:

```text
.github/workflows/priority-f-poc.yml
```

Reviewed Priority G documents:

```text
docs/66_priority_g1_sqlite_persistence.md
docs/67_priority_g2_repository_schema.md
docs/68_priority_g3_type_safe_reconstruction.md
docs/69_priority_g4_atomic_publication.md
docs/70_priority_g5_current_scope_query_endpoint.md
docs/71_priority_g6_process_history_query_endpoint.md
docs/72_priority_g7_trajectory_query_endpoint.md
docs/73_priority_g8_memory_record_retrieval_and_type_safe_reconstruction.md
docs/74_priority_g9_restart_and_recovery_tests.md
```

---

## 3. Verified Runtime Contract

The implemented bounded Runtime API is:

```text
POST /loop/step
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /trajectory/{trajectory_ref}
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

Responsibility separation remains:

```text
POST /loop/step
→ executes and publishes one bounded Process

GET query surfaces
→ observe committed Runtime state only
```

Query endpoints do not execute Slice, calculate Stability, select Operator Response, or mutate current scope.

---

## 4. Persistence and Publication Review

The accepted publication boundary is:

```text
complete LoopStepResult and canonical child records
+
current-scope pointer
+
idempotency entry when supplied
→ one SQLite transaction
```

Verified properties:

```text
atomic publication
rollback on publication failure
record identity collision protection
persistent idempotency conflict protection
canonical JSON digest verification
schema-version verification
closed record registry reconstruction
Pydantic type validation
```

Committed Process history and TrajectoryEdge history remain append-oriented observation surfaces.

---

## 5. Current Scope, History, and Trajectory Separation

The review confirms:

```text
current scope
≠ complete Process history
≠ TrajectoryEdge history
```

Current scope is one explicit pointer per `loop_id`.

Process history is an ordered bounded summary of committed Processes for one explicit `loop_id`.

Trajectory query returns committed typed `TrajectoryEdge` records matching an explicit reference.

Trajectory match fields are:

```text
relation_ref
source_ref
target_ref
parent_process_ref
```

`relation_ref` preserves `Structure.current_mode.relation_ref`.

`source_ref` remains the Slice input source.

---

## 6. Typed Retrieval and Reconstruction Review

Direct memory retrieval returns:

```text
MemoryRecordEnvelope
├─ record_id
├─ record_type
└─ record
```

The `record` field is restricted to the closed canonical Runtime record union.

SQLite reconstruction follows:

```text
record identity lookup
→ schema version check
→ canonical digest check
→ closed registry lookup
→ JSON decoding
→ Pydantic validation
→ typed Runtime object
```

Repository failures remain separate from Runtime outcomes.

---

## 7. Restart and Recovery Review

The review confirms recovery across a newly created `SQLiteStore` instance preserves:

```text
current scope
Process history order
TrajectoryEdge order
typed records
complete Process meaning
persistent idempotency behavior
```

Identical replay after restart does not publish a new Process or duplicate history.

Empty and missing state remains explicit absence rather than VOID, DEFER, STOP, or NOT_EVALUABLE.

---

## 8. Test and Workflow Alignment

At Priority G completion, the GitHub Actions workflow executed:

```text
tests/test_bounded_api.py
tests/test_priority_f_poc.py
tests/test_sqlite_repository.py
tests/test_restart_recovery.py
```

The G-9 verification run completed successfully:

```text
run_id = 30080831829
job_id = 89441803281
conclusion = success
```

Priority H subsequently extended the same workflow with production-hardening, recovery, security, and load tests. The complete G + H workflow is reviewed separately in the Priority G + H Cross Review.

---

## 9. Refinements Applied During G-10

README was updated to include:

```text
Priority G API endpoint list
atomic persistence boundary
query responsibility boundary
Priority G document index
current app and test structure
Priority G roadmap state
```

G-7 documentation had already been refined to preserve the distinction:

```text
relation_ref
≠ source_ref
```

G-9 was updated from implementation-pending to verified complete with workflow evidence.

Priority H completion later updated README again so the repository entry point now describes both the persistent Runtime boundary and production hardening.

---

## 10. Priority G Deferred Work and Priority H Disposition

At Priority G completion, the following were intentionally deferred:

```text
cursor tokens stable under concurrent insertion
indexed normalized trajectory relation columns
WAL-specific lifecycle tests
concurrent multi-process writers
schema migration framework
backup and restore tooling
corrupt database recovery
production authentication and authorization
rate limiting
observability and operational metrics
production deployment configuration
```

Priority H disposition:

```text
WAL configuration and lock lifecycle
→ implemented and tested in H-4 / H-9

bounded concurrent SQLite writers
→ implemented and tested in H-4 / H-9

schema compatibility boundary
→ implemented in H-6

backup and restore tooling
→ implemented in H-7

corrupt or incompatible backup rejection
→ implemented in H-7

production authentication boundary
→ implemented in H-2 / H-8

rate and resource limiting
→ implemented in H-3

structured operational diagnostics
→ implemented in H-5

production configuration profiles and fail-fast
→ implemented in H-1 / H-8
```

Still deferred after Priority H:

```text
cursor tokens stable under concurrent insertion
indexed normalized trajectory relation columns
migration beyond schema version 1
multi-host or distributed writer coordination
external metrics and tracing
public production deployment declarations and SLOs
```

These remaining items are either future repository evolution or deployment-specific work. They do not invalidate the bounded single-host SQLite RC scope.

---

## 11. Cross-document Decision

```text
Core invariant consistency
= VERIFIED

Process / current scope / history / trajectory separation
= VERIFIED

InMemoryStore / SQLiteStore contract alignment
= VERIFIED

API / repository error boundary alignment
= VERIFIED

Typed reconstruction alignment
= VERIFIED

Restart and idempotency alignment
= VERIFIED

README / implementation surface alignment
= VERIFIED AFTER PRIORITY H SYNCHRONIZATION

G-1 through G-10
= COMPLETE
```

Priority G completion status:

```text
Priority G Cross-document Review and Refinement
= COMPLETE
```

No Runtime behavior was changed by this document reconciliation.

---

## 12. Relationship to Priority H and RC Review

Priority G established the bounded persistent Runtime contract.

Priority H hardened that contract without changing its canonical semantics.

```text
Priority G
→ persistent Runtime and observation surfaces

Priority H
→ configuration, admission, concurrency, observability,
  compatibility, recovery, security, and load hardening
```

The next decision point is:

```text
Priority G + Priority H Cross Review
→ RC Review
→ RC Acceptance or targeted return-to-hardening
```
