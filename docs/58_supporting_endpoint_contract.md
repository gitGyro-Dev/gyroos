# 58. Supporting Endpoint Contract

---

## 1. Purpose

This document defines **Priority E-7: Supporting Endpoint Contract** for the GyroOS API.

The purpose is to define the bounded read, retrieval, and authorized maintenance endpoints that support:

```text
POST /loop/step
```

without creating a second Runtime decision path.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Supporting endpoints expose or execute already-established Runtime relations.
They do not redefine the Core and do not select `OperatorResponse`.

---

## 2. E-7 Decision Summary

The first API keeps the supporting surface intentionally small.

Canonical initial endpoints:

```text
GET  /health
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /process/{process_id}
GET  /trajectory/{trajectory_id}
GET  /memory/record/{record_id}
POST /memory/retrieve
POST /memory/compress
POST /reslice/execute
```

The primary Runtime endpoint remains:

```text
POST /loop/step
```

Responsibility rule:

```text
/loop/step
= execute one bounded Gyro Process and select one OperatorResponse

supporting endpoint
= read, resolve, retrieve, or execute an already-authorized support operation
```

No supporting endpoint may become an alternate response owner.

---

## 3. Endpoint Categories

Supporting endpoints are divided into four categories.

```text
1. Service observability
2. Runtime read views
3. Record retrieval and storage maintenance
4. Already-selected Re-Slice execution
```

### 3.1 Service observability

```text
GET /health
```

### 3.2 Runtime read views

```text
GET /loop/state/{loop_id}
GET /loop/history/{loop_id}
GET /process/{process_id}
GET /trajectory/{trajectory_id}
GET /memory/record/{record_id}
```

### 3.3 Record retrieval and maintenance

```text
POST /memory/retrieve
POST /memory/compress
```

### 3.4 Already-selected Re-Slice execution

```text
POST /reslice/execute
```

---

## 4. Global Supporting-endpoint Constraints

Every supporting endpoint MUST preserve the following.

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

Every supporting endpoint MUST NOT:

```text
select CONTINUE
select ADJUST
select RESLICE
select JUMP
select DEFER
select STOP
infer a latest object without an explicit current-scope contract
replace complete history with a current view
delete lineage silently
convert missing data into VOID
convert operational failure into STOP
return GyroAuth or other application verdicts
```

A support endpoint may return evidence used by a later `/loop/step` call.
It must not decide how that evidence should be interpreted by the Loop Controller.

---

## 5. Common Read-response Envelope

Read endpoints should return a common envelope.

```python
class ReadResultEnvelope:
    request_trace_id: str | None
    resource_type: str
    resource_id: str
    current_scope_ref: str | None
    record_version: str | None
    retrieved_at: str
    data: dict
    included_records: list[dict]
    included_refs: list[str]
    metadata: dict
```

Rules:

```text
resource_type and resource_id are required
retrieved_at uses timezone-aware UTC format
included_records contain complete typed objects
included_refs contain unique non-empty refs
metadata must not override canonical fields
```

The envelope is transport structure only.
It is not a new Runtime object.

---

## 6. Pagination and Bounded Reads

Collection endpoints must be bounded.

Canonical query parameters:

```text
limit
cursor
order
from_process_index
to_process_index
include_records
include_metadata
```

Initial rules:

```text
1 <= limit <= server_max_limit
order = ASC | DESC
cursor is opaque
```

A caller cannot bypass server limits by sending a larger value.

The response may include:

```text
next_cursor
has_more
returned_count
```

A bounded response must not imply that omitted history does not exist.

```text
not included in this page
≠ absent from history
```

---

## 7. `GET /health`

### 7.1 Purpose

Expose transport and implementation readiness.

It may report:

```text
service availability
runtime version
schema version
storage reachability
reference resolver readiness
policy registry readiness
```

### 7.2 Candidate response

