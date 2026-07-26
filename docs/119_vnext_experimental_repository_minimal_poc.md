# 119. vNext Experimental Repository Minimal PoC

---

## 1. Purpose

This document records the isolated implementation of integration gate B initial scope:

```text
B1. ExperimentalRecordEnvelope
B2. ExperimentalRecordRepository contract
B3. InMemoryExperimentalRecordRepository
```

The implementation remains experimental, process-local, ephemeral, and isolated from the current canonical SQLite repository.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. B1 ExperimentalRecordEnvelope

Added to:

```text
app/vnext/models.py
```

Fields:

```text
record_id
process_id
record_type
payload
source_ref
provisional
stored_at
metadata
```

The envelope stores an opaque payload.

It does not:

```text
reconstruct a typed vNext model
establish canonical authority
select a current record
define version order
define Trajectory order
define establishment order
validate record_type against a registry
```

---

## 3. B2 ExperimentalRecordRepository Contract

Added:

```text
app/vnext/experimental_repository.py
ExperimentalRecordRepository
```

The abstract contract defines only:

```text
save(envelope)
get(record_id)
list(process_id=None, record_type=None)
delete(record_id)
```

The contract does not define:

```text
transactions
compare-and-swap
append-only semantics
version history
current/latest selection
canonical authority
cross-process coordination
crash recovery
retention policy
```

---

## 4. B3 InMemoryExperimentalRecordRepository

Added:

```text
app/vnext/experimental_repository.py
InMemoryExperimentalRecordRepository
```

Characteristics:

```text
process-local
ephemeral
thread-safe within one Python process
deep-copy on save/get/list
record_id keyed storage
same-ID save replaces prior envelope
optional process_id and record_type filters
boolean delete result
```

Replacement by record ID is a storage operation only.

```text
replacement
≠ canonical supersession
≠ version advancement
≠ current-record selection
```

---

## 5. Read / Write Boundary

The repository may write only to its private in-memory mapping.

It does not write to:

```text
current SQLite schema
Runtime history
POST /loop/step result
SemanticAssemblyService output
Readability assembly output
Continuity assembly output
Trajectory assembly output
public API response
GyroAuth state
```

Stored payloads remain opaque envelopes.

---

## 6. Ordering Boundary

The list operation returns matching records but does not define semantic ordering.

```text
list order
≠ time order
≠ establishment order
≠ revision order
≠ Trajectory order
≠ canonical history
```

No sorting guarantee is introduced in the initial contract.

---

## 7. Copy and Mutation Boundary

The in-memory implementation deep-copies envelopes on:

```text
save
get
list
```

Caller mutation after save does not alter stored content.

Mutation of a returned envelope does not alter stored content.

---

## 8. Tests

Added:

```text
tests/vnext/test_experimental_repository.py
```

Coverage includes:

```text
contract implementation
save/get behavior
deep-copy on save
independent returned copies
same-ID replacement
process filter
record-type filter
combined filtering
delete success/failure
absence of canonical/current/version/order fields
```

The Priority F workflow executes this test with all accepted Runtime and vNext regression tests.

---

## 9. Isolation Boundary

The repository remains isolated from:

```text
current SQLite repository
repository reconstruction registry
Runtime execution
OperatorResponse selection
public experimental API
GyroAuth consumption
cross-process persistence
file-system persistence
JSON artifact export
```

---

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Persistence added to Core
= NO

Current SQLite schema changed
= NO

Canonical authority introduced
= NO

Current/latest selection introduced
= NO

Typed reconstruction introduced
= NO

Runtime behavior changed
= NO

Public API changed
= NO
```

---

## 11. Current Decision

```text
ExperimentalRecordEnvelope
= VERIFIED AS OPAQUE EXPERIMENTAL ENVELOPE

ExperimentalRecordRepository
= VERIFIED AS MINIMAL ABSTRACT CONTRACT

InMemoryExperimentalRecordRepository
= VERIFIED AS ISOLATED EPHEMERAL REPOSITORY

Current SQLite schema
= UNCHANGED

Typed reconstruction registry
= NOT IMPLEMENTED

GitHub Actions verification
= VERIFIED
```

Verified workflow runs:

```text
30181950498
30181963740
30181978771
30182000923
```

---

## 12. Review Gate

Proceed to:

```text
Experimental Repository Review
```

The review must confirm:

```text
opaque envelope boundary
contract minimality
deep-copy safety
replacement semantics
filter semantics
ordering non-semantics
canonical authority absence
Runtime isolation
SQLite isolation
public API isolation
regression verification
```

Only after that review should the next B step be considered:

```text
B4. JSON artifact repository design
```

Do not introduce SQLite experimental tables before the review.
