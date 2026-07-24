# 66. Priority G-1 — Persistence Boundary and Repository Contract

---

## 1. Purpose

This document defines **G-1: Persistence Boundary and Repository Contract** for the GyroOS bounded Runtime.

Priority F established an execution-verified bounded Process:

```text
one LoopStepRequest
→ one bounded Gyro Process
→ one complete LoopStepResult
→ one atomic in-memory publication
```

Priority G introduces durable state and query support without changing the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

Persistence is a Runtime support responsibility.
It must not become a second execution engine, a second response owner, or an alternative interpretation layer.

---

## 2. Contract Decision

The Runtime executor shall depend on a storage-independent repository contract.

```text
ProcessExecutor
→ RuntimeRepository contract
→ InMemoryStore | SQLiteStore
```

The repository contract defines observable storage behavior.
It does not expose SQLite tables, SQL syntax, connection objects, transaction cursors, or storage-specific exceptions to Runtime orchestration.

Canonical decision:

```text
RuntimeRepository
= storage-independent behavioral contract

InMemoryStore
= reference implementation for bounded tests and PoC

SQLiteStore
= first persistent implementation
```

---

## 3. Responsibility Boundary

### 3.1 Repository responsibilities

A conforming repository may:

```text
store one complete canonical Runtime result group
resolve a Process by explicit process_id
resolve a canonical record by explicit record_id
resolve the current-scope Process reference by explicit loop_id
resolve an idempotency entry by explicit loop_id and idempotency_key
return ordered Process history for one explicit loop_id
return ordered TrajectoryEdge records for one explicit trajectory relation
preserve identity, lineage, digest, and publication order
apply one atomic publication boundary
```

### 3.2 Prohibited responsibilities

A repository must not:

```text
execute Slice
produce SliceDone
read or calculate Stability
select OperatorResponse
build RuntimeContinuityResult
classify Boundary State
create VoidEvidence from missing storage data
infer a record without an explicit identity or query scope
choose an implicit latest record
collapse complete history into current scope
rewrite canonical payload semantics
repair invalid Runtime objects silently
execute reconstructed objects
```

The only canonical OperatorResponse owner remains:

```text
LoopController
```

The repository records that decision after the complete result group has passed Runtime validation.

---

## 4. Repository Protocol

The implementation contract should be expressible as a Python protocol or abstract base interface equivalent to:

```python
from typing import Protocol

class RuntimeRepository(Protocol):
    def get_process(self, process_id: str) -> LoopStepResult | None:
        ...

    def get_record(self, record_id: str) -> object | None:
        ...

    def get_current_scope(self, loop_id: str) -> str | None:
        ...

    def get_idempotent(
        self,
        loop_id: str,
        idempotency_key: str,
    ) -> IdempotencyEntry | None:
        ...

    def publish(
        self,
        *,
        result: LoopStepResult,
        request_digest: str,
        idempotency_key: str | None,
    ) -> None:
        ...

    def list_process_history(
        self,
        *,
        loop_id: str,
        limit: int,
        cursor: str | None,
    ) -> Page[LoopStepResult]:
        ...

    def list_trajectory_edges(
        self,
        *,
        trajectory_ref: str,
        limit: int,
        cursor: str | None,
    ) -> Page[TrajectoryEdge]:
        ...
```

The exact persistent envelope and page models are deferred to G-2.
The behavioral requirements in this document are binding for those later models.

---

## 5. Explicit Identity Rule

All singular retrieval operations require explicit identity.

```text
get_process(process_id)
get_record(record_id)
get_current_scope(loop_id)
get_idempotent(loop_id, idempotency_key)
```

The repository shall not provide ambiguous operations such as:

```text
get_latest_process()
get_last_record()
get_current_or_latest()
find_best_match()
```

unless a later contract defines the complete scope and ordering explicitly.

This preserves:

```text
identity
≠ recency
≠ current scope
≠ complete history
```

---

## 6. Current Scope and History Separation

Current scope is an explicit pointer:

```text
loop_id
→ current process_id
```

It is not a destructive replacement of history.

A successful publication shall:

```text
append one immutable completed Process to history
+
update the current-scope pointer for that loop_id
```

Therefore:

```text
current scope
≠ only retained Process

current scope
≠ complete Process history
```

Updating current scope must not delete, overwrite, or mutate prior Process records.

---

## 7. Atomic Publication Contract

`publish(...)` is the repository transaction boundary.

Its input is one fully constructed and validated `LoopStepResult` plus request-level publication metadata.

The publication group includes, when present:

```text
LoopStepResult / Process record
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
DeferredRelationRecord
TrajectoryEdge
idempotency entry
current-scope pointer update
```

Required semantics:

```text
all required writes succeed
→ complete result group becomes visible

any required write fails
→ no part of the new completed Process becomes visible
```

A repository must not expose:

```text
Process without SliceDone
Process without StabilityResult
Process without OperatorResponse
Process without RuntimeContinuityResult
partial evidence sets
idempotency entry without the referenced Process
current-scope pointer to an unpublished Process
```

### 7.1 Validation ownership

The executor owns construction and canonical Runtime validation before publication.

The repository must still enforce storage-level integrity including:

```text
identity collision rejection
transactional completeness
referential consistency within the publication group
canonical payload digest consistency when persisted
```

The repository must not reinterpret a valid object to make it fit storage.

---

## 8. Idempotency Contract

An idempotency entry is scoped by:

```text
(loop_id, idempotency_key)
```

It preserves at least:

```text
request_digest
process_id
complete LoopStepResult reconstruction reference
```

Required behavior:

```text
same scope + same key + same digest
→ return the original completed Process as replay

same scope + same key + different digest
→ idempotency conflict

no entry
→ normal execution may continue
```

The persistent implementation must preserve this behavior across repository and application restarts.