```json
{
  "status": "READY",
  "service": "gyroos-api",
  "runtime_version": "vNext",
  "schema_version": "priority-e",
  "checks": {
    "storage": "READY",
    "reference_resolver": "READY",
    "policy_registry": "READY"
  },
  "checked_at": "2026-07-13T00:00:00Z"
}
```

Canonical health statuses:

```text
READY
DEGRADED
UNAVAILABLE
```

### 7.3 Constraints

`GET /health` MUST NOT expose:

```text
OperatorResponse
Boundary State classification
StabilityResult
current active Runtime evidence
application verdict
```

A degraded service state is not `OperatorResponse = STOP`.

---

## 8. `GET /loop/state/{loop_id}`

### 8.1 Purpose

Return the **current-scope view** for one logical Loop.

```text
current-scope view
≠ complete Loop history
```

### 8.2 Candidate response object

```python
class LoopCurrentScopeView:
    loop_id: str
    current_scope_ref: str
    latest_completed_process_ref: str | None
    active_trajectory_ref: str | None

    active_structure_ref: str | None
    active_slice_ref: str | None
    active_orientation_ref: str | None
    active_slice_policy_ref: str | None

    current_boundary_refs: list[str]
    current_boundary_state_refs: list[str]
    current_context_refs: list[str]
    current_void_refs: list[str]
    deferred_relation_refs: list[str]

    last_operator_response_ref: str | None
    last_continuity_result_ref: str | None

    scope_status: str
    version: str
    updated_at: str
    metadata: dict
```

Candidate `scope_status` values:

```text
ACTIVE
PENDING
STOPPED_FOR_CURRENT_SCOPE
NO_COMPLETED_PROCESS
```

These are view statuses.
They are not OperatorResponse values.

### 8.3 Rules

The endpoint MUST:

```text
return one explicit current_scope_ref
preserve references to current selected records
expose version or equivalent concurrency identity
```

The endpoint MUST NOT:

```text
erase superseded history
imply current record is globally final
invent a current object from an unidentified latest record
select a response from the current state
```

`supersedes_for_current_scope` remains a scoped relation.
It does not mean universal invalidation.

---

## 9. `GET /loop/history/{loop_id}`

### 9.1 Purpose

Return bounded Process and continuity history for one Loop.

### 9.2 Candidate history item

```python
class LoopHistoryItem:
    process_id: str
    process_index: int
    parent_process_ref: str | None

    slice_ref: str
    stability_result_ref: str
    operator_response_ref: str
    continuity_result_ref: str

    trajectory_ref: str | None
    created_record_refs: list[str]

    completed_at: str
    metadata: dict
```

### 9.3 Rules

History ordering must use:

```text
process_index
+
explicit lineage
```

Timestamp alone is insufficient.

The endpoint must preserve:

```text
RESLICE parent linkage
JUMP branch linkage
DEFER pending relation linkage
STOP current-scope boundary
Boundary State reclassification lineage
```

The endpoint must not flatten all branches into one false linear sequence.

---

## 10. `GET /process/{process_id}`

### 10.1 Purpose

Return the complete published result group for one bounded Process.

### 10.2 Canonical content

```text
ProcessRecord
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
UpdateDecision when present
NextProcessPreparation when present
created record refs
trajectory edges
```

### 10.3 Publication rule

Only a complete published Process may be returned as a valid Runtime result.

A reserved or failed internal attempt must not masquerade as a completed Process.

An implementation may expose diagnostics through a separate administrative contract later.
That is outside the first API.

---

## 11. `GET /trajectory/{trajectory_id}`

### 11.1 Purpose

Return a bounded trajectory graph or segment.

Trajectory is not assumed to be a single linear list.

```text
Trajectory
= ordered Process relations
+ branches
+ continuity edges
+ retained evidence lineage
```

### 11.2 Candidate response

