# 70. Priority G-5 — Current-scope Query Endpoint

---

## 1. Purpose

This document defines and records the implementation of **G-5: Current-scope Query Endpoint**.

G-4 completed atomic publication and durable idempotency protection.
G-5 exposes the current committed Process for one explicit `loop_id` without collapsing or replacing complete Process history.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The endpoint is a Runtime query surface.
It does not execute a new Process, calculate Stability, or select OperatorResponse.

---

## 2. Endpoint

```text
GET /loop/state/{loop_id}
```

The endpoint requires an explicit `loop_id`.
It does not infer a loop, choose the most recent loop globally, or fall back to an unrelated Process.

Canonical lookup relation:

```text
loop_id
→ current-scope process_id
→ complete LoopStepResult
```

---

## 3. Response Model

The canonical response model is:

```text
CurrentScopeState
```

Fields:

```text
loop_id
current_process_id
process
```

Where:

```text
process
= complete typed LoopStepResult
```

The response does not return an untyped storage row or a partially reconstructed Process.

---

## 4. Current Scope and History Separation

The endpoint returns only the explicit current-scope pointer and its referenced Process.

```text
current scope
≠ complete Process history
```

A successful publication performs both:

```text
append immutable completed Process
+
update current-scope pointer
```

The pointer update does not delete, overwrite, or hide previous Process records.
History retrieval remains G-6.

---

## 5. Success Behavior

When the current-scope pointer and referenced Process both exist:

```text
HTTP 200
```

Response:

```json
{
  "loop_id": "loop_001",
  "current_process_id": "process_...",
  "process": {
    "process_id": "process_..."
  }
}
```

The full `LoopStepResult` is returned under `process`.

---

## 6. Missing Scope Behavior

When no current-scope pointer exists for the explicit `loop_id`:

```text
HTTP 404
error_code = GYRO_API_NOT_FOUND_CURRENT_SCOPE
category = NOT_FOUND
phase = CURRENT_SCOPE_QUERY
```

Missing scope is an API not-found condition.
It is not converted into:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
StabilityStatus.NOT_EVALUABLE
```

---

## 7. Broken Pointer Behavior

When a current-scope pointer exists but references a missing Process:

```text
HTTP 500
error_code = GYRO_API_REPOSITORY_INTEGRITY
category = REPOSITORY
phase = CURRENT_SCOPE_QUERY
```

This state is a repository integrity failure.
It must not be silently treated as an absent scope or a Runtime result.

```text
broken current-scope pointer
≠ not found scope
≠ VOID
≠ DEFER
≠ STOP
```

---

## 8. Implemented Files

Updated:

```text
app/models.py
app/main.py
tests/test_bounded_api.py
```

Added model:

```text
CurrentScopeState
```

Added endpoint:

```text
GET /loop/state/{loop_id}
```

---

## 9. Tests

The bounded API tests verify:

```text
current-scope endpoint returns explicit loop_id
current-scope endpoint returns the pointer process_id
returned Process identity equals current_process_id
missing current scope returns structured 404 ApiError
broken current-scope pointer returns repository integrity 500
query does not execute a new Process
```

GitHub Actions run:

```text
run_id = 30072730648
job_id = 89416797764
conclusion = success
```

The job completed the bounded API, PoC, and SQLite repository test step successfully.

---

## 10. Responsibility Review

The responsibility chain remains:

```text
ProcessExecutor
→ executes and publishes one bounded Process

RuntimeRepository
→ preserves current-scope pointer and Process

GET /loop/state/{loop_id}
→ reads the explicit pointer and returns its typed Process
```

The endpoint does not become:

```text
Loop Controller
Stability evaluator
history selector
implicit latest resolver
recovery mechanism
```

---

## 11. G-5 Decision

```text
G-5 Current-scope Query Endpoint
= COMPLETE

Current scope / history separation
= ACCEPTED

Structured missing-scope behavior
= VERIFIED

Broken-pointer integrity behavior
= VERIFIED

GitHub Actions execution verification
= PASS
```

The next Priority G step is:

```text
G-6 Process History Query Endpoint
```
