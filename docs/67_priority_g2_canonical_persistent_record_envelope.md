# 67. Priority G-2 — Canonical Persistent Record Envelope

---

## 1. Purpose

This document defines **G-2: Canonical Persistent Record Envelope** for the GyroOS bounded Runtime.

G-1 established the storage-independent repository boundary:

```text
ProcessExecutor
→ RuntimeRepository
→ InMemoryStore | SQLiteStore
```

G-2 defines how canonical Runtime objects are represented at the persistence boundary without changing their Runtime meaning.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

A persistence envelope is a storage representation.
It is not a new Gyro Logic object, a Runtime decision object, or an alternative API response.

---

## 2. Canonical Decision

Every persisted canonical Runtime object shall be stored through one common envelope.

```text
Canonical Runtime object
→ validate
→ canonical JSON payload
→ canonical digest
→ PersistentRecordEnvelope
→ repository storage
```

On retrieval:

```text
PersistentRecordEnvelope
→ verify envelope
→ verify digest
→ resolve registered record type
→ canonical Pydantic validation
→ typed Runtime object
```

The canonical Runtime object remains authoritative for Runtime semantics.
The envelope adds persistence identity, version, integrity, and query metadata.

---

## 3. PersistentRecordEnvelope

The canonical envelope shall contain:

```python
class PersistentRecordEnvelope(CanonicalModel):
    record_id: str
    record_type: PersistentRecordType
    canonical_payload: dict[str, Any]
    canonical_digest: str
    schema_version: str
    runtime_version: str
    created_at: datetime

    process_id: str | None = None
    loop_id: str | None = None
    publication_id: str
    publication_order: int

    parent_process_ref: str | None = None
    trajectory_ref: str | None = None
    operator_response_ref: str | None = None
    continuity_result_ref: str | None = None
    source_ref: str | None = None
    target_ref: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)
```

The exact Python implementation may be introduced with G-3.
The field semantics in this document are binding.

---

## 4. Field Semantics

### 4.1 `record_id`

`record_id` is the explicit identity used by repository retrieval.

```text
get_record(record_id)
```

It must equal the canonical identity of the enclosed object.

Examples:

```text
LoopStepResult.process_id
SliceDone.slice_id
StabilityResult.stability_result_id
OperatorResponse.operator_response_id
RuntimeContinuityResult.continuity_result_id
BoundaryEvidence.boundary_evidence_id
BoundaryStateRecord.boundary_state_record_id
ContextEvidence.context_evidence_id
VoidEvidence.void_evidence_id
DeferredRelationRecord.deferred_relation_record_id
TrajectoryEdge.trajectory_edge_id
```

The repository must reject a mismatch between `record_id` and the identity inside `canonical_payload`.

### 4.2 `record_type`

`record_type` identifies the registered canonical model used for reconstruction.

It must not contain arbitrary Python import paths, class names supplied by clients, executable code, or dynamic deserialization instructions.

### 4.3 `canonical_payload`

The payload is the complete canonical JSON-compatible representation of one Runtime object.

Required serialization mode:

```python
model.model_dump(mode="json")
```

The payload must preserve:

```text
explicit identities
canonical enum values
lineage references
evidence references
timestamps
metadata
```

Indexed envelope fields are query aids.
They must not replace, truncate, or silently rewrite the canonical payload.

### 4.4 `canonical_digest`

The digest protects canonical payload integrity.

Canonical digest input:

```text
UTF-8 encoded canonical JSON
```

Canonical JSON requirements:

```text
sorted object keys
compact separators
Unicode preserved as JSON
no storage-specific columns
no non-deterministic formatting
```

Reference algorithm:

```python
json.dumps(
    canonical_payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
```

Digest algorithm for Priority G:

```text
SHA-256
```

The stored form shall be an unambiguous lowercase hexadecimal digest.

### 4.5 `schema_version`

`schema_version` identifies the persistent envelope and canonical record schema contract.

Initial value:

```text
1
```