```python
class TrajectoryView:
    trajectory_id: str
    current_scope_ref: str | None

    process_refs: list[str]
    slice_refs: list[str]
    continuity_refs: list[str]
    trajectory_edges: list[TrajectoryEdge]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]
    deferred_relation_refs: list[str]

    branch_refs: list[str]
    resolution_level: str
    storage_tier: str

    next_cursor: str | None
    metadata: dict
```

### 11.3 Constraints

The endpoint MUST preserve:

```text
branch points
JUMP reconnection
RESLICE source lineage
DEFER pending relation
STOP current-scope boundary
Boundary State reclassification
coexisting or conflicting readings
```

Trajectory similarity returned by this endpoint is not automatically Dynamic Equivalence.

---

## 12. `GET /memory/record/{record_id}`

### 12.1 Purpose

Return one typed retained Runtime record.

Possible record types include:

```text
RuntimeStructureRecord
SliceDoneRecord
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityRecord
OperatorResponseRecord
ContinuityRecord
DeferredRelationRecord
TrajectoryRecord
```

### 12.2 Candidate response

```python
class MemoryRecordResult:
    record_id: str
    record_type: str
    record_version: str
    resolution_level: str
    storage_tier: str
    content_digest: str
    record: dict
    lineage_refs: list[str]
    retrieved_at: str
    metadata: dict
```

### 12.3 Rules

The endpoint MUST NOT:

```text
infer record type from ID prefix only
return a different type under the requested identity
silently substitute a summary for full data without declaring resolution_level
mark VoidEvidence as deferred or resolved
```

If only reduced-resolution content is available, that fact must be explicit.

---

## 13. `POST /memory/retrieve`

### 13.1 Purpose

Materialize or retrieve explicitly identified retained records for inspection or later use.

It does not select `RESLICE`.

### 13.2 Candidate request

```python
class MemoryRetrieveRequest:
    request_id: str
    record_refs: list[str]
    requested_resolution: str | None
    include_dependencies: bool
    max_dependency_depth: int
    client_trace_id: str | None
    metadata: dict
```

Candidate resolution values:

```text
FULL
SUMMARY
VECTOR
POINTER
BEST_AVAILABLE
```

### 13.3 Candidate response

```python
class MemoryRetrieveResult:
    request_id: str
    retrieved_records: list[MemoryRecordResult]
    unresolved_refs: list[str]
    dependency_refs: list[str]
    bounded_by_limits: bool
    retrieved_at: str
    metadata: dict
```

### 13.4 Rules

The endpoint MUST:

```text
resolve only explicit refs
respect dependency and payload limits
declare unresolved refs
preserve original identity and content digest
```

It MUST NOT:

```text
select latest Context automatically
create an OperatorResponse
execute Slice
classify Boundary State
convert retrieval failure into VOID
```

A missing record is an API/resource error or an explicitly unresolved retrieval result according to E-8.
It is not VoidEvidence.

---

## 14. `POST /memory/compress`

### 14.1 Purpose

Execute an explicitly authorized storage-resolution operation.

```text
memory compression
≠ forgetting
≠ Operator Response
```

### 14.2 Candidate request

```python
class MemoryCompressRequest:
    request_id: str
    target_refs: list[str]
    target_resolution: str
    expected_record_versions: dict[str, str]
    authorization_ref: str | None
    preserve_dependency_depth: int
    dry_run: bool
    client_trace_id: str | None
    metadata: dict
```

Canonical target resolutions:

```text
SUMMARY
VECTOR
POINTER
```

`FULL` is not a compression target.

### 14.3 Candidate result

```python
class MemoryCompressResult:
    request_id: str
    operation_id: str
    dry_run: bool
    compressed_refs: list[str]
    unchanged_refs: list[str]
    rejected_refs: list[str]
    preservation_refs: list[str]
    before_versions: dict[str, str]
    after_versions: dict[str, str]
    completed_at: str
    metadata: dict
```

### 14.4 Preservation rules

Compression must preserve, directly or by reference:

