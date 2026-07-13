# 61. Priority E — Cross-document Review and Refinement

---

## 1. Purpose

This document completes **Priority E: API Contract and Implementation Readiness** by reviewing the following documents as one contract set:

```text
E-1  docs/52_api_boundary_and_execution_model.md
E-2  docs/53_canonical_request_schema.md
E-3  docs/54_canonical_slice_done_and_evidence_schemas.md
E-4  docs/55_stability_response_and_continuity_schemas.md
E-5  docs/56_validation_and_cross_reference_rules.md
E-6  docs/57_loop_step_execution_contract.md
E-7  docs/58_supporting_endpoint_contract.md
E-8  docs/59_http_status_runtime_status_and_error_model.md
E-9  docs/60_api_implementation_and_test_plan.md
```

The review verifies that these documents form one implementable API contract without redefining Gyro Logic or collapsing Runtime responsibilities.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Priority E defines the API representation of one bounded Runtime execution of this Core.

---

## 2. Final Review Decision

```text
PRIORITY E COMPLETE

API CONTRACT ACCEPTED

READY FOR BOUNDED IMPLEMENTATION
```

No blocking responsibility collapse was found across E-1 through E-9.

The contract is sufficiently defined to begin the first FastAPI / Pydantic implementation described in E-9.

Implementation must remain bounded by the accepted Priority E contract rather than reopening settled API semantics during coding.

---

## 3. Canonical API Relation

The reviewed API relation is:

```text
LoopStepRequest
↓
request validation
↓
explicit reference resolution
↓
current-scope and lineage validation
↓
one bounded Gyro Process
↓
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done {
    representation
    Difference / Deviation
    SliceReadability
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
Memory / Trajectory record preparation
↓
complete result validation
↓
atomic publication
↓
LoopStepResult
```

The following object separation is canonical:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
≠ HTTP status
≠ ApiError
```

---

## 4. Execution Boundary Review

### 4.1 One request, one Process

The accepted execution boundary is:

```text
one valid HTTP request
=
one bounded Gyro Process execution attempt
```

For the first API:

```text
max_slice_operations = 1
```

This rule is consistent across E-1, E-2, E-5, E-6, and E-9.

### 4.2 RESLICE boundary

When the selected response is `RESLICE`:

```text
Process_n
→ OperatorResponse_n = RESLICE
→ prepare SliceRequest_{n+1}
→ return LoopStepResult_n
```

The current request does not recursively execute `Process_{n+1}`.

The prepared request must preserve:

```text
source_type
source_ref
parent_process_ref
parent_slice_ref
requested_by_response_ref
trajectory_ref when applicable
```

### 4.3 Hidden state restriction

The accepted state model remains:

```text
explicit-input hybrid state model
```

A server may retain records, but semantic correctness must remain reconstructable through explicit identities, references, request content, policy identity, and lineage.

The API must not depend on an unidentified:

```text
latest SliceDone
latest Boundary
latest Boundary State
latest Context
latest VoidEvidence
latest Orientation
latest active Process
```

---

## 5. Request Contract Review

The canonical request root is:

```text
LoopStepRequest
├─ request_id
├─ loop_id
├─ structure
├─ slice_request
├─ runtime_limits
├─ idempotency_key
├─ client_trace_id
├─ previous_state_ref
├─ expected_current_scope_ref
├─ policy_ref
├─ request_context
└─ metadata
```

### 5.1 Identity ownership

```text
client-owned correlation identity
= request_id, loop_id, idempotency_key, client_trace_id

server-owned Runtime artifact identity
= process_id, slice_id, evidence IDs, result IDs, record IDs, trajectory edge IDs
```

Client correlation identities must not substitute for server Runtime artifact identities.

### 5.2 Slice request ownership

`OperatorOrientation` and `SlicePolicy` remain inside the Slice execution context.

```text
Operator Orientation
≠ independent Core stage

Slice Policy
≠ independent Core stage
```

### 5.3 Initial Slice and Re-Slice

For the first implementation:

```text
mode = SLICE
→ source_type = RUNTIME_STRUCTURE
→ source_ref = structure.structure_id
```

For `RESLICE`:

```text
source_type identifies a retained Runtime source
+
source_ref resolves to that type
+
complete parent and response lineage exists
```

---

## 6. Evidence Schema Review

The following canonical implementation objects are consistent across E-3 through E-9:

```text
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
```

Naming discipline:

```text
*_evidence
= embedded or directly retained evidence objects

