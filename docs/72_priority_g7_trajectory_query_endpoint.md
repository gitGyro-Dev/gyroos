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

## 3. Initial Query Identity

The current canonical `TrajectoryEdge` model contains:

```text
trajectory_edge_id
process_id
operator_response_ref
continuity_result_ref
edge_type
source_ref
target_ref
parent_process_ref
created_at
metadata
```

Priority G-7 does not add a new synthetic trajectory identifier.
The initial query key is an explicit relation reference matching one of:

```text
source_ref
target_ref
parent_process_ref
```

Canonical match rule:

```text
trajectory_ref equals one explicit edge relation field
→ edge belongs to the bounded query result
```

The repository does not derive semantic similarity, infer hidden branches, or merge unrelated references.

---

## 4. Response Model

Added:

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

The endpoint preserves the canonical edge payload including:

```text
RESLICE_CONNECTION
JUMP_RECONNECTION
DEFERRED_PENDING_RELATION
STOPPED_FOR_CURRENT_SCOPE
DIRECT_CONNECTION
ADJUSTED_CONNECTION
```

It does not convert these edge types into new Runtime outcomes.

---

## 5. Ordering Contract

Canonical initial ordering is:

```text
publication order ascending
```

For `InMemoryStore`, successful publication appends each `trajectory_edge_id` to an immutable in-memory order list.

For `SQLiteStore`, committed `TrajectoryEdge` rows are reconstructed in insertion order.

Ordering is not based on:

```text
edge type
Stability value
current-scope pointer
lexical record identity
query relation field priority
```

---

## 6. Pagination Contract

G-7 uses the same bounded cursor form as G-6:

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

Example:

```text
GET /trajectory/relation_001?limit=2
→ next_cursor="2"

GET /trajectory/relation_001?limit=2&cursor=2
→ next matching page
```

---

## 7. Empty Result Behavior

When no `TrajectoryEdge` matches the explicit reference:

```text
HTTP 200
items = []
next_cursor = null
```

An empty trajectory query is not:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
StabilityStatus.NOT_EVALUABLE
API not-found error
```

It is a valid query with an empty bounded result set.

---

## 8. Invalid Query and Integrity Behavior

Invalid cursor:

```text
HTTP 422
error_code = GYRO_API_VALIDATION_TRAJECTORY_CURSOR
category = VALIDATION
phase = TRAJECTORY_QUERY
```

Repository reconstruction or digest integrity failure:

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_INTEGRITY
category = REPOSITORY
phase = TRAJECTORY_QUERY
```

Repository failure remains separate from Runtime continuity meaning.

---

## 9. Repository Implementations

### 9.1 InMemoryStore

Added:

```text
trajectory_history: list[trajectory_edge_id]
list_trajectory_edges(...)
```

Successful publication appends generated trajectory edges once.
Idempotent replay does not append duplicate edges because no new publication occurs.

### 9.2 SQLiteStore

Added:

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

The first SQLite implementation reconstructs the bounded edge set before matching.
Later optimization may add indexed relation columns without changing canonical payload authority.

---

## 10. Implemented Files

Updated:

```text
app/models.py
app/repositories.py
app/sqlite_repository.py
app/main.py
tests/test_bounded_api.py
tests/test_sqlite_repository.py
```

Added endpoint:

```text
GET /trajectory/{trajectory_ref}
```

---

## 11. Tests

API tests verify:

```text
matching source_ref edges are returned
publication order is preserved
complete TrajectoryEdge payload is returned
bounded pagination and next_cursor
empty query returns HTTP 200 with empty items
invalid cursor returns structured HTTP 422
idempotent replay does not duplicate trajectory history
```

SQLite tests verify:

```text
trajectory edges survive repository restart
publication order survives restart
pagination survives restart
unknown relation returns empty page
invalid cursor is rejected
```

The existing GitHub Actions workflow runs both affected test files.

---

## 12. Responsibility Review

Accepted chain:

```text
ProcessExecutor
→ creates one complete bounded result group

ContinuityBuilder
→ creates RuntimeContinuityResult

ProcessExecutor publication assembly
→ creates canonical TrajectoryEdge

RuntimeRepository
→ preserves and returns committed typed edges

GET /trajectory/{trajectory_ref}
→ returns a bounded explicit-reference edge page
```

The endpoint must not:

```text
select OperatorResponse
change edge_type
create inferred edges
resolve pending DeferredRelationRecord
execute RESLICE
perform JUMP
terminate current scope
collapse trajectory into current state
```

---

## 13. G-7 Decision

```text
G-7 Trajectory Query Endpoint
= IMPLEMENTED

Explicit relation-reference matching
= IMPLEMENTED

InMemoryStore trajectory query
= IMPLEMENTED

SQLiteStore persistent trajectory query
= IMPLEMENTED

Bounded pagination
= IMPLEMENTED

GitHub Actions execution verification
= PENDING
```

After the updated workflow passes, G-7 may be marked:

```text
G-7
= COMPLETE
```

The next Priority G step is:

```text
G-8 Memory Record Retrieval and Type-safe Reconstruction
```