A repository must not silently load an unsupported schema version.
It must raise or return the repository-level category:

```text
RepositorySchemaMismatch
```

Migration is not implicit reconstruction.

### 4.6 `runtime_version`

`runtime_version` identifies the GyroOS Runtime implementation version that produced the envelope.

The first implementation may use a repository-owned constant such as:

```text
0.1.0
```

The value is diagnostic and compatibility metadata.
It must not be used to reinterpret canonical payload semantics silently.

### 4.7 `publication_id`

All records produced by one atomic `publish(...)` operation shall share one `publication_id`.

```text
one complete LoopStepResult group
→ one publication_id
```

This identity supports:

```text
atomic completeness checks
publication-group inspection
rollback verification
```

It does not replace `process_id`.

### 4.8 `publication_order`

`publication_order` is a repository-assigned monotonically increasing order within one repository instance or database.

It provides deterministic history ordering.

```text
publication_order ascending
```

It is not Runtime time, Stability order, causal authority, or current scope.

```text
publication order
≠ created_at
≠ process identity
≠ current scope
```

### 4.9 `process_id` and `loop_id`

`process_id` links supporting records to the completed Process when applicable.

`loop_id` is required for the Process envelope and may be copied into supporting envelopes as an indexed query aid.

A copied index value must equal the corresponding canonical relation.
A mismatch is a repository integrity error.

### 4.10 Lineage index fields

The following fields are optional indexed copies of canonical references:

```text
parent_process_ref
trajectory_ref
operator_response_ref
continuity_result_ref
source_ref
target_ref
```

They enable bounded query execution.
They are not independent semantic sources.

When an index field and canonical payload disagree:

```text
reject envelope
→ RepositoryIntegrityError
```

The repository must not choose whichever value appears newer or more convenient.

---

## 5. PersistentRecordType Registry

Priority G shall use a closed registry.

Initial record types:

```text
LOOP_STEP_RESULT
SLICE_DONE
STABILITY_RESULT
OPERATOR_RESPONSE
RUNTIME_CONTINUITY_RESULT
BOUNDARY_EVIDENCE
BOUNDARY_STATE_RECORD
CONTEXT_EVIDENCE
VOID_EVIDENCE
DEFERRED_RELATION_RECORD
TRAJECTORY_EDGE
```

Reference mapping:

```python
PERSISTENT_RECORD_REGISTRY = {
    PersistentRecordType.LOOP_STEP_RESULT: LoopStepResult,
    PersistentRecordType.SLICE_DONE: SliceDone,
    PersistentRecordType.STABILITY_RESULT: StabilityResult,
    PersistentRecordType.OPERATOR_RESPONSE: OperatorResponse,
    PersistentRecordType.RUNTIME_CONTINUITY_RESULT: RuntimeContinuityResult,
    PersistentRecordType.BOUNDARY_EVIDENCE: BoundaryEvidence,
    PersistentRecordType.BOUNDARY_STATE_RECORD: BoundaryStateRecord,
    PersistentRecordType.CONTEXT_EVIDENCE: ContextEvidence,
    PersistentRecordType.VOID_EVIDENCE: VoidEvidence,
    PersistentRecordType.DEFERRED_RELATION_RECORD: DeferredRelationRecord,
    PersistentRecordType.TRAJECTORY_EDGE: TrajectoryEdge,
}
```

Registry rules:

```text
record type must be known
known type maps to exactly one canonical model
client input cannot extend the registry
unknown type is rejected
reconstruction always runs canonical validation
```

Unknown or unsupported types map to:

```text
RepositorySerializationError
or
RepositorySchemaMismatch
```

They must not be returned as untyped dictionaries when a typed canonical record is expected.

---

## 6. Canonical Identity Extraction

Envelope construction must use a fixed identity extractor by record type.

