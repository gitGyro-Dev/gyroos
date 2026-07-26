# 131. vNext Public Experimental API Review

---

## 1. Scope

Reviewed:

```text
ExperimentalApiSettings
ExperimentalRecordCreateRequest
ExperimentalRecordResponse
ExperimentalRecordListResponse
ExperimentalApiError
ExperimentalRepositoryProvider
experimental record router
main application router registration
```

---

## 2. Public Contract Boundary

The API exposes only:

```text
ExperimentalRecordEnvelope CRUD
```

It does not expose Semantic, Readability, Continuity, Trajectory, or Runtime assembly services.

Decision:

```text
Initial public contract scope
= ACCEPTED
```

---

## 3. Namespace Isolation

All new routes are under:

```text
/vnext/experimental
```

The existing bounded Runtime route remains:

```text
/loop/step
```

Decision:

```text
Namespace isolation
= ACCEPTED

Current Runtime route preservation
= ACCEPTED
```

---

## 4. Repository Dependency Boundary

Routes depend on:

```text
ExperimentalRecordRepository
```

through the explicit provider dependency.

The initial backend is in-memory only.

Decision:

```text
Abstract repository dependency
= ACCEPTED

Initial backend selection
= ACCEPTED

JSON artifact backend public exposure
= NOT APPROVED
```

---

## 5. Opaque Record Boundary

The create request maps only to:

```text
ExperimentalRecordEnvelope
```

The API does not infer record semantics or reconstruct typed vNext models.

Decision:

```text
Opaque payload boundary
= ACCEPTED

Typed reconstruction absence
= ACCEPTED
```

---

## 6. Resource and List Boundary

The API limits:

```text
payload bytes
metadata bytes
record ID length
record type length
list result count
```

List results explicitly state:

```text
ordering = UNSPECIFIED
```

Decision:

```text
Resource limits
= ACCEPTED FOR EXPERIMENTAL POC

Ordering non-semantics
= ACCEPTED
```

---

## 7. Error Boundary

The initial route error contract distinguishes:

```text
request validation
record not found
```

No Runtime, SQLite, or typed reconstruction errors are introduced by the initial in-memory route scope.

Decision:

```text
Initial error contract
= ACCEPTED
```

---

## 8. Authentication Boundary

The experimental router reuses the existing bearer dependency.

This does not introduce a separate identity or authorization model and does not map records to GyroAuth decisions.

Decision:

```text
Existing authentication dependency reuse
= ACCEPTED

GyroAuth mapping absence
= ACCEPTED
```

---

## 9. Runtime and Layer Consistency

Unchanged:

```text
Structure → Slice → Stability
ProcessExecutor
StabilityEngine
OperatorResponse selection
current SQLite schema
Runtime history
```

Decision:

```text
Core consistency
= ACCEPTED

Runtime isolation
= ACCEPTED

Persistence isolation
= ACCEPTED
```

---

## 10. Test and Workflow State

Tests cover:

```text
settings and public model validation
provider dependency boundary
CRUD routes
filters
bounded list results
explicit not-found errors
canonical field rejection
existing /loop/step registration
```

The Priority F workflow includes all C1-C3 tests.

Final workflow run verification remains pending.

---

## 11. Final Decision

```text
C public experimental API review
= COMPLETE AT DESIGN / IMPLEMENTATION LEVEL

C1 settings and public models
= ACCEPTED

C2 repository provider boundary
= ACCEPTED

C3 experimental record routes
= ACCEPTED PENDING WORKFLOW VERIFICATION

Critical design blocker
= NONE IDENTIFIED

GitHub Actions verification
= PENDING
```

Do not proceed to assembly endpoints, JSON backend public selection, or GyroAuth consumption until workflow verification succeeds and the next integration gate is explicitly selected.
