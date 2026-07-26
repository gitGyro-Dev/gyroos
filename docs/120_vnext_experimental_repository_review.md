# 120. vNext Experimental Repository Review

---

## 1. Purpose

This document reviews the isolated experimental repository implementation:

```text
ExperimentalRecordEnvelope
ExperimentalRecordRepository
InMemoryExperimentalRecordRepository
```

The review evaluates persistence boundaries only. It does not approve canonical SQLite integration, typed reconstruction, public API exposure, or GyroAuth consumption.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Verified Scope

Verified workflow runs:

```text
30181950498 = success
30181963740 = success
30181978771 = success
30182000923 = success
```

Reviewed files:

```text
app/vnext/models.py
app/vnext/experimental_repository.py
tests/vnext/test_experimental_repository.py
docs/119_vnext_experimental_repository_minimal_poc.md
```

---

## 3. Opaque Envelope Boundary

`ExperimentalRecordEnvelope` stores:

```text
record identity
process scope
record-type label
opaque payload
optional source reference
provisional marker
storage timestamp
metadata
```

It does not reconstruct or validate a typed vNext model.

Decision:

```text
Opaque envelope boundary
= ACCEPTED
```

---

## 4. Contract Minimality

The repository contract defines only:

```text
save
get
list
delete
```

It does not imply transactions, versions, authority, current selection, append-only history, or canonical ordering.

Decision:

```text
Repository contract minimality
= ACCEPTED
```

---

## 5. In-memory Implementation Boundary

The in-memory implementation is:

```text
process-local
ephemeral
thread-safe within one Python process
keyed by record_id
```

It is not a durability mechanism or cross-process store.

Decision:

```text
In-memory implementation boundary
= ACCEPTED
```

---

## 6. Copy and Mutation Safety

Deep copies are used on:

```text
save
get
list
```

Caller-side mutation does not alter stored state, and mutation of returned records does not rewrite repository state.

Decision:

```text
Copy / mutation safety
= ACCEPTED
```

---

## 7. Replacement Semantics

Saving the same `record_id` replaces the prior stored envelope.

This means only:

```text
record_id-keyed storage replacement
```

It does not mean:

```text
canonical supersession
version progression
current-record selection
Trajectory revision
Identity continuation
```

Decision:

```text
Replacement semantics
= ACCEPTED AS STORAGE-LOCAL BEHAVIOR
```

---

## 8. Filter Semantics

`list` supports optional filters:

```text
process_id
record_type
```

Filters are exact-match storage queries only. They do not perform ontology matching, namespace expansion, inheritance, or semantic classification.

Decision:

```text
Filter semantics
= ACCEPTED
```

---

## 9. Ordering Non-semantics

Repository list order does not define:

```text
time order
establishment order
revision order
Trajectory order
canonical history
importance
precedence
```

Decision:

```text
Ordering non-semantics
= ACCEPTED
```

---

## 10. Authority and Reconstruction Boundaries

The repository does not:

```text
select authoritative records
select current/latest records
reconstruct typed models
validate record_type against a registry
resolve record references
```

Decision:

```text
Canonical authority absence
= ACCEPTED

Typed reconstruction absence
= ACCEPTED
```

---

## 11. Runtime, SQLite, API, and GyroAuth Isolation

The implementation remains isolated from:

```text
POST /loop/step
ProcessExecutor
StabilityEngine
OperatorResponse selection
current SQLite schema
repository reconstruction registry
public API routes
GyroAuth state or decisions
```

Decision:

```text
Runtime isolation
= ACCEPTED

SQLite isolation
= ACCEPTED

Public API isolation
= ACCEPTED

GyroAuth isolation
= ACCEPTED
```

---

## 12. Layer Consistency

```text
Gyro Logic definitions changed
= NO

Persistence added to Core
= NO

Canonical storage semantics introduced
= NO

Current Runtime contract changed
= NO

Current SQLite schema changed
= NO
```

Decision:

```text
Layer consistency
= ACCEPTED
```

---

## 13. Findings

No critical blocker was identified.

The repository is intentionally insufficient for durable persistence. This is not a defect in B1-B3; durability belongs to the separate B4 design gate.

---

## 14. Final Decision

```text
Experimental Repository Review
= COMPLETE

ExperimentalRecordEnvelope
= ACCEPTED

ExperimentalRecordRepository
= ACCEPTED AS MINIMAL CONTRACT

InMemoryExperimentalRecordRepository
= ACCEPTED AS ISOLATED EPHEMERAL IMPLEMENTATION

Critical design blocker
= NONE IDENTIFIED

B4 design consideration
= APPROVED
```

---

## 15. Next

Proceed to:

```text
B4. JSON artifact repository design
```

Do not implement canonical SQLite persistence, typed reconstruction, public API exposure, or automatic Runtime publication as part of B4.
