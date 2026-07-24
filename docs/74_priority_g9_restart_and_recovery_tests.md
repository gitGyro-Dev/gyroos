# 74. Priority G-9 — Restart and Recovery Tests

---

## 1. Purpose

This document defines and records the implementation of **G-9: Restart and Recovery Tests**.

G-8 completed typed canonical record retrieval and reconstruction boundaries.
G-9 verifies that committed Runtime state remains recoverable after process and repository restart without silently rebuilding, mutating, or duplicating canonical records.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Recovery is a repository and application lifecycle concern.
It does not execute an implicit Process, evaluate Stability, or select OperatorResponse.

---

## 2. Recovery Boundary

The initial recovery contract is:

```text
completed SQLite publication
→ repository instance is discarded
→ new SQLiteStore opens the same database
→ committed Runtime state is reconstructed through canonical checks
```

Recovery must preserve:

```text
current-scope pointer
ordered Process history
ordered TrajectoryEdge history
typed canonical memory records
complete LoopStepResult reconstruction
persistent idempotency entries
```

Recovery must not:

```text
create a new Process
advance current scope
append duplicate history
append duplicate trajectory edges
repair invalid records silently
convert repository failure into Runtime status
```

---

## 3. Complete Runtime State Recovery Scenario

The primary G-9 test publishes two bounded Processes for one loop:

```text
Process 1 → CONTINUE / DIRECT_CONNECTION
Process 2 → ADJUST / ADJUSTED_CONNECTION
```

After constructing a new `SQLiteStore` from the same database, the test verifies:

```text
current scope references Process 2
Process history contains Process 1 then Process 2
Trajectory history contains both edges in publication order
TrajectoryEdge objects are reconstructed as typed models
StabilityResult is reconstructed as its exact typed model
Process 2 retains ADJUST and ADJUSTED_CONNECTION
```

The test confirms that current scope, history, trajectory, and direct record retrieval describe the same committed state.

---

## 4. Idempotent Replay after Restart

A completed request is published with a persistent idempotency entry.
The repository is then reopened and the identical request is executed again.

Required behavior:

```text
same loop_id
+
same idempotency_key
+
same request digest
→ original Process replayed
```

The recovery test verifies:

```text
replayed process_id equals original process_id
replayed = true
Process history contains one item only
Trajectory history contains one edge only
current scope remains the original Process
```

Restart does not weaken idempotency protection.

---

## 5. Empty and Missing State after Restart

Opening and reopening an empty database preserves explicit absence:

```text
missing current scope → None
missing Process → None
missing record → None
unknown loop history → empty page
unknown trajectory reference → empty page
```

Absence after restart is not converted into:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
StabilityStatus.NOT_EVALUABLE
```

---

## 6. Implemented Files

Added:

```text
tests/test_restart_recovery.py
```

Updated:

```text
.github/workflows/priority-f-poc.yml
```

The workflow now executes:

```text
tests/test_bounded_api.py
tests/test_priority_f_poc.py
tests/test_sqlite_repository.py
tests/test_restart_recovery.py
```

---

## 7. Test Scenarios

The G-9 test file contains:

```text
test_restart_recovers_complete_runtime_state

test_restart_idempotent_replay_does_not_publish_new_state

test_restart_preserves_empty_and_missing_queries
```

These tests verify application-level recovery using a newly created `SQLiteStore`, not merely repeated reads through the original store instance.

---

## 8. Deferred Recovery Work

G-9 does not yet implement:

```text
crash recovery during an open transaction
WAL-specific recovery testing
concurrent multi-process writer recovery
schema migration recovery
backup and restore tooling
corrupt database file recovery
automatic repair or quarantine
production retry policy
```

These concerns remain outside the bounded Priority G prototype.

---

## 9. Responsibility Review

```text
SQLite transaction boundary
→ guarantees committed or rolled-back publication

SQLiteStore initialization
→ opens persistent storage and prepares schema

canonical reconstruction pipeline
→ verifies and rebuilds typed Runtime objects

G-9 tests
→ verify lifecycle restart behavior across repository instances
```

Recovery does not become the Loop Controller and does not reinterpret canonical Runtime meaning.

---

## 10. G-9 Decision

```text
G-9 Restart and Recovery Tests
= IMPLEMENTED

Complete Runtime state recovery scenario
= IMPLEMENTED

Restart-safe idempotent replay verification
= IMPLEMENTED

Empty and missing state recovery verification
= IMPLEMENTED

GitHub Actions execution verification
= PENDING
```

After the updated workflow passes, G-9 may be marked:

```text
G-9
= COMPLETE
```

The next Priority G step is:

```text
G-10 Priority G Cross-document Review and Refinement
```