An idempotency lookup must not create, mutate, or republish Runtime records.

---

## 9. Record Retrieval Contract

`get_record(record_id)` returns the canonical Runtime record represented by that explicit identity.

For persistent storage, retrieval must:

```text
read the stored record type
read the canonical payload
validate the payload through the registered canonical Pydantic model
return the typed canonical object
```

It must not return an unvalidated executable object.

Missing record behavior:

```text
record_id not found
→ repository returns None
→ API layer maps to the defined not-found ApiError
```

Missing storage data must not become:

```text
BoundaryState.VOID
VoidEvidence
OperatorResponse.DEFER
OperatorResponse.STOP
```

---

## 10. Ordered Query Contract

History and trajectory queries require:

```text
explicit query scope
stable deterministic ordering
bounded limit
opaque or contract-defined cursor
```

### 10.1 Process history

Process history is scoped by `loop_id`.

Canonical ordering direction for the first implementation:

```text
publication order ascending
```

A page must not silently skip or duplicate records when the underlying dataset is unchanged.

### 10.2 Trajectory edges

Trajectory query is scoped by an explicit trajectory identity or explicit relation defined in G-7.

The repository may use indexed lineage fields, but returned canonical `TrajectoryEdge` payloads remain authoritative.

### 10.3 No unbounded query

The repository must reject or normalize requests outside the accepted bounds.

```text
limit is required or has a bounded default
limit has a defined maximum
```

The concrete page envelope and cursor representation are deferred to G-2.

---

## 11. Repository Error Categories

Storage-specific exceptions must be translated into repository-level categories before reaching the API layer.

Required categories include:

```text
RecordIdentityCollision
IdempotencyConflict
RepositoryIntegrityError
RepositoryUnavailable
RepositorySerializationError
RepositorySchemaMismatch
```

A repository error is not a Runtime result.

```text
repository failure
≠ StabilityStatus
≠ Boundary State
≠ OperatorResponse
≠ RuntimeContinuityType
```

The API layer may map repository failures to the accepted HTTP/error model, but it must not fabricate a successful `LoopStepResult`.

---

## 12. Concurrency and Visibility

The first implementation is single-node, but the repository contract must define publication visibility clearly.

Required behavior:

```text
read before commit
→ previous committed state

read after successful commit
→ complete new state

read during failed publication
→ no partial new state
```

For concurrent publications affecting the same `loop_id`, the persistent implementation must serialize or detect conflicts so that the current-scope pointer never references an indeterminate Process.

Priority G does not require distributed consensus or multi-node locking.

---

## 13. Canonical Object Ownership

The repository stores objects produced by the existing Runtime components:

```text
SliceEngine
→ SliceDone and evidence

StabilityEngine
→ StabilityResult

LoopController
→ OperatorResponse

ContinuityBuilder
→ RuntimeContinuityResult

ProcessExecutor
→ complete LoopStepResult and supporting records

RuntimeRepository
→ atomic preservation and explicit retrieval
```

This ownership chain is normative.

The repository does not gain authority over the Gyro Process merely because it persists the result.

---

## 14. InMemoryStore Conformance

The existing `InMemoryStore` already provides the core G-1 operations:

```text
get_process
get_record
get_current_scope
get_idempotent
publish
```

Its atomic boundary is one `RLock`-protected publication block.

G-1 does not require replacing it.
It remains the reference implementation for fast bounded tests.

Later Priority G steps must refactor `ProcessExecutor` to depend on the common repository contract rather than the concrete `InMemoryStore` type.

The following capabilities remain to be added or formalized:

```text
storage-independent protocol type
repository-level error types
typed idempotency entry
bounded page contract
process history query
trajectory query
```

---

## 15. SQLiteStore Conformance Requirements

The future `SQLiteStore` must implement the same observable behavior as `InMemoryStore` for shared operations.

It must additionally demonstrate:

```text
transactional publication
restart-safe record retrieval
restart-safe idempotency
restart-safe current scope
ordered history query
ordered trajectory query
typed canonical reconstruction
schema-version rejection or migration boundary
```

SQLite-specific details remain implementation-private.

The Runtime executor must not know:

```text
table names
SQL statements
connection lifecycle
SQLite row format
SQLite transaction syntax
```

---

## 16. Security Constraints

A conforming persistent repository must:

```text
use parameterized statements
use an explicit record-type registry
validate reconstructed canonical payloads
reject unknown record types
reject unsupported schema versions
bound query limits
avoid dynamic object import from stored values
avoid implicit code execution during deserialization
```

Stored metadata is data.
It must never be treated as executable configuration without a separate validated contract.

---

## 17. G-1 Acceptance Criteria

G-1 is complete when the following decisions are explicit and mutually consistent:

```text
repository is a Runtime support boundary
repository contract is storage-independent
ProcessExecutor will depend on the contract
explicit identity is required for singular retrieval
current scope remains separate from complete history
publish is one atomic result-group boundary
idempotency semantics are preserved across implementations
missing records remain storage/API errors, not Runtime VOID
history and trajectory queries are bounded and explicitly scoped
canonical reconstruction requires model validation
storage-specific errors do not leak as Runtime responses
InMemoryStore remains a valid reference implementation
SQLiteStore requirements are defined without leaking SQLite into Runtime orchestration
```

Decision:

```text
G-1 Persistence Boundary and Repository Contract
= COMPLETE

G-2 Canonical Persistent Record Envelope
= READY TO START
```

---

## 18. Next Step

The next step is:

```text
G-2 Canonical Persistent Record Envelope
```

G-2 must define:

```text
PersistentRecordEnvelope
record-type registry
canonical payload digest
schema_version
runtime_version
IdempotencyEntry
Page and cursor models
lineage index fields
serialization and reconstruction rules
```
