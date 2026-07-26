# 130. vNext Public Experimental API Minimal PoC

---

## 1. Purpose

This document records implementation of integration gate C initial scope:

```text
C1. experimental API settings and public models
C2. repository dependency / provider boundary
C3. experimental record routes
```

The API exposes only opaque experimental record CRUD under:

```text
/vnext/experimental
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. C1 Settings and Public Models

Added:

```text
app/vnext/experimental_api.py
```

Components:

```text
ExperimentalApiSettings
ExperimentalApiModel
ExperimentalRecordCreateRequest
ExperimentalRecordResponse
ExperimentalRecordListResponse
ExperimentalApiError
```

Resource limits:

```text
maximum payload bytes
maximum metadata bytes
maximum list result count
maximum record ID length
maximum record type length
```

The transport converts create requests only to:

```text
ExperimentalRecordEnvelope
```

---

## 3. C2 Provider Boundary

Added:

```text
app/vnext/experimental_api_provider.py
```

Components:

```text
ExperimentalRepositoryProvider
experimental_repository_provider
get_experimental_repository
```

The provider exposes:

```text
ExperimentalRecordRepository
```

The initial backend is:

```text
InMemoryExperimentalRecordRepository
```

The JSON artifact repository is not selected by default.

---

## 4. C3 Routes

Added:

```text
app/vnext/experimental_api_routes.py
```

Routes:

```text
POST   /vnext/experimental/records
GET    /vnext/experimental/records/{record_id}
GET    /vnext/experimental/records
DELETE /vnext/experimental/records/{record_id}
```

The router reuses the existing bearer dependency but does not call Runtime execution.

---

## 5. Main Application Integration

Updated:

```text
app/main.py
```

Only router registration was added:

```text
app.include_router(experimental_api_router)
```

Existing bounded Runtime routes remain present and unchanged in behavior.

---

## 6. API Semantics

The API supports:

```text
opaque envelope creation
record ID retrieval
process_id filtering
record_type filtering
bounded list result count
delete by record ID
explicit not-found errors
```

The API does not support:

```text
current/latest selection
canonical authority
version progression
semantic ordering
Trajectory ordering
typed reconstruction
assembly execution
Runtime projection execution
JSON backend selection
GyroAuth mapping
```

List responses state:

```text
ordering = UNSPECIFIED
```

---

## 7. Tests

Added:

```text
tests/vnext/test_experimental_api_models.py
tests/vnext/test_experimental_api_provider.py
tests/vnext/test_experimental_api_routes.py
```

Coverage includes:

```text
resource settings validation
opaque envelope conversion
extra/canonical field rejection
payload and metadata limits
provider contract dependency
explicit backend replacement
CRUD round trip
filter behavior
list bounding
explicit 404 errors
existing /loop/step route registration
```

The Priority F workflow includes all three test files.

---

## 8. Isolation Boundary

Unchanged:

```text
POST /loop/step behavior
ProcessExecutor
StabilityEngine
OperatorResponse selection
current SQLite schema
JSON artifact backend selection
Semantic assembly routes
Readability assembly routes
Continuity assembly routes
Trajectory assembly routes
Runtime projection routes
GyroAuth consumption
```

---

## 9. Current Decision

```text
C1 settings and public models
= IMPLEMENTED

C2 repository provider boundary
= IMPLEMENTED

C3 experimental record routes
= IMPLEMENTED

Initial repository backend
= IN-MEMORY

Current /loop/step
= UNCHANGED

GitHub Actions verification
= PENDING
```