*_records
= identity-bearing classified Runtime records

*_refs
= explicit references to separately retained records
```

### 6.1 Boundary-aware does not mean Boundary-required

A valid `SliceDone` may contain no `BoundaryEvidence`.

```text
Boundary-aware
≠ Boundary-required
```

### 6.2 Readability and confidence separation

The contract consistently separates:

```text
boundary_readability
target_relation_readability
boundary_state_confidence
context_confidence
stability value
response_confidence
```

No one value may silently substitute for another.

### 6.3 VOID refinement

A `VOID` Boundary State requires:

```text
an identifiable relevant Boundary relation
+
the target relation is not sufficiently readable or connectable relative to it
```

If the Boundary distinction itself is unreadable:

```text
retain unclassified Boundary evidence
or unreadable distinction evidence
```

Do not force `VOID`.

### 6.4 VoidEvidence separation

```text
Void as Boundary State
≠ VoidEvidence
≠ DeferredRelationRecord
≠ DEFER
≠ JUMP
≠ STOP
```

`VoidEvidence` must not contain:

```text
deferred
resolved
should_defer
should_jump
should_stop
```

---

## 7. Stability, Response, and Continuity Review

### 7.1 StabilityResult

`StabilityResult` remains a Runtime reading of whether the opened Path is readable as an establishment that can continue.

It is not:

```text
HTTP success
Process completion
OperatorResponse
Boundary readability
Boundary State confidence
application verdict
```

Important:

```text
continuability = true
≠ OperatorResponse = CONTINUE
```

### 7.2 OperatorResponse

Canonical values are exactly:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

The following are legacy compatibility interpretations only and must not appear as canonical enum values:

```text
CHANGE_ORIENTATION
RESLICE_CONTEXT
DEFER_VOID
VOID
```

The sole response owner is:

```text
Loop Controller
```

The following do not select `OperatorResponse`:

```text
SliceEngine
StabilityEngine
ReSliceEngine
MemoryRuntime
TrajectoryCache
Gyro-OOM Damper
Local Inertia
BoundaryStateRecord
ContextEvidence
VoidEvidence
API route layer
validation layer
support endpoint
```

### 7.3 RuntimeContinuityResult

Canonical mapping:

| OperatorResponse | RuntimeContinuityType |
|---|---|
| CONTINUE | DIRECT_CONNECTION |
| ADJUST | ADJUSTED_CONNECTION |
| RESLICE | RESLICE_CONNECTION |
| JUMP | JUMP_RECONNECTION |
| DEFER | DEFERRED_PENDING_RELATION |
| STOP | STOPPED_FOR_CURRENT_SCOPE |

This is a result consistency relation.

`RuntimeContinuityResult` does not select or revise the response.

---

## 8. Cross-reference and Lineage Review

The accepted validation model includes:

```text
field validation
identity validation
reference resolution
lineage and graph validation
cross-object semantic validation
execution-precondition validation
generated-result validation
persistence/publication validation
```

### 8.1 Embedded and referenced identity

When one identity appears both embedded and referenced:

```text
canonical embedded digest
=
canonical resolved digest
```

Conflicting duplicate identity is invalid.

The API must not silently prefer one representation.

### 8.2 Process result identity

The following must identify the same Process:

```text
SliceDone.process_id
StabilityResult.process_id
OperatorResponse.process_id
RuntimeContinuityResult.process_id
```

The following references must resolve exactly:

```text
StabilityResult.slice_id
→ SliceDone.slice_id

OperatorResponse.stability_result_ref
→ StabilityResult.stability_result_id

RuntimeContinuityResult.operator_response_ref
→ OperatorResponse.operator_response_id
```

### 8.3 Reclassification history

Boundary State refinement must preserve prior records through explicit lineage such as:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
supersedes_for_current_scope
reopened_from
invalidated_by_evidence
unreadable_under
```

```text
supersedes_for_current_scope
≠ universal deletion or invalidation
```

---