```text
LOOP_STEP_RESULT
→ process_id

SLICE_DONE
→ slice_id

STABILITY_RESULT
→ stability_result_id

OPERATOR_RESPONSE
→ operator_response_id

RUNTIME_CONTINUITY_RESULT
→ continuity_result_id

BOUNDARY_EVIDENCE
→ boundary_evidence_id

BOUNDARY_STATE_RECORD
→ boundary_state_record_id

CONTEXT_EVIDENCE
→ context_evidence_id

VOID_EVIDENCE
→ void_evidence_id

DEFERRED_RELATION_RECORD
→ deferred_relation_record_id

TRAJECTORY_EDGE
→ trajectory_edge_id
```

The extractor is repository code.
It is not inferred dynamically from the first field ending in `_id`.

This avoids accidental identity ambiguity.

---

## 7. Envelope Construction Contract

A conforming envelope factory shall:

```text
1. receive one validated canonical Runtime object
2. resolve its registered record type
3. extract its canonical record identity
4. serialize the complete payload in JSON mode
5. calculate the canonical SHA-256 digest
6. extract only contract-defined index fields
7. assign publication_id and publication_order
8. validate the complete PersistentRecordEnvelope
```

The factory must not:

```text
calculate Stability
select OperatorResponse
classify Boundary State
add missing evidence
repair malformed lineage
invent a trajectory identity
replace explicit references with latest records
```

Envelope creation occurs after Runtime construction and before repository commit.

---

## 8. Envelope Reconstruction Contract

A conforming reconstruction operation shall:

```text
1. validate the envelope schema
2. verify supported schema_version
3. resolve record_type through the closed registry
4. recompute canonical_digest from canonical_payload
5. compare stored and computed digest
6. validate indexed identity and lineage consistency
7. validate canonical_payload through the registered Pydantic model
8. return the typed canonical object
```

Failure behavior:

```text
unknown record type
→ RepositorySerializationError

unsupported schema version
→ RepositorySchemaMismatch

digest mismatch
→ RepositoryIntegrityError

record_id mismatch
→ RepositoryIntegrityError

canonical model validation failure
→ RepositorySerializationError
```

Reconstruction must not execute methods or callbacks from stored data.

---

## 9. Publication Group Contract

One `LoopStepResult` publication produces envelopes for:

```text
LoopStepResult
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
BoundaryEvidence[]
BoundaryStateRecord[]
ContextEvidence[]
VoidEvidence[]
DeferredRelationRecord when present
TrajectoryEdge[]
```

All envelopes in the group share:

```text
publication_id
process_id when applicable
loop_id as a query index when applicable
schema_version
runtime_version
```

All envelopes must have distinct `record_id` values.

Publication completeness requires the Process envelope and its mandatory direct records:

```text
LoopStepResult
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
```

The supporting evidence and trajectory envelopes must exactly match the identities referenced by the complete `LoopStepResult`.

A publication group with missing, duplicate, unexpected, or mismatched records must be rejected before commit.

---

## 10. Separate Non-Runtime Persistence Records

The following repository data are required by G-1 but are not canonical Gyro Process objects:

```text
idempotency entry
current-scope pointer
repository schema metadata
```

They shall not be falsely registered as Runtime record types.

### 10.1 IdempotencyEntry

Reference model:

```python
class IdempotencyEntry(CanonicalModel):
    loop_id: str
    idempotency_key: str
    request_digest: str
    process_id: str
    created_at: datetime
```

Its identity scope is:

```text
(loop_id, idempotency_key)
```

### 10.2 CurrentScopePointer

Reference model:

```python
class CurrentScopePointer(CanonicalModel):
    loop_id: str
    process_id: str
    updated_at: datetime
```

It is mutable repository state pointing to an immutable completed Process.

```text
CurrentScopePointer
≠ LoopStepResult
≠ Process history
```

### 10.3 RepositorySchemaMetadata

The persistent implementation shall record at least:

```text
repository_schema_version
created_at
last_migrated_at when applicable
```

Priority G does not yet define automatic migration.

---

## 11. Bounded Page Envelope

G-1 deferred the concrete page model to G-2.

Canonical first implementation:

```python
class Page(CanonicalModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    limit: int
```

Rules:

