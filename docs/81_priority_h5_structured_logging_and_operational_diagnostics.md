# 81. Priority H-5 — Structured Logging and Operational Diagnostics

---

## 1. Purpose

H-5 introduces one bounded operational-observability boundary for the GyroOS Runtime API.

The purpose is to make request flow, response status, execution duration, and correlation identity observable without exposing credentials, request payloads, database paths, or canonical Runtime contents.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Operational logging observes hosting behavior. It does not evaluate Stability, select OperatorResponse, mutate Process identity, or publish canonical records.

---

## 2. Configuration Contract

Added environment variables:

```text
GYROOS_LOG_LEVEL
GYROOS_JSON_LOGGING
```

Supported log levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Defaults:

```text
development → DEBUG
test        → INFO
production  → INFO
JSON logging → enabled
```

Production startup rejects:

```text
GYROOS_JSON_LOGGING=false
```

This keeps machine-readable operational output mandatory in production.

---

## 3. Structured Log Format

Added:

```text
app/observability.py
```

Primary components:

```text
JsonFormatter
configure_logging(...)
RequestDiagnosticsMiddleware
```

Request completion logs contain bounded fields:

```text
timestamp
level
logger
event
request_id
method
path
status_code
duration_ms
client_host
```

The JSON formatter may also carry bounded error metadata when explicitly supplied:

```text
error_code
retryable
```

---

## 4. Request Correlation

The diagnostics middleware accepts:

```text
X-Request-ID
```

When a non-empty value is supplied, the first 128 characters are preserved.

When no value is supplied, GyroOS generates:

```text
req_<uuid hex>
```

Every HTTP response receives:

```text
X-Request-ID: <correlation id>
```

The same request ID is placed into the request-completion log.

This transport correlation ID remains separate from canonical Gyro Process `request_id`.

---

## 5. Middleware Boundary

`RequestDiagnosticsMiddleware` is the outer HTTP diagnostics boundary.

It observes responses produced by:

```text
resource admission control
authentication
request validation
Runtime execution
repository access
health endpoint
```

Successful responses log at `INFO`.

HTTP responses with status code 400 or greater log at `WARNING`.

Unhandled exceptions log `request_failed` at exception level and are re-raised to the existing FastAPI error boundary.

---

## 6. Sensitive Information Exclusion

The H-5 request logger does not record:

```text
Authorization header
bearer token
API bearer-token setting
request body
response body
database path
canonical record payload
filesystem details
```

The logger records route paths but not query-string values.

This is an explicit minimum disclosure boundary. Future logging additions must preserve the same rule unless a separately reviewed redaction contract is introduced.

---

## 7. Implemented Files

Added:

```text
app/observability.py
tests/test_observability.py
docs/81_priority_h5_structured_logging_and_operational_diagnostics.md
```

Updated:

```text
app/settings.py
app/main.py
tests/test_runtime_settings.py
.github/workflows/priority-f-poc.yml
```

---

## 8. Test Coverage

Settings tests verify:

```text
development/test log-level defaults
explicit production log level
invalid log-level rejection
invalid JSON-logging boolean rejection
production non-JSON logging rejection
```

Observability tests verify:

```text
request ID generation
supplied request ID preservation
X-Request-ID response header
structured JSON fields
request completion diagnostics
secret and database-path exclusion
```

The workflow executes the H-5 observability test file.

---

## 9. Deferred Observability Work

H-5 does not yet implement:

```text
OpenTelemetry traces
metrics endpoint
Prometheus counters
distributed trace propagation
log shipping configuration
external SIEM integration
log sampling
log rotation
persistent audit log
principal identity logging
canonical Runtime event stream
```

Audit events and general operational logs remain separate concerns.

---

## 10. Responsibility Review

```text
RuntimeSettings
→ defines logging mode and minimum level

configure_logging
→ installs the process logging formatter and handler

RequestDiagnosticsMiddleware
→ assigns transport correlation and records bounded request outcomes

Runtime endpoints
→ retain Process and repository responsibilities
```

Transport request IDs and operational logs do not become part of canonical Process memory, trajectory, Stability, or OperatorResponse.

---

## 11. H-5 Decision

```text
H-5 Structured Logging and Operational Diagnostics
= COMPLETE

JSON structured logging
= IMPLEMENTED

Request correlation
= IMPLEMENTED

Response correlation header
= IMPLEMENTED

Sensitive-field exclusion
= IMPLEMENTED

GitHub Actions execution verification
= PASSED
```

Verified by GitHub Actions run:

```text
30091681637
```

The next Priority H step is:

```text
H-6 Schema Migration and Compatibility
```