## 9. Validation versus Runtime Outcome Review

The following are valid Runtime outcomes and may be returned with `200 OK`:

```text
Boundary State = UNKNOWN
Boundary State = VOID
StabilityStatus = NOT_EVALUABLE
StabilityStatus = VOID_RELATED
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

The following are API errors:

```text
malformed request
unsupported canonical enum
missing explicit record
reference type mismatch
invalid lineage
identity conflict
current-scope conflict
Response / Continuity mismatch
incomplete generated result group
internal execution failure
```

The contract must not perform transformations such as:

```text
missing record → VoidEvidence
invalid RESLICE → STOP
current-scope conflict → JUMP
transport timeout → DEFER
rate limit → DEFER
authorization denial → STOP
```

---

## 10. HTTP and ApiError Review

The accepted initial HTTP set is:

```text
200 OK
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
413 Payload Too Large
415 Unsupported Media Type
422 Unprocessable Content
429 Too Many Requests
500 Internal Server Error
503 Service Unavailable
504 Gateway Timeout
```

Canonical separation:

```text
400
= request representation cannot be parsed or interpreted

422
= request representation is parseable but violates canonical schema or object relations
```

A structured `ApiError` remains separate from every Runtime object.

```text
ApiError
≠ StabilityResult
≠ Boundary State
≠ VoidEvidence
≠ OperatorResponse
≠ RuntimeContinuityResult
```

---

## 11. Supporting Endpoint Review

The supporting endpoint contract remains subordinate to `/loop/step`.

Initial endpoints:

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

Implementation priority is defined in E-9.

Important boundaries:

```text
GET /loop/state/{loop_id}
= current-scope view
≠ complete history
```

```text
POST /memory/retrieve
= retrieve explicit records
≠ infer latest evidence
≠ execute Slice
```

```text
POST /memory/compress
= execute an authorized storage operation
≠ choose DEFER, JUMP, or STOP
```

```text
POST /reslice/execute
= execute a previously selected and validated Re-Slice request
≠ decide RESLICE
```

The first implementation may defer `/reslice/execute` and use the canonical `/loop/step` request with `mode = RESLICE` as the primary Re-Slice execution path.

This avoids creating two competing canonical Process execution paths during the first milestone.

---

## 12. Transaction and Publication Review

One `/loop/step` call is one logical transaction boundary.

The implementation must stage generated artifacts until the complete group is valid:

```text
SliceDone
+
StabilityResult
+
OperatorResponse
+
RuntimeContinuityResult
+
required updates, records, and lineage
```

Publication rule:

```text
complete and valid result group
→ publish atomically
→ return success
```

Failure rule:

```text
incomplete or inconsistent result group
→ do not publish a completed Process
→ return structured ApiError
```

A diagnostic failed-attempt record may be retained internally, but it must not masquerade as a valid completed `LoopStepResult`.

---

## 13. Idempotency Review

Recommended idempotency identity:

```text
(loop_id, idempotency_key)
```

Rules:

```text
same key
+
same canonical request digest
+
completed prior result
→ return prior LoopStepResult
```

```text
same key
+
different canonical request digest
→ 409 identity conflict
```

```text
same key and digest already in progress
→ do not start a second Process
```

Idempotent replay must not generate new Runtime artifact identities.

---

## 14. Implementation Readiness Review

The accepted first implementation stack is:

```text
Python
FastAPI
Pydantic
pytest
in-memory repositories
```

Required first milestone endpoints:

```text
POST /loop/step
GET  /health
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

Recommended implementation layers:

```text
API routes
canonical models
validation
Runtime engines
repositories
services
error mapping
```

The repository structure proposed in E-9 is accepted as an implementation starting point, subject to ordinary path-level refinement that does not alter responsibility boundaries.

---

## 15. Required Scenario Coverage

The first bounded implementation must cover at least:

```text
A. readable Boundary / NORMAL / CONTINUE
B. UNKNOWN with retained Context source / RESLICE
C. VOID-related evidence / DEFER
D. conflicting Boundary evidence / ADJUST or JUMP
```

These are deterministic PoC policy scenarios.

They are not universal Gyro Logic mappings.

Required negative coverage includes:

