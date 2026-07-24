# 65. Priority G — Persistent Runtime State and Query API Assessment

---

## 1. Purpose

This document begins **Priority G: Persistent Runtime State and Query API** after completion of Priority F.

Priority F established and execution-verified:

```text
bounded /loop/step implementation
+
canonical Runtime objects
+
repeatable PoC scenarios
+
TrajectoryEdge and DeferredRelationRecord preservation
+
GitHub Actions test and artifact generation
```

Priority G moves from an in-memory demonstration toward a reconstructable Runtime state surface without changing the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

Persistence and query are Runtime support responsibilities.
They do not redefine Gyro Logic and do not select OperatorResponse.

---

## 2. Why Priority G Is Next

The current PoC proves that one bounded Process can be executed and observed.
However, the current repository still relies on an in-memory store.

This means:

```text
Process records disappear when the application restarts
current-scope state is not durable
Trajectory history cannot be reconstructed across runs
DeferredRelationRecord is not durable
explicit references cannot survive process restart
supporting query endpoints remain incomplete
```

The next safe step is therefore not production deployment or GyroAuth integration.
It is to make the accepted Runtime records durable and queryable while preserving the Priority E and F boundaries.

---

## 3. Priority G Goal

Priority G must establish:

```text
a repository interface independent of storage technology
+
a minimal persistent implementation
+
atomic publication of complete Runtime result groups
+
explicit query endpoints
+
current-scope and complete-history separation
+
restart-safe identity and lineage reconstruction
```

The target is a bounded persistent Runtime prototype.
It is not a distributed database or production-grade event platform.

---

## 4. Proposed Priority G Scope

```text
G-1  Persistence Boundary and Repository Contract
G-2  Canonical Persistent Record Envelope
G-3  SQLite Repository Implementation
G-4  Atomic Publication and Idempotency Persistence
G-5  Current-scope Query Endpoint
G-6  Process History Query Endpoint
G-7  Trajectory Query Endpoint
G-8  Memory Record Retrieval and Type-safe Reconstruction
G-9  Restart and Recovery Tests
G-10 Priority G Cross-document Review and Refinement
```

This order is intentional.

```text
repository contract
→ record envelope
→ storage implementation
→ publication semantics
→ query endpoints
→ restart tests
→ review
```

---

## 5. G-1 — Persistence Boundary

The storage layer may:

```text
store canonical Runtime records
resolve explicit identities
publish complete result groups atomically
preserve idempotency records
preserve current-scope pointers
return ordered Process and Trajectory records
```

It must not:

```text
execute Slice
read Stability
select OperatorResponse
reinterpret Boundary State
infer an unidentified latest record
collapse history into current scope
convert missing storage records into VoidEvidence
```

The repository interface must remain usable by both:

```text
InMemoryStore
SQLiteStore
```

The Runtime executor must depend on the repository contract, not on SQLite-specific behavior.

---

## 6. G-2 — Persistent Record Envelope

Every stored Runtime object should be represented by a common persistence envelope containing at least:

```text
record_id
record_type
process_id when applicable
loop_id when applicable
canonical_payload
canonical_digest
created_at
schema_version
runtime_version
```

Optional lineage index fields may include:

```text
parent_process_ref
operator_response_ref
continuity_result_ref
trajectory_ref
source_ref
target_ref
```

The canonical payload remains the source representation of the Runtime object.
Indexed columns are query aids and must not silently replace or change payload semantics.

---

## 7. G-3 — Initial Storage Technology

The first persistent implementation should use:

```text
SQLite
```

Reasons:

```text
single-file local operation
transaction support
low operational complexity
suitable for bounded prototype tests
portable across local and CI environments
```

SQLite is an implementation choice for Priority G.
It is not part of Gyro Logic and is not a permanent architectural commitment.

---

## 8. G-4 — Atomic Publication

The current in-memory publication relation must be preserved:

```text
complete valid result group
→ one atomic publication
```

The persistent transaction must include, when generated:

```text
LoopStepResult / Process record
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
idempotency record
current-scope update
```

Failure rule:

```text
any required write fails
→ rollback complete transaction
→ no completed Process becomes visible
```

A partially published Process must not be returned as successful.

---

## 9. Query Endpoint Direction

Priority G should implement the supporting endpoints deferred in Priority E.

### 9.1 Current scope

```text
GET /loop/state/{loop_id}
```

Returns the current-scope view only.

```text
current scope
≠ complete history
```

### 9.2 Process history

```text
GET /loop/history/{loop_id}
```

Returns ordered Process references and bounded summaries.
It must support pagination.

### 9.3 Trajectory

```text
GET /trajectory/{trajectory_id}
```

Returns explicit TrajectoryEdge records and branch relations.
It must preserve:

```text
RESLICE lineage
JUMP reconnection
DEFER pending relation
STOP current-scope termination
```

### 9.4 Memory record

The existing endpoint remains:

```text
GET /memory/record/{record_id}
```

The persistent implementation must reconstruct the canonical record type rather than return an untyped dictionary when type information is available.

---

## 10. Restart and Recovery Requirements

Priority G must demonstrate:

```text
create Process
→ stop application/store instance
→ create new store instance using same database
→ retrieve Process and records by identity
→ preserve current-scope pointer
→ preserve idempotent replay behavior
```

Required recovery scenarios include:

```text
NORMAL / CONTINUE Process survives restart
VOID / DEFER and DeferredRelationRecord survive restart
RESLICE preparation lineage survives restart
TrajectoryEdge remains queryable
same idempotency key and digest returns original Process after restart
```

---

## 11. Security and Data Boundaries

Priority G does not yet implement production authentication or multi-tenant authorization.

However, it must avoid:

```text
arbitrary SQL construction from request values
unsafe record-type deserialization
implicit object execution during reconstruction
unbounded history queries
silent schema downgrade
```

All database operations should use parameterized queries.
All reconstructed records must pass canonical Pydantic validation.

---

## 12. Non-goals

Priority G does not yet include:

```text
PostgreSQL
multi-node replication
distributed transactions
background autonomous processing
streaming or WebSocket APIs
production observability stack
GyroAuth integration
UI dashboard
performance optimization beyond bounded tests
record deletion policy
```

These remain later priorities.

---

## 13. Acceptance Criteria

Priority G is complete when:

```text
repository contract is storage-independent
SQLite implementation passes canonical tests
complete result groups publish transactionally
idempotency survives restart
current scope survives restart
Process history is queryable
TrajectoryEdge history is queryable
canonical records reconstruct by explicit identity
missing records remain API errors, not Runtime VOID
restart and recovery tests pass in GitHub Actions
cross-document review finds no responsibility collapse
```

---

## 14. Initial Decision

```text
Priority G
= Persistent Runtime State and Query API

Status
= STARTED

G-1 direction
= ACCEPTED FOR DESIGN
```

The first implementation step should be **G-1: Persistence Boundary and Repository Contract**.