```text
identity
record type
content digest or derivation digest
source lineage
parent lineage
Boundary State reclassification lineage
Trajectory branch points
OperatorResponse and continuity references
VoidEvidence traceability
DeferredRelationRecord separation
```

Compression MUST NOT:

```text
delete unresolved evidence silently
remove Δ lineage silently
turn DEFER into a storage status
turn low Local Inertia into automatic deletion
select JUMP or STOP
```

### 14.5 Concurrency

When `expected_record_versions` are supplied, each target version must match before mutation.
A mismatch is a storage/current-state conflict.

It is not a Runtime `ADJUST` or `STOP` result.

---

## 15. `POST /reslice/execute`

### 15.1 Purpose

Execute a Re-Slice request that has already been selected and prepared by a prior `OperatorResponse = RESLICE`.

```text
/reslice/execute
= execute an already-authorized Re-Slice request
≠ decide RESLICE
```

### 15.2 Initial recommendation

The preferred client flow remains:

```text
POST /loop/step
with SliceRequest.mode = RESLICE
```

`POST /reslice/execute` is an optional low-level convenience endpoint.
It must reuse the same canonical execution and validation path as `/loop/step`.

It must not implement a separate Re-Slice semantic pipeline.

### 15.3 Candidate request

```python
class ReSliceExecuteRequest:
    request_id: str
    loop_id: str
    idempotency_key: str | None

    prepared_request: SliceRequest
    runtime_limits: RuntimeLimits

    expected_current_scope_ref: str | None
    previous_state_ref: str | None
    policy_ref: str | None

    client_trace_id: str | None
    metadata: dict
```

Required conditions:

```text
prepared_request.mode = RESLICE
prepared_request.source_ref resolves
prepared_request.parent_process_ref resolves
prepared_request.parent_slice_ref resolves
prepared_request.requested_by_response_ref resolves
referenced OperatorResponse.response_type = RESLICE
submitted request matches prior prepared or authorized request
max_slice_operations = 1
```

### 15.4 Execution result

The result must be the same canonical `LoopStepResult` shape used by `/loop/step`.

The endpoint executes:

```text
one HTTP request
=
one bounded Re-Slice Process
```

If that Process selects another `RESLICE`, it prepares another request and returns.
It does not recurse.

### 15.5 Prohibited behavior

`POST /reslice/execute` MUST NOT:

```text
accept ContextEvidence existence as sufficient authorization
accept VoidEvidence existence as sufficient authorization
create a synthetic prior RESLICE response
bypass lineage validation
execute multiple Re-Slices recursively
use a separate OperatorResponse vocabulary
```

---

## 16. Deferred Relation Access

A separate endpoint such as:

```text
GET /deferred/{deferred_relation_id}
```

may be added later.

It is not required for the first API because a `DeferredRelationRecord` can be retrieved through:

```text
GET /memory/record/{record_id}
```

A future deferred-relation endpoint must not automatically resume or Re-Slice the relation.

```text
retrieve pending relation
≠ select RESLICE
≠ select CONTINUE
```

---

## 17. Boundary and Evidence Query Endpoints

Dedicated endpoints such as:

```text
GET /boundary/{boundary_id}
GET /context/{context_evidence_id}
GET /void/{void_evidence_id}
```

are deferred from the first API.

The first implementation should use:

```text
GET /memory/record/{record_id}
```

This avoids expanding the API surface before common record semantics are stable.

If dedicated endpoints are added later, they remain typed read views only.
They must not select OperatorResponse.

---

## 18. Current-scope Mutation Endpoints

The first API does not expose a generic endpoint such as:

```text
POST /loop/state/set
POST /loop/current/replace
```

because unrestricted current-scope mutation could bypass:

```text
Process execution
Slice lineage
OperatorResponse ownership
RuntimeContinuityResult
Trajectory preservation
```

Current-scope changes should initially occur only through atomically published `/loop/step` results or explicitly defined storage-maintenance contracts.

---

## 19. Deletion Endpoints

