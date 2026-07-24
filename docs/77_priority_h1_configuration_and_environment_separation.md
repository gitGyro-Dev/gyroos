# 77. Priority H-1 — Configuration and Environment Separation

---

## 1. Purpose

H-1 introduces one typed configuration boundary for the bounded GyroOS Runtime.

The purpose is to prevent deployment behavior from being scattered across module constants, request payloads, developer-local assumptions, and implicit environment state.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Configuration selects how the Runtime is hosted and connected to storage. It does not select OperatorResponse and does not alter canonical Process meaning.

---

## 2. Implemented Configuration Model

Added:

```text
app/settings.py
```

Primary types:

```text
RuntimeEnvironment
RuntimeSettings
```

Supported profiles:

```text
development
test
production
```

The settings object is immutable after construction.

---

## 3. Environment Variable Contract

```text
GYROOS_ENV
GYROOS_DATABASE_PATH
GYROOS_HOST
GYROOS_PORT
GYROOS_DEBUG
GYROOS_SQLITE_TIMEOUT_SECONDS
```

Precedence:

```text
explicit environment variable
→ profile default
→ safe code default
```

Request bodies cannot override these settings.

---

## 4. Profile Defaults

### Development

```text
GYROOS_ENV = development
database_path = runtime.db
host = 127.0.0.1
port = 8000
debug = true
sqlite timeout = 5.0 seconds
```

### Test

```text
GYROOS_ENV = test
database_path = .runtime-test.db
host = 127.0.0.1
port = 8000
debug = false
sqlite timeout = 5.0 seconds
```

### Production

Production has no implicit database path.

Required:

```text
GYROOS_ENV=production
GYROOS_DATABASE_PATH=<explicit persistent path>
GYROOS_DEBUG=false
```

Host, port, and SQLite timeout may be explicitly supplied.

---

## 5. Startup Validation

The following configuration fails during settings construction:

```text
unknown GYROOS_ENV
empty GYROOS_HOST
port outside 1..65535
non-integer port
invalid boolean text
non-numeric SQLite timeout
non-positive SQLite timeout
production without database path
production with debug enabled
```

These are startup and deployment failures.

They are not translated into Runtime outcomes such as:

```text
BoundaryState.VOID
VoidEvidence
StabilityStatus.NOT_EVALUABLE
OperatorResponse.DEFER
OperatorResponse.STOP
```

---

## 6. SQLite Configuration

`SQLiteStore` now accepts:

```text
timeout_seconds
```

The constructor validates:

```text
timeout_seconds > 0
```

Every SQLite connection uses the configured timeout.

Existing callers remain compatible through the default:

```text
5.0 seconds
```

The stored runtime version for new publications is now:

```text
priority-h1
```

This records the implementation generation without changing the schema version.

---

## 7. Application Surface

FastAPI receives:

```text
debug = settings.debug
```

The health endpoint exposes only non-secret profile information:

```json
{
  "status": "ok",
  "runtime": "bounded",
  "version": "0.1.0",
  "environment": "development"
}
```

It does not expose:

```text
database path
secret values
filesystem details
connection credentials
```

---

## 8. Implemented Files

Added:

```text
app/settings.py
tests/test_runtime_settings.py
docs/77_priority_h1_configuration_and_environment_separation.md
```

Updated:

```text
app/main.py
app/sqlite_repository.py
.github/workflows/priority-f-poc.yml
```

---

## 9. Test Coverage

The H-1 test file verifies:

```text
development defaults
test database isolation default
production database requirement
production debug rejection
valid production configuration
unknown environment rejection
invalid port rejection
invalid boolean rejection
invalid timeout rejection
SQLiteStore timeout propagation
SQLiteStore non-positive timeout rejection
```

The existing API test verifies the health endpoint remains available. The workflow now includes the H-1 test file.

---

## 10. Verification

GitHub Actions run:

```text
run_id = 30084358480
job_id = 89452952024
conclusion = success
```

Verified:

```text
typed environment profile parsing
production fail-fast validation
SQLite timeout propagation
health endpoint environment reporting
all bounded Runtime and production-hardening tests pass
```

---

## 11. Deferred Configuration Work

H-1 does not yet implement:

```text
secret manager integration
configuration file loading
container deployment manifests
TLS configuration
authentication keys
rate-limit configuration
logging configuration
migration configuration
```

These belong to later Priority H steps.

---

## 12. Responsibility Review

```text
RuntimeSettings
→ parses and validates deployment configuration

SQLiteStore
→ consumes bounded storage connection settings

FastAPI application
→ consumes non-semantic hosting settings

Gyro Process request
→ remains unable to mutate server configuration
```

No configuration value becomes part of the invariant Core.

---

## 13. H-1 Decision

```text
H-1 Configuration and Environment Separation
= COMPLETE

Typed environment profiles
= VERIFIED

Production startup validation
= VERIFIED

SQLite timeout configuration
= VERIFIED

Non-secret health environment reporting
= VERIFIED

GitHub Actions execution verification
= PASS
```

The next Priority H step is:

```text
H-2 Authentication and Authorization Boundary
```