```text
VOID as OperatorResponse
legacy response aliases in canonical enum
Context exists → automatic RESLICE
VoidEvidence exists → automatic DEFER
low Stability → automatic STOP
missing record → VoidEvidence
invalid RESLICE → fallback STOP
timeout → DEFER
current-scope conflict → JUMP or STOP
partial completed Process publication
```

---

## 16. Canonical Source Precedence

When an earlier Priority E assessment statement remains provisional and a later E document fixes the same subject, the later focused contract is authoritative.

Precedence by subject:

```text
execution and state boundary
→ docs/52_api_boundary_and_execution_model.md

request schema
→ docs/53_canonical_request_schema.md

SliceDone and evidence schemas
→ docs/54_canonical_slice_done_and_evidence_schemas.md

Stability, Response, and Continuity schemas
→ docs/55_stability_response_and_continuity_schemas.md

validation and references
→ docs/56_validation_and_cross_reference_rules.md

/loop/step execution
→ docs/57_loop_step_execution_contract.md

support endpoints
→ docs/58_supporting_endpoint_contract.md

HTTP and error semantics
→ docs/59_http_status_runtime_status_and_error_model.md

implementation and testing
→ docs/60_api_implementation_and_test_plan.md
```

`docs/51_priority_e_api_assessment.md` remains the planning and assessment record.

It is not the final schema source where a later focused document exists.

---

## 17. Refinements Fixed by This Review

The following cross-document interpretations are fixed:

### 17.1 Continuity naming

Use:

```text
RuntimeContinuityResult
```

as the canonical object name.

`ContinuityResult` may appear only as an informal shortening in explanatory prose.

### 17.2 Re-Slice execution path

The first canonical path is:

```text
POST /loop/step
with SliceRequest.mode = RESLICE
```

`POST /reslice/execute` is an optional support endpoint after the core path is stable.

It must use the same Process execution and validation semantics rather than creating a second incompatible Runtime contract.

### 17.3 Required collection serialization

Canonical result collection fields must be serialized as arrays, including empty arrays.

```text
[]
≠ not evaluated
```

Evaluation state must be represented explicitly when required.

### 17.4 Metadata restriction

`metadata` is extension space only.

It must not:

```text
override canonical fields
introduce alternate enums
hide identity or lineage
change Response ownership
bypass validation
```

### 17.5 Policy status

Deterministic response rules used by the first implementation must be versioned implementation policy.

They must not be described as Gyro Logic definitions.

---

## 18. Acceptance Criteria Review

Priority E acceptance criteria are satisfied:

```text
1. API execution boundary is fixed.
2. One request equals one bounded Process.
3. Request identity and Runtime artifact identity are separated.
4. Canonical request fields and enums are defined.
5. SliceDone and evidence schemas are defined.
6. Stability, Response, and Continuity are separate.
7. Cross-reference and lineage rules are defined.
8. Runtime outcomes and API errors are separate.
9. Supporting endpoints do not own Response selection.
10. Atomic publication and idempotency are defined.
11. A bounded implementation and test plan exists.
12. No application-layer verdict is introduced into GyroOS.
13. No legacy response alias remains canonical.
14. No valid UNKNOWN, VOID, DEFER, JUMP, or STOP outcome is treated as an automatic HTTP failure.
15. No blocking cross-document responsibility collapse remains.
```

---

## 19. Final Priority E Decision

```text
Priority E
= COMPLETE
```

The next safe activity is bounded API implementation according to:

```text
docs/60_api_implementation_and_test_plan.md
```

The implementation must begin with canonical models, enums, in-memory repositories, validation, and the smallest `/loop/step` path.

It must not begin by expanding into:

```text
persistent distributed storage
background autonomous loops
GyroAuth integration
production authorization policy
complex UI
unbounded Re-Slice execution
```

---

## 20. Summary

Priority E converts the reviewed GyroOS Runtime model into a coherent API contract.

The accepted implementation boundary is:

```text
one explicit request
→ one validated bounded Gyro Process
→ one complete result group
→ one atomic publication
```

The API preserves:

```text
Structure → Slice → Stability
```

while exposing Boundary-aware evidence, Stability, Operator Response, Runtime Continuity, lineage, and failure semantics without collapsing their responsibilities.