The first API does not expose generic Runtime record deletion.

Not included:

```text
DELETE /memory/record/{record_id}
DELETE /trajectory/{trajectory_id}
DELETE /loop/{loop_id}
```

Deletion requires separate retention, legal, privacy, and lineage-preservation design.

Archive or resolution reduction is not deletion.

```text
COLD storage
POINTER representation
current-scope supersession
≠ record deletion
```

---

## 20. Idempotency for Supporting Writes

The following endpoints should support idempotency:

```text
POST /memory/retrieve
POST /memory/compress
POST /reslice/execute
```

The recommended identity scope is endpoint-specific:

```text
(endpoint, operation scope, idempotency_key)
```

For `POST /reslice/execute`, the scope should also include `loop_id`.

Same key and same canonical request digest may return the previous completed result.
Same key with different canonical content is a conflict.

Read endpoints are naturally repeatable but may return a newer declared record version unless the caller requests or supplies an explicit version.

---

## 21. Authorization Boundary

Authorization is transport and operation permission.
It is not GyroOS Operator Response.

Examples:

```text
caller may read Loop history
caller may retrieve specified record
caller may execute authorized compression
caller may execute prepared Re-Slice request
```

Authorization failure must not be represented as:

```text
Boundary State = VOID
StabilityStatus = UNSTABLE
OperatorResponse = STOP
RuntimeContinuityType = STOPPED_FOR_CURRENT_SCOPE
```

Exact HTTP status and error codes are defined in Priority E-8.

---

## 22. Error Boundary

Supporting endpoints must return structured API errors for conditions such as:

```text
resource not found
wrong record type
version conflict
invalid cursor
unsupported resolution
missing Re-Slice authorization lineage
payload limit exceeded
storage operation rejected
implementation failure
```

They must not synthesize Runtime result objects to represent API failures.

Examples:

```text
missing ContextEvidence record
≠ VoidEvidence
```

```text
compression conflict
≠ ADJUST
```

```text
Re-Slice authorization missing
≠ STOP
```

---

## 23. Audit and Observability

Write-like support operations should record:

```text
operation_id
request_id
caller identity reference when available
canonical request digest
target refs
before versions
after versions
authorization ref
started_at
completed_at
outcome
```

Audit records are operational evidence.
They are not Slice evidence unless explicitly introduced into a later `LoopStepRequest` through a documented evidence contract.

`client_trace_id` and transport trace IDs must not change Runtime semantics.

---

## 24. API Surface for the First Implementation

### Required

```text
POST /loop/step
GET  /health
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

### Recommended

```text
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /trajectory/{trajectory_id}
POST /memory/retrieve
```

### Optional after the core path is stable

```text
POST /memory/compress
POST /reslice/execute
```

The implementation should not block the main PoC on every optional support endpoint.

---

## 25. Acceptance Criteria

Priority E-7 is complete when:

```text
1. /loop/step remains the only initial OperatorResponse selection endpoint.
2. Read endpoints distinguish current-scope view from complete history.
3. Process retrieval returns a complete published result group.
4. Trajectory reads preserve branches and continuity edges.
5. Memory retrieval resolves only explicit references.
6. Memory compression preserves identity, lineage, and traceability.
7. /reslice/execute requires a prior RESLICE authorization relation.
8. No supporting endpoint converts operational failure into a Runtime response.
9. No generic current-state replacement or deletion endpoint bypasses Process lineage.
10. All supporting writes are bounded, version-aware, and idempotency-capable.
```

---

## 26. E-7 Decision

```text
Priority E-7
Status: ACCEPTED
```

The supporting API remains subordinate to:

```text
POST /loop/step
```

The canonical responsibility boundary is:

```text
/loop/step
= execute one bounded Process and select one OperatorResponse

supporting endpoints
= inspect, resolve, retrieve, compress, or execute an already-selected operation
```

Next:

```text
Priority E-8
= HTTP Status, Runtime Status, and Error Model
```
