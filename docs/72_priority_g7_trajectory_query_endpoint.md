# 72. Priority G-7 — Trajectory Query Endpoint

---

## 1. Purpose

This document defines and records the implementation of **G-7: Trajectory Query Endpoint**.

G-6 exposed ordered Process history for one explicit `loop_id`.
G-7 exposes committed `TrajectoryEdge` records for one explicit Runtime relation reference without reinterpreting or rebuilding the trajectory.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Trajectory query is a Runtime observation surface.
It does not execute Slice, evaluate Stability, select OperatorResponse, or create new branch relations.

---

## 2. Endpoint

```text
GET /trajectory/{trajectory_ref}
```

Query parameters:

```text
limit  = integer, default 20, minimum 1, maximum 100
cursor = optional offset cursor
```

The endpoint requires an explicit `trajectory_ref`.
It does not infer a global trajectory or select a latest relation.

---

## 3. Query Identity

The canonical `TrajectoryEdge` model contains:

```text
trajectory_edge_id
process_id
operator_response_ref
continuity_result_ref
edge_type
relation_ref
source_ref
target_ref
parent_process_ref
created_at
metadata
```

The query key matches one explicit edge relation field:

```text
relation_ref
source_ref
target_ref
parent_process_ref
```

Canonical match rule:

```text
trajectory_ref equals one explicit edge relation field
→ edge belongs to the bounded query result
```

`relation_ref` preserves the observed Runtime relation from `Structure.current_mode.relation_ref`.
`source_ref` remains the Slice input source and is not overwritten by the relation query key.

The repository does not derive semantic similarity, infer hidden branches, or merge unrelated references.

---

## 4. Response Model

```text
TrajectoryEdgePage
```

Fields:

```text
trajectory_ref
items
limit
next_cursor
```

`items` contains complete typed `TrajectoryEdge` records.
The endpoint preserves canonical edge payload and does not convert continuity types into new Runtime outcomes.

---

## 5. Ordering and Pagination

Canonical ordering is successful publication order ascending.
The bounded cursor contract is:

```text
cursor absent
→ offset 0

valid non-negative integer string
→ begin at that matching-edge offset

invalid or negative cursor
→ HTTP 422
```

The query is bounded by:

```text
1 <= limit <= 100
```

---

## 6. Empty and Error Behavior

No matching edge:

```text
HTTP 200
items = []
next_cursor = null
```

Invalid cursor:

```text
HTTP 422
error_code = GYRO_API_VALIDATION_TRAJECTORY_CURSOR
category = VALIDATION
phase = TRAJECTORY_QUERY
```

Repository reconstruction or digest failure:

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_INTEGRITY
category = REPOSITORY
phase = TRAJECTORY_QUERY
```

These conditions are not Runtime responses such as VOID, DEFER, or STOP.

---

## 7. Repository Implementations

### 7.1 InMemoryStore

```text
trajectory_history: list[trajectory_edge_id]
list_trajectory_edges(...)
```

Successful publication appends generated trajectory edges once.
Idempotent replay does not append duplicate edges.

### 7.2 SQLiteStore

```text
list_trajectory_edges(...)
```

The implementation:

```text
selects committed TrajectoryEdge rows
→ verifies schema and digest
→ reconstructs typed TrajectoryEdge
→ applies exact explicit-reference matching
→ returns bounded publication-order page
```

---

## 8. Implemented Files

```text
app/models.py
app/runtime.py
app/repositories.py
app/sqlite_repository.py
app/main.py
tests/test_bounded_api.py
tests/test_sqlite_repository.py
```

Endpoint:

```text
GET /trajectory/{trajectory_ref}
```

---

## 9. Verification

GitHub Actions run:

```text
run_id = 30075166381
job_id = 89424208222
conclusion = success
```

Verified:

```text
explicit relation_ref matching
source_ref semantic preservation
publication ordering
bounded pagination
empty result behavior
invalid cursor behavior
idempotent replay non-duplication
SQLite restart-safe retrieval
all bounded API, PoC, and SQLite tests pass
```

---

## 10. Responsibility Review

```text
ProcessExecutor
→ creates one complete bounded result group and canonical TrajectoryEdge

RuntimeRepository
→ preserves and returns committed typed edges

GET /trajectory/{trajectory_ref}
→ returns a bounded explicit-reference edge page
```

The endpoint does not select OperatorResponse, change edge type, create inferred edges, resolve pending relations, execute RESLICE, perform JUMP, or change current scope.

---

## 11. G-7 Decision

```text
G-7 Trajectory Query Endpoint
= COMPLETE

Explicit relation-reference matching
= VERIFIED

InMemoryStore trajectory query
= VERIFIED

SQLiteStore persistent trajectory query
= VERIFIED

Bounded pagination
= VERIFIED

GitHub Actions execution verification
= PASS
```

The next Priority G step is:

```text
G-8 Memory Record Retrieval and Type-safe Reconstruction
```
