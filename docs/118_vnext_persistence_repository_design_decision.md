# 118. vNext Persistence / Repository Design Decision

---

## 1. Purpose

This document records the design decision for integration gate B:

```text
B. persistence / repository support
```

The decision follows completion of integration gate A:

```text
Read-only Runtime projection
= COMPLETE
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Persistence is an implementation support capability. It is not a new Core stage and must not redefine semantic, readability, continuity, Trajectory, or Runtime meaning.

---

## 2. Decision Context

The isolated vNext architecture now contains explicit in-memory records for:

```text
Semantic realization
Incorporated Readability
Continuity Readability
Trajectory
Read-only Runtime projection
```

These records currently have:

```text
typed models
pure builders
isolated assembly services
reference-integrity validation
deep-copy boundaries
```

They do not yet have durable storage or repository reconstruction semantics.

---

## 3. Options Reviewed

### Option 1. Modify current canonical SQLite tables

Decision:

```text
REJECTED FOR INITIAL B IMPLEMENTATION
```

Reason:

```text
would couple experimental records to accepted Runtime persistence
would require migration and reconstruction contracts too early
would increase rollback and compatibility risk
could imply canonical status not yet granted
```

### Option 2. Add separate experimental SQLite tables immediately

Decision:

```text
DEFERRED
```

Reason:

```text
possible later
requires schema ownership, migrations, transaction semantics, retention, and reconstruction policy
not necessary to validate repository boundaries first
```

### Option 3. JSON artifact repository

Decision:

```text
DEFERRED AS SECOND STEP
```

Reason:

```text
useful for inspection and exchange
requires atomic write, file naming, corruption, replacement, and concurrency rules
should follow repository contract validation
```

### Option 4. Isolated in-memory experimental repository

Decision:

```text
SELECTED AS INITIAL B IMPLEMENTATION
```

Reason:

```text
validates repository interfaces without changing SQLite
preserves experimental status
supports deterministic tests
allows save/get/list/delete semantics to be reviewed independently
keeps reconstruction and serialization policy explicit
provides a safe base for later JSON or SQLite adapters
```

---

## 4. Selected Boundary

The initial B implementation should introduce:

```text
ExperimentalRecordEnvelope
ExperimentalRecordRepository
InMemoryExperimentalRecordRepository
```

The repository must remain separate from:

```text
current SQLite repository
canonical Runtime persistence
repository reconstruction registry
POST /loop/step
public API
GyroAuth
```

---

## 5. ExperimentalRecordEnvelope

Recommended fields:

```text
record_id
process_id
record_type
record_payload
schema_version
provisional
created_at
metadata
```

Purpose:

```text
store one explicit serialized vNext record payload
preserve record type and schema label
avoid requiring a canonical class registry initially
support later adapters without changing domain models
```

The envelope does not prove that `record_payload` matches `record_type`.

Initial validation should be structural only.

---

## 6. Repository Contract

Recommended minimal operations:

```text
save(envelope)
get(record_id)
list(process_id=None, record_type=None)
delete(record_id)
```

Initial semantics:

```text
save existing record_id
= reject by default

get missing record_id
= return None

list order
= insertion order for deterministic PoC behavior only

delete missing record_id
= return false
```

Insertion order must not be interpreted as:

```text
time order
establishment order
Trajectory order
authority precedence
canonical history
```

---

## 7. Copy and Ownership Boundary

The repository must deep-copy envelopes on both write and read.

```text
caller object
≠ stored repository object
≠ returned repository object
```

Repository storage does not grant semantic ownership or canonical authority.

---

## 8. Reconstruction Boundary

The initial repository must not reconstruct:

```text
StabilityScene
ReadabilityContext
ContinuityRelationRecord
TrajectoryGraph
RuntimeSnapshot
```

from envelope payloads.

It returns the stored envelope only.

Typed reconstruction requires a later explicit registry decision.

---

## 9. Transaction and Concurrency Boundary

The initial in-memory repository does not define production transaction semantics.

It should provide deterministic single-process behavior only.

It does not claim:

```text
multi-process safety
durable atomicity
crash recovery
cross-record transactions
optimistic locking
pessimistic locking
```

Those belong to later JSON or SQLite adapter reviews.

---

## 10. Retention and Deletion Boundary

The initial repository provides explicit deletion only.

It does not infer:

```text
expiry
retention period
archival
supersession cleanup
Trajectory garbage collection
current-record replacement
```

---

## 11. Security Boundary

The initial repository is internal experimental infrastructure.

It does not add:

```text
authentication
authorization
encryption at rest
tenant separation
public query access
```

These must be reviewed before any public API or GyroAuth consumption.

---

## 12. Proposed Implementation Sequence

```text
1. ExperimentalRecordEnvelope design
2. repository protocol / abstract contract
3. in-memory repository implementation
4. unit tests
5. Actions verification
6. B repository review
7. decide whether JSON adapter is useful
8. only then consider separate experimental SQLite tables
```

Do not begin with current SQLite schema modification.

---

## 13. Required Tests

The initial test set should verify:

```text
save and get
missing get
filtered list by process_id
filtered list by record_type
combined filtering
duplicate record ID rejection
delete existing record
delete missing record
deep-copy on save
deep-copy on get
no typed reconstruction
no current/latest/authority inference
```

---

## 14. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Persistence added to Core
= NO

Current Runtime repository changed
= NO

Current SQLite schema changed
= NO

Public API introduced
= NO

GyroAuth dependency introduced
= NO
```

---

## 15. Final Decision

```text
B persistence / repository design decision
= COMPLETE

Initial persistence target
= ISOLATED IN-MEMORY EXPERIMENTAL REPOSITORY

Current SQLite modification
= NOT APPROVED

Separate experimental SQLite tables
= DEFERRED

JSON artifact repository
= DEFERRED UNTIL REPOSITORY CONTRACT REVIEW

Typed reconstruction registry
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```

---

## 16. Next Step

Proceed to:

```text
B1. ExperimentalRecordEnvelope
B2. ExperimentalRecordRepository contract
B3. InMemoryExperimentalRecordRepository
```

After implementation and Actions verification, perform a separate B repository review before considering JSON or SQLite adapters.
