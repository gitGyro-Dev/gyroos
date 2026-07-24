# 79. Priority H-3 — Request Size, Rate, and Resource Limits

---

## 1. Purpose

H-3 introduces bounded admission controls for the GyroOS Runtime API.

The purpose is to prevent one caller or one malformed request from consuming unbounded request-body, request-rate, or concurrent execution capacity.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Admission control decides whether an HTTP request may enter the Runtime API. It does not evaluate Stability, select OperatorResponse, or create canonical records.

---

## 2. Configuration Contract

Added environment variables:

```text
GYROOS_MAX_REQUEST_BODY_BYTES
GYROOS_RATE_LIMIT_REQUESTS
GYROOS_RATE_LIMIT_WINDOW_SECONDS
GYROOS_MAX_CONCURRENT_REQUESTS
```

Defaults:

```text
max request body       = 1,048,576 bytes
rate limit             = 120 requests
rate window            = 60 seconds
max concurrent requests = 32
```

All values must be positive integers.

Request payloads cannot override these settings.

---

## 3. Middleware Boundary

Added:

```text
app/resource_limits.py
```

Primary components:

```text
FixedWindowRateLimiter
ResourceLimitMiddleware
```

The middleware is applied to the FastAPI application before protected Runtime endpoints execute.

Public health monitoring remains excluded:

```text
GET /health
```

All other HTTP endpoints pass through request admission control.

---

## 4. Request Body Limit

When `Content-Length` exceeds the configured body limit:

```text
HTTP 413 Payload Too Large
error_code = GYRO_API_REQUEST_TOO_LARGE
category = RESOURCE_LIMIT
phase = REQUEST_ADMISSION
```

The request is rejected before authentication, validation, Process execution, or repository access.

The current bounded implementation uses the declared `Content-Length` header. Streaming body enforcement and reverse-proxy enforcement remain deferred.

---

## 5. Rate Limit

The initial limiter is an in-process fixed-window limiter keyed by client host.

When the configured number of requests is exhausted within the window:

```text
HTTP 429 Too Many Requests
error_code = GYRO_API_RATE_LIMITED
category = RESOURCE_LIMIT
phase = REQUEST_ADMISSION
Retry-After = remaining bounded window seconds
```

Old entries expire when the configured time window passes.

The limiter does not alter Process identity, idempotency keys, current scope, history, or trajectory.

---

## 6. Concurrent Request Limit

The middleware uses an asynchronous semaphore bounded by:

```text
GYROOS_MAX_CONCURRENT_REQUESTS
```

When no execution slot is immediately available:

```text
HTTP 503 Service Unavailable
error_code = GYRO_API_CONCURRENCY_LIMIT
category = RESOURCE_LIMIT
phase = REQUEST_ADMISSION
Retry-After = 1
```

The rejected request does not execute a partial Process and does not publish records.

---

## 7. Error Separation

H-3 admission failures are transport and hosting outcomes.

They are not converted into:

```text
BoundaryState.VOID
VoidEvidence
StabilityStatus.NOT_EVALUABLE
OperatorResponse.DEFER
OperatorResponse.STOP
RuntimeContinuityResult
```

No admission failure becomes part of canonical Runtime memory.

---

## 8. Implemented Files

Added:

```text
app/resource_limits.py
tests/test_resource_limits.py
docs/79_priority_h3_request_size_rate_and_resource_limits.md
```

Updated:

```text
app/settings.py
app/main.py
tests/test_runtime_settings.py
.github/workflows/priority-f-poc.yml
```

---

## 9. Test Coverage

Settings tests verify:

```text
safe default values
explicit production-compatible values
non-positive body limit rejection
non-positive rate count rejection
non-positive rate window rejection
non-positive concurrency limit rejection
```

Resource-limit tests verify:

```text
oversized request returns HTTP 413
bounded request reaches endpoint
rate exhaustion returns HTTP 429
Retry-After is present
health remains excluded
fixed-window entries expire
```

GitHub Actions run `30091152703` completed successfully. The workflow executed the bounded Runtime, production-hardening, and PoC artifact steps without failure.

---

## 10. Deferred Resource-Control Work

H-3 does not yet implement:

```text
distributed rate limiting
principal-aware rate limiting
per-endpoint quotas
streaming body byte counting
reverse-proxy configuration
persistent rate counters
adaptive load shedding
queueing policy
CPU or memory quotas
request execution timeout
```

Multi-process deployments require a shared limiter or external gateway before public production exposure.

---

## 11. Responsibility Review

```text
RuntimeSettings
→ defines bounded deployment limits

ResourceLimitMiddleware
→ performs HTTP admission control

Authentication boundary
→ validates admitted caller credentials

Runtime endpoints
→ retain Process and repository responsibilities
```

Resource controls do not become Gyro Logic definitions or OperatorResponse policy.

---

## 12. H-3 Decision

```text
H-3 Request Size, Rate, and Resource Limits
= COMPLETE

Request body limit
= COMPLETE

Fixed-window rate limit
= COMPLETE

Concurrent request limit
= COMPLETE

Public health exclusion
= COMPLETE

GitHub Actions execution verification
= COMPLETE
```

The next Priority H step is:

```text
H-4 Concurrency and SQLite Locking
```