```text
items are ordered deterministically
limit is bounded
next_cursor is opaque to API clients
no cursor means no additional page
```

Default and maximum values for Priority G:

```text
default limit = 50
maximum limit = 200
```

The first cursor may encode or represent the last returned `publication_order`.
Its external form must not allow clients to inject SQL fragments or arbitrary ordering logic.

A page is a query envelope.
It is not persisted as a Runtime record.

---

## 12. Digest and Identity Separation

The following identities must remain distinct:

```text
record_id
≠ canonical_digest
≠ publication_id
≠ process_id
≠ idempotency request_digest
```

Definitions:

```text
record_id
= canonical object identity

canonical_digest
= integrity digest of one canonical payload

publication_id
= identity shared by one atomic publication group

process_id
= identity of one bounded Gyro Process

request_digest
= canonical digest of one LoopStepRequest for idempotency
```

No one value may be substituted for another merely because all are unique-looking strings.

---

## 13. Time Semantics

The envelope preserves both canonical object time and repository publication order.

```text
canonical object created_at/completed_at
= Runtime-produced timestamp

PersistentRecordEnvelope.created_at
= envelope creation timestamp

publication_order
= deterministic repository commit order
```

The repository must not rewrite canonical timestamps to equal database insertion time.

Query ordering for Priority G uses:

```text
publication_order ascending
```

not timestamp comparison.

---

## 14. Security Boundary

The envelope and registry must prevent:

```text
arbitrary class import
pickle or executable deserialization
dynamic evaluation of stored values
SQL constructed from record_type or cursor text
silent schema downgrade
unvalidated dictionary return
payload/index disagreement
```

Required controls:

```text
closed enum for record_type
parameterized SQL
canonical Pydantic validation
SHA-256 digest verification
bounded query limits
explicit schema-version checks
```

A valid digest does not prove semantic validity.
Canonical model validation remains mandatory.

---

## 15. Compatibility with Current InMemoryStore

The current `InMemoryStore` stores typed objects directly.
It does not need to serialize envelopes internally for Priority G-2 documentation completion.

However, it must conform observably to the same canonical relations:

```text
explicit record identity
complete publication group
record-type-safe retrieval
idempotency scope
current-scope separation
```

During G-3/G-4, the common repository module may introduce envelope factories shared by tests and `SQLiteStore` while preserving the fast direct-object behavior of `InMemoryStore`.

The executor shall continue to receive typed canonical objects from either implementation.

---

## 16. Validation Matrix

| Condition | Required result |
|---|---|
| Known type, valid payload, matching digest and identity | Return typed canonical object |
| Unknown `record_type` | `RepositorySerializationError` |
| Unsupported `schema_version` | `RepositorySchemaMismatch` |
| Digest mismatch | `RepositoryIntegrityError` |
| Envelope `record_id` differs from payload identity | `RepositoryIntegrityError` |
| Indexed lineage differs from payload | `RepositoryIntegrityError` |
| Payload fails canonical Pydantic validation | `RepositorySerializationError` |
| Record not found by explicit ID | Return `None`; API maps not-found error |
| Duplicate `record_id` during publication | `RecordIdentityCollision` |
| Partial publication group | Reject and roll back |

None of these failures may be converted into:

```text
BoundaryState.VOID
VoidEvidence
StabilityStatus.NOT_EVALUABLE
OperatorResponse.DEFER
OperatorResponse.STOP
```

---

## 17. G-2 Acceptance Criteria

G-2 is complete when the following are fixed by contract:

```text
common PersistentRecordEnvelope fields
closed PersistentRecordType registry
canonical JSON and SHA-256 digest rules
explicit identity extraction per record type
payload/index consistency rules
schema and Runtime version fields
publication_id and publication_order semantics
separate idempotency/current-scope models
bounded Page envelope
safe typed reconstruction sequence
repository error mapping
```

Status:

```text
G-2 Canonical Persistent Record Envelope
= COMPLETE

G-3 SQLite Repository Implementation
= READY TO START
```
