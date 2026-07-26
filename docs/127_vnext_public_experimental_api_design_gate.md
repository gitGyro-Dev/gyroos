# 127. vNext Public Experimental API Design Gate

---

## 1. Purpose

This document records the design gate for:

```text
C. public experimental API
```

The API must expose selected vNext experimental capabilities without changing the accepted Runtime contract, introducing canonical authority, or collapsing isolated layers.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Entry Conditions

The following gates are complete:

```text
A. read-only Runtime projection
B. persistence / repository support
```

This does not automatically approve public exposure.

C requires a separate experimental API boundary.

---

## 3. Namespace Decision

Selected namespace:

```text
/vnext/experimental
```

The API must not add new behavior under:

```text
/loop/step
```

The experimental namespace must remain visibly separate from the accepted Runtime API.

Decision:

```text
Experimental namespace separation
= REQUIRED
```

---

## 4. Initial Endpoint Scope

The first minimal API should expose repository operations only:

```text
POST   /vnext/experimental/records
GET    /vnext/experimental/records/{record_id}
GET    /vnext/experimental/records
DELETE /vnext/experimental/records/{record_id}
```

The first API should not expose all assembly services in the same step.

Deferred:

```text
semantic assembly endpoints
readability assembly endpoints
continuity assembly endpoints
trajectory assembly endpoints
Runtime projection endpoint
```

This keeps the first public boundary small and reviewable.

---

## 5. Request / Response Boundary

The public record contract is based on:

```text
ExperimentalRecordEnvelope
```

The API must not reconstruct or return typed vNext records based on `record_type`.

```text
record_type
= caller-supplied label

payload
= opaque JSON object
```

Decision:

```text
Opaque envelope API boundary
= REQUIRED
```

---

## 6. Repository Injection Boundary

The API layer must depend on:

```text
ExperimentalRecordRepository
```

not directly on:

```text
InMemoryExperimentalRecordRepository
JsonArtifactExperimentalRecordRepository
```

Backend selection must occur at application composition/configuration time.

The route layer must not infer canonical preference between backends.

Decision:

```text
Repository contract injection
= REQUIRED
```

---

## 7. Initial Backend Decision

For the first API PoC, select:

```text
InMemoryExperimentalRecordRepository
```

Reason:

```text
no filesystem configuration required
no durability claims
smaller operational surface
clear experimental lifecycle
```

The JSON artifact backend remains independently verified and may be selected later by explicit configuration.

Decision:

```text
Initial public API backend
= IN-MEMORY EXPERIMENTAL REPOSITORY
```

---

## 8. Error Contract

Initial HTTP mapping:

```text
invalid request model
→ 422

record not found
→ 404

unsafe or backend-specific repository error
→ 400 or 500 only through explicit mapping

successful save
→ 200 or 201

successful delete
→ 204
```

The API must not silently convert corrupted persistent artifacts into `404`.

When the JSON backend is introduced later, artifact errors require explicit response mapping.

---

## 9. List Boundary

Supported filters:

```text
process_id
record_type
```

The API must not expose or imply:

```text
latest=true
current=true
canonical=true
sort=trajectory
sort=establishment
```

List response order remains non-semantic.

Decision:

```text
List filtering
= ALLOWED

Semantic ordering
= FORBIDDEN
```

---

## 10. Resource Boundaries

The first API implementation must define bounded inputs:

```text
maximum payload size
maximum metadata size
maximum list response count
maximum record ID length
maximum record type length
```

Exact values should be implemented as explicit experimental settings and tested.

No unbounded repository listing should be exposed publicly.

---

## 11. Security Boundary

The first API PoC must not claim production authentication or authorization.

At minimum it must preserve existing application authentication boundaries and must not weaken current protected routes.

The experimental route must not introduce:

```text
path-selected filesystem access
caller-selected repository root
caller-selected backend class
arbitrary typed object construction
```

---

## 12. Non-responsibilities

The initial public API does not:

```text
change /loop/step
execute Runtime
select OperatorResponse
infer Semantic records
infer Readability records
infer Continuity records
infer Trajectory records
reconstruct typed records
select current/latest records
assert canonical authority
perform GyroAuth decisions
```

---

## 13. Recommended Implementation Order

```text
C1. experimental API settings and public models
↓
Review
↓
C2. repository dependency/provider boundary
↓
Review
↓
C3. experimental record routes
↓
Actions verification
↓
C Review
```

Do not expose assembly services until the record API is verified and reviewed.

---

## 14. Current Decision

```text
C public experimental API design gate
= COMPLETE

Initial endpoint scope
= EXPERIMENTAL RECORD CRUD ONLY

Initial backend
= IN-MEMORY EXPERIMENTAL REPOSITORY

Current /loop/step contract
= UNCHANGED

Typed reconstruction
= NOT APPROVED

Assembly service exposure
= DEFERRED

GyroAuth consumption
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```
