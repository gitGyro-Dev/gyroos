# 52. API Boundary and Execution Model

---

## 1. Purpose

This document defines **Priority E-1: API Boundary and Execution Model** for GyroOS.

The purpose is to fix the execution ownership, state boundary, identity boundary, and replay boundary of the GyroOS API before request and response schemas are finalized.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The API represents this Core in Runtime.

It does not redefine it.

---

## 2. Decision Summary

The first GyroOS API uses the following execution model:

```text
one HTTP request
=
one bounded Gyro Process
```

The primary endpoint remains:

```text
POST /loop/step
```

The state model is:

```text
explicit-input hybrid state model
```

This means:

```text
current Runtime Structure and SliceRequest are explicit request inputs
+
retained Runtime records may be resolved through explicit references
+
all records created by the current step are returned directly or by explicit reference
+
semantic correctness does not depend on invisible global state
```

A server may retain state for efficiency.

However, hidden retained state must never become the only source of meaning for a valid step.

---

## 3. API Responsibility Boundary

`POST /loop/step` owns the orchestration of one bounded Runtime step.

It may:

```text
validate one LoopStepRequest
resolve explicit retained references
create one Process identity
execute one Slice
produce one SliceDone
read one StabilityResult
select one OperatorResponse
produce one RuntimeContinuityResult
prepare one next request when required
persist or return records produced by the step
```

It must not:

```text
execute an unbounded Gyro Loop
recursively execute all future Processes
hide response selection inside a support endpoint
convert Runtime outcomes into application verdicts
collapse SliceDone, StabilityResult, OperatorResponse, or RuntimeContinuityResult
```

---

## 4. Canonical Execution Chain

The endpoint represents the following Runtime relation:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  ↓
  slice-done {
    representation
    Difference / Deviation
    BoundaryEvidence
    BoundaryStateRecord
    ContextEvidence
    VoidEvidence
  }
}
↓
StabilityResult
↓
Loop Controller / OperatorResponse
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
RuntimeContinuityResult
↓
Memory / Trajectory preservation
```

The following remain distinct API objects:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

---

## 5. One Request Equals One Process

The first implementation must execute exactly one Gyro Process per `/loop/step` call.

```text
LoopStepRequest_n
↓
Gyro Process_n
↓
LoopStepResult_n
```

If the selected OperatorResponse is `RESLICE`, the response may include:

```text
next_request
source references
parent lineage
runtime limits for the next step
```

But the current call does not automatically execute the next Process.

Correct:

```text
Process_n
→ RESLICE
→ prepare SliceRequest_{n+1}
→ return response
```

Incorrect:

```text
Process_n
→ RESLICE
→ recursively execute Process_{n+1}
→ recursively execute Process_{n+2}
→ ...
```

This bounded rule prevents hidden recursion and preserves observable Process boundaries.

---

## 6. Hybrid State Model

The API supports both embedded input and explicit references.

### Embedded input

The request may carry the current Runtime Structure and Slice execution context directly.

```text
RuntimeStructureInput
SliceRequest
OperatorOrientation
SlicePolicy
RuntimeLimits
```

### Explicit retained references

The request may also refer to retained records such as:

```text
prior SliceDone
ContextEvidence
BoundaryEvidence
BoundaryStateRecord
VoidEvidence
Trajectory segment
Deferred relation
Prior Runtime state
```

### Rule

```text
embedded input
+
explicit references
=
valid hybrid request
```

But:

```text
hidden server state without explicit identity
≠ sufficient semantic contract
```

---

## 7. Stateful and Stateless Compatibility

The contract must support two implementation modes.

### Stateless-compatible mode

The client sends all data needed for the current step.

```text
request contains current Structure
+
request contains SliceRequest
+
all referenced evidence is embedded or externally resolvable
```

### Stateful-assisted mode

The server stores Runtime records and resolves explicit references.

```text
loop_id
previous_state_ref
trajectory_ref
record refs
```

may be used to retrieve retained state.

### Invariant

Both modes must produce semantically equivalent step behavior when supplied with equivalent evidence.

```text
storage strategy
≠ Runtime meaning
```

---

## 8. Hidden State Restriction

A server may store:

```text
LoopState
Memory Runtime records
Trajectory records
current-scope pointers
idempotency records
```

However, the API must expose enough information to reconstruct the step.

At minimum, the response must make traceable:

```text
process identity
source identity
Slice identity
orientation identity
policy identity
parent lineage
considered evidence references
selected response
continuity result
created record references
```

The API must not rely on an undocumented mutable global variable such as:

```text
current active loop
current implicit orientation
latest hidden SliceDone
latest hidden Context
```

without explicit identity in the request or response.

---

## 9. Identity Ownership

Identity ownership is divided between client-provided correlation identity and server-generated Runtime identity.

### Client-provided or client-selected identity

Candidate fields:

```text
request_id
loop_id
idempotency_key
client_trace_id
```

These identify the request context or logical loop.

### Server-generated Runtime identity

Candidate fields:

```text
process_id
slice_id
stability_result_id
operator_response_id
continuity_result_id
record_id
trajectory_edge_id
```

These identify Runtime artifacts produced by execution.

### Rule

The first implementation should not require clients to generate internal Runtime artifact IDs.

```text
client owns correlation identity
server owns execution artifact identity
```

Explicit imported records may retain externally supplied IDs only when validation confirms uniqueness and provenance.

---

## 10. Loop Identity and Process Identity

`loop_id` and `process_id` must remain distinct.

```text
loop_id
= logical Gyro Loop or execution thread identity

