# 71. Priority G-6 — Process History Query Endpoint

---

## 1. Purpose

This document defines and records the implementation of **G-6: Process History Query Endpoint**.

G-5 exposed only the explicit current-scope Process.
G-6 exposes the immutable completed Process sequence for one explicit `loop_id` without changing current scope or executing a new Process.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

History is a Runtime observation surface.
It does not select OperatorResponse, reconstruct an implicit latest Process, or alter canonical Runtime records.

---

## 2. Endpoint

```text
GET /loop/history/{loop_id}
```

Query parameters:

```text
limit  = integer, default 20, minimum 1, maximum 100
cursor = optional opaque-to-client offset cursor
```

The endpoint requires an explicit `loop_id`.
It does not aggregate unrelated loops or infer a global current history.

---

## 3. Response Models

Added canonical query models:

```text
ProcessHistoryItem
ProcessHistoryPage
```

`ProcessHistoryItem` contains a bounded summary:

```text
process_id
request_id
loop_id
completed_at
stability_status
stability_value
operator_response
continuity_type
```

`ProcessHistoryPage` contains:

```text
loop_id
items
limit
next_cursor
```

The history endpoint intentionally returns summaries rather than duplicating every complete `LoopStepResult` in the page.
A complete Process remains retrievable by explicit `process_id`.

---

## 4. Ordering Contract

Canonical initial ordering is:

```text
publication order ascending
```

For `InMemoryStore`, this is the append order recorded during successful publication.

For `SQLiteStore`, only `LoopStepResult` rows for the explicit `loop_id` are selected and ordered by committed insertion order.

The endpoint must not order by:

```text
random identity
client request lexical order
current-scope pointer
Stability value
OperatorResponse type
```

Current scope and history remain separate:

```text
current scope
≠ final item inferred by the client
≠ complete history
```

---

## 5. Pagination Contract

The first implementation uses a non-negative integer offset serialized as a string cursor.

Example:

```text
first request:  limit=2, cursor absent
first response: next_cursor="2"
second request: limit=2, cursor="2"
```

Rules:

```text
cursor absent
→ offset 0

valid non-negative integer cursor
→ begin at that offset

invalid or negative cursor
→ HTTP 422 structured ApiError
```

The API exposes the cursor as a string so a future implementation may replace the internal representation without changing the response field.

No unbounded history query is allowed.

---

## 6. Empty History Behavior

When no completed Process exists for the explicit `loop_id`:

```text
HTTP 200
items = []
next_cursor = null
```

An empty history is not an API not-found error because the query scope is valid and the bounded result set is empty.

It must not become:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
StabilityStatus.NOT_EVALUABLE
```

---

## 7. Invalid Query Behavior

Invalid cursor behavior:

```text
HTTP 422
error_code = GYRO_API_VALIDATION_HISTORY_CURSOR
category = VALIDATION
phase = PROCESS_HISTORY_QUERY
```

FastAPI validates the bounded `limit` range:

```text
1 <= limit <= 100
```

Repository integrity failures during reconstruction remain:

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_INTEGRITY
category = REPOSITORY
phase = PROCESS_HISTORY_QUERY
```

Repository failure is not a Runtime result.

---

## 8. Repository Implementations

### 8.1 InMemoryStore

Added:

```text
process_history: dict[loop_id, list[process_id]]
list_process_history(...)
```

Only a successful new publication appends one `process_id`.
Idempotent replay does not append a second history item.

### 8.2 SQLiteStore

Added:

```text
list_process_history(...)
```

The query selects:

```text
loop_id = explicit loop scope
record_type = LoopStepResult
bounded LIMIT + OFFSET
```

Every row passes the existing canonical checks:

```text
schema version
canonical digest
closed type registry
Pydantic validation
```

History survives store and application restart because it is reconstructed from committed persistent records.

---

## 9. Implemented Files

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
GET /loop/history/{loop_id}
```

---

## 10. Tests

API tests verify:

```text
ascending publication order
bounded summary fields
limit and next_cursor behavior
second-page continuation
empty history returns HTTP 200 with empty items
invalid cursor returns structured HTTP 422
idempotent replay does not duplicate history
```

SQLite tests verify:

```text
history survives repository restart
ascending Process order is preserved
pagination survives restart
unknown loop returns empty page
invalid cursor is rejected
```

GitHub Actions verification:

```text
run_id = 30073474793
job_id = 89419069605
conclusion = success
```

The bounded API, PoC, and SQLite repository test step completed successfully.

---

## 11. Responsibility Review

The accepted responsibility chain is:

```text
ProcessExecutor
→ creates and publishes one bounded Process

RuntimeRepository
→ preserves immutable Process records and their publication sequence

GET /loop/history/{loop_id}
→ returns a bounded ordered summary page
```

The endpoint does not:

```text
execute Slice
calculate Stability
select OperatorResponse
change current scope
repair missing records
infer an implicit latest Process
collapse history into current state
```

---

## 12. G-6 Decision

```text
G-6 Process History Query Endpoint
= COMPLETE

InMemoryStore history support
= VERIFIED

SQLiteStore persistent history support
= VERIFIED

Bounded cursor pagination
= VERIFIED

Current scope / history separation
= ACCEPTED

GitHub Actions execution verification
= PASS
```

The next Priority G step is:

```text
G-7 Trajectory Query Endpoint
```