# 78. Priority H-2 — Authentication and Authorization Boundary

---

## 1. Purpose

H-2 introduces the first explicit access boundary for the bounded GyroOS Runtime API.

The purpose is to prevent anonymous callers from executing Processes or reading Runtime state in production.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Authentication determines whether an external caller may enter an API surface. It does not select OperatorResponse, evaluate Stability, or alter canonical Runtime records.

---

## 2. Initial Security Model

The initial H-2 model uses one configured static bearer token:

```text
Authorization: Bearer <configured token>
```

This is a bounded production-hardening boundary.

It is not yet:

```text
user authentication
OAuth2 authorization server
JWT issuance
role-based access control
multi-tenant identity
service account registry
secret rotation system
```

Those concerns remain deferred.

---

## 3. Environment Variable Contract

Added:

```text
GYROOS_AUTH_REQUIRED
GYROOS_API_BEARER_TOKEN
```

Defaults:

```text
development → authentication disabled
test        → authentication disabled
production  → authentication enabled
```

Production requires:

```text
GYROOS_AUTH_REQUIRED=true
GYROOS_API_BEARER_TOKEN=<non-empty secret>
```

Production startup fails when authentication is disabled or the bearer token is absent.

The token is never returned by the health endpoint or Runtime API.

---

## 4. Public and Protected Surfaces

Public endpoint:

```text
GET /health
```

Protected endpoints:

```text
POST /loop/step
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /trajectory/{trajectory_ref}
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

The protected endpoints are grouped under one shared FastAPI `APIRouter` dependency.

This avoids endpoint-by-endpoint authentication omissions.

---

## 5. Authentication Evaluation

Added:

```text
app/security.py
```

Primary functions:

```text
authorize_bearer(...)
require_runtime_bearer(...)
```

Evaluation:

```text
authentication disabled
→ allow request

authentication enabled + missing/malformed bearer
→ HTTP 401

authentication enabled + incorrect bearer
→ HTTP 401

authentication enabled + exact configured bearer
→ continue to Runtime endpoint
```

Token comparison uses constant-time `secrets.compare_digest`.

---

## 6. Unauthorized Response Contract

Missing or invalid credentials return:

```text
HTTP 401 Unauthorized
WWW-Authenticate: Bearer
```

Authentication failure occurs before:

```text
Process execution
reference resolution
current-scope lookup
history query
trajectory query
memory reconstruction
```

Authentication failure is not converted into:

```text
BoundaryState.VOID
VoidEvidence
StabilityStatus.NOT_EVALUABLE
OperatorResponse.DEFER
OperatorResponse.STOP
```

---

## 7. Authorization Boundary

H-2 establishes an authenticated/unauthenticated boundary only.

An authenticated caller currently has access to all protected Runtime endpoints.

The current rule is:

```text
valid configured bearer
→ authenticated Runtime client
```

Fine-grained authorization remains deferred:

```text
read versus execute permissions
loop-specific access
record-specific access
administrative operations
principal identity
role claims
```

These should not be simulated through request payload fields.

---

## 8. Implemented Files

Added:

```text
app/security.py
tests/test_authentication_boundary.py
docs/78_priority_h2_authentication_and_authorization_boundary.md
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
development/test authentication defaults
production bearer-token requirement
production authentication-disable rejection
valid production security configuration
optional local authentication enablement
invalid authentication boolean rejection
```

Authentication tests verify:

```text
health remains public
missing bearer is rejected
invalid bearer is rejected
correct bearer is accepted
authentication-disabled profile remains locally compatible
```

The workflow executes the H-2 test file and completed successfully.

---

## 10. Deferred Security Work

H-2 does not yet implement:

```text
TLS termination
hashed token storage
secret manager integration
token rotation
multiple active tokens
principal identity
RBAC or ABAC
audit event logging
rate limiting
request-size limits
CSRF or browser session support
```

TLS and secure secret delivery are deployment requirements before public network exposure.

---

## 11. Responsibility Review

```text
RuntimeSettings
→ determines whether authentication is required and loads the configured token

security boundary
→ validates transport credentials before Runtime access

FastAPI protected router
→ applies one shared authentication dependency

Runtime endpoints
→ retain their existing Process and repository responsibilities
```

The bearer token does not become part of canonical Process identity, request digest, trajectory, Stability, or memory records.

---

## 12. H-2 Decision

```text
H-2 Authentication and Authorization Boundary
= COMPLETE

Production authentication requirement
= VERIFIED

Shared protected-router boundary
= VERIFIED

Constant-time bearer validation
= VERIFIED

Public health / protected Runtime separation
= VERIFIED

Fine-grained authorization
= DEFERRED

GitHub Actions execution verification
= PASS
```

The next Priority H step is:

```text
H-3 Request Size, Rate, and Resource Limits
```