process_id
= one bounded Gyro Process execution identity
```

One loop may contain multiple Processes.

```text
loop_001
├─ process_001
├─ process_002
└─ process_003
```

A `/loop/step` request may reuse the same `loop_id` across calls.

Each successful execution creates a new `process_id` unless the request is an idempotent replay of an already completed step.

---

## 11. Idempotency and Retry Boundary

Network retry must not silently create duplicate Process records.

The request should support an optional:

```text
idempotency_key
```

Candidate rule:

```text
same loop_id
+
same idempotency_key
+
same canonical request content
=
return the previously completed LoopStepResult
```

Conflict rule:

```text
same loop_id
+
same idempotency_key
+
different canonical request content
=
identity conflict
```

The likely HTTP result for this conflict is:

```text
409 Conflict
```

Exact error codes are finalized in E-8.

---

## 12. Replay and Reconstruction

The API should support deterministic reconstruction where policy and implementation permit it.

A replayable step requires references to:

```text
Runtime Structure
SliceRequest
OperatorOrientation
SlicePolicy
Runtime limits
resolved retained evidence
policy version
implementation version
```

The response should record:

```text
input_snapshot_ref or request_digest
policy_ref or policy_version
runtime_version
created_at
parent refs
```

Replay does not require identical wall-clock metadata.

Replay means:

```text
same semantic inputs and policy
→ equivalent Runtime decision path
```

It does not promise bit-for-bit identity when nondeterministic implementations are explicitly enabled.

---

## 13. Transaction Boundary

One `/loop/step` execution should be treated as one logical transaction.

The transaction includes:

```text
request validation
reference resolution
Process creation
Slice execution
SliceDone creation
Stability reading
OperatorResponse selection
RuntimeContinuityResult creation
record persistence
response construction
```

The implementation should avoid returning a successful result when only part of the required Runtime record set was persisted.

Candidate atomicity rule:

```text
required step records persist together
or
no completed Process is published
```

Optional compression, cold archive, and later materialization remain outside this immediate transaction.

---

## 14. Failure Boundary

The API must distinguish failure before Process execution from a valid Runtime outcome.

### API or execution failure

Examples:

```text
malformed request
unsupported enum
missing referenced record
identity conflict
invalid lineage
internal implementation failure
```

These produce structured API errors.

### Valid Runtime outcome

Examples:

```text
Boundary State = UNKNOWN
Boundary State = VOID
Stability = not_evaluable
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

These are valid `LoopStepResult` outcomes and are not automatically HTTP errors.

---

## 15. Support Endpoint Boundary

Support endpoints remain subordinate to `/loop/step`.

Potential support endpoints include:

```text
GET /loop/state/{loop_id}
GET /loop/history/{loop_id}
GET /trajectory/{trajectory_id}
GET /memory/record/{record_id}
POST /reslice/execute
POST /memory/retrieve
POST /memory/compress
```

They must not become alternate decision owners.

Examples:

```text
POST /reslice/execute
= execute an already selected Re-Slice request
≠ decide RESLICE
```

```text
POST /memory/compress
= perform an authorized storage operation
≠ choose DEFER, JUMP, or STOP
```

```text
GET /loop/state/{loop_id}
= return a current-scope view
≠ erase or replace complete history
```

---

## 16. Application Boundary

GyroOS returns Runtime evidence and Runtime responses.

It does not return application-specific verdicts such as:

```text
authenticated
access_denied
fraud
malware
approved
rejected
```

GyroOS may return:

```text
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
Boundary evidence
Trajectory evidence
```

GyroAuth or another application may interpret these results within its own layer.

```text
GyroOS Runtime result
≠ GyroAuth authentication result
```

---

## 17. Concurrency Boundary

Multiple requests may target the same `loop_id`.

The first implementation should not silently accept conflicting concurrent updates to the same current scope.

Candidate rule:

```text
previous_state_ref or expected_version matches
→ execution may proceed

previous_state_ref or expected_version is stale
→ state conflict
```

The likely result is:

```text
409 Conflict
```

Exact fields and validation are finalized in E-2 and E-5.

Different independent `loop_id` values may execute concurrently.

---

## 18. Bounded Execution Limits

Every step must have explicit bounded limits.

Candidate Runtime limits include:

```text
max_slice_operations
max_evidence_items
max_reference_resolution_depth
max_reslice_depth
max_trajectory_edges_created
max_execution_time_ms
max_memory_materialization_items
```

For the first implementation:

```text
max_slice_operations = 1
```

because one `/loop/step` executes one Process and one Slice.

A `RESLICE` response prepares another request rather than executing it recursively.

---

## 19. Initial Persistence Decision

The API contract permits persistence but does not require a specific database.

The first implementation may use:

```text
in-memory repository
```

provided that:

```text
identities are explicit
references are validated
history is not overwritten
current-scope view is distinct from full history
retry behavior is testable
```

A later storage implementation may replace the in-memory repository without changing the API semantics.

---

## 20. E-1 Accepted Decisions

Priority E-1 confirms the following:

```text
1. POST /loop/step remains the primary endpoint.
2. One HTTP request executes one bounded Gyro Process.
3. One step executes one Slice operation in the first implementation.
4. RESLICE prepares the next SliceRequest and does not recurse in the same call.
5. The API uses an explicit-input hybrid state model.
6. Retained state is accessed only through explicit identity or references.
7. Hidden server state is optional and must not be semantically required.
8. loop_id and process_id remain distinct.
9. Client correlation IDs and server Runtime artifact IDs have separate ownership.
10. Idempotency is part of the API boundary.
11. One step is one logical persistence transaction.
12. Runtime outcomes remain separate from API errors.
13. Support endpoints do not own OperatorResponse selection.
14. GyroOS does not return application-specific verdicts.
15. Concurrency conflicts must be detected rather than silently overwritten.
```

---

## 21. Deferred Decisions

The following are intentionally deferred:

```text
exact required and optional request fields
exact enum definitions
exact Pydantic model syntax
exact idempotency storage duration
exact concurrency version field name
exact persistence backend
exact HTTP error codes and error body
exact support endpoint set
```

These are addressed in E-2 through E-9.

---

## 22. Acceptance Criteria

Priority E-1 is complete when:

```text
API execution ownership is explicit.
One request / one Process is fixed.
Re-Slice recursion is excluded from the first endpoint contract.
Stateful and stateless-compatible execution are both supported.
Hidden state cannot replace explicit lineage.
ID ownership is separated.
Retry and concurrency boundaries are identified.
Support endpoint responsibility is constrained.
Application-layer verdicts remain outside GyroOS.
```

---

## 23. Priority E-1 Decision

Status:

```text
ACCEPTED
```

The API boundary is now stable enough to define the canonical request schema.

Next:

```text
Priority E-2
= Canonical Request Schema
```
