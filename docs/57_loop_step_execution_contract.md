# 57. `/loop/step` Execution Contract

---

## 1. Purpose

This document defines **Priority E-6: `/loop/step` Execution Contract** for the GyroOS API.

The purpose is to fix the ordered execution responsibility, transaction boundary, publication boundary, idempotency behavior, and bounded completion semantics of:

```text
POST /loop/step
```

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The endpoint represents one bounded Runtime execution of this Core.
It does not execute an unbounded Loop and does not redefine Gyro Logic.

---

## 2. E-6 Decision Summary

The canonical execution rule is:

```text
one valid HTTP request
=
one bounded Gyro Process execution attempt
```

For the first API:

```text
max_slice_operations = 1
```

A successful non-replay call creates exactly one new `process_id`.

A `RESLICE` OperatorResponse may prepare a next `SliceRequest`, but the current call must not execute that next Process.

```text
Process_n
→ OperatorResponse_n = RESLICE
→ prepare SliceRequest_{n+1}
→ return LoopStepResult_n
```

The endpoint must not recursively continue through future Processes.

---

## 3. Endpoint Responsibility

`POST /loop/step` owns orchestration of one bounded Runtime step.

It owns:

```text
request admission
request validation coordination
idempotency check
explicit reference resolution
current-scope concurrency check
Process identity creation
one Slice execution
SliceDone creation
StabilityResult reading
OperatorResponse selection through LoopController
RuntimeContinuityResult creation
optional bounded update application
optional next Process preparation
Memory and Trajectory record preparation
cross-object result validation
atomic publication or complete direct return
```

It does not own:

```text
application verdicts
GyroAuth decisions
unbounded loop execution
implicit latest-object selection
background autonomous continuation
support-endpoint response selection
silent evidence deletion
```

---

## 4. Canonical Execution Pipeline

The endpoint executes the following ordered pipeline:

```text
Phase 0  Transport admission
Phase 1  Request deserialization and shape validation
Phase 2  Canonical request digest and idempotency check
Phase 3  Explicit reference resolution
Phase 4  Current-scope and lineage precondition validation
Phase 5  Process identity reservation
Phase 6  Slice execution
Phase 7  SliceDone validation and staging
Phase 8  Stability reading
Phase 9  OperatorResponse selection
Phase 10 RuntimeContinuityResult construction
Phase 11 Optional bounded update and next-request preparation
Phase 12 Memory / Trajectory record preparation
Phase 13 Complete result-group validation
Phase 14 Atomic publication
Phase 15 LoopStepResult serialization and return
```

The order is mandatory for the first implementation.

An implementation may optimize internal calls, but it must preserve the same responsibility and publication boundaries.

---

## 5. Phase 0 — Transport Admission

Transport admission checks conditions that exist before canonical Runtime request validation.

Examples:

```text
supported content type
payload size within transport limit
request body readable
endpoint available
caller permitted to invoke endpoint
```

Failure in this phase produces an API error.

It must not create:

```text
process_id
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
```

Transport rejection is not a Runtime `STOP` result.

---

## 6. Phase 1 — Request Deserialization and Shape Validation

Deserialize the request into the canonical `LoopStepRequest` schema.

Validate:

```text
required fields
field types
canonical enum values
numeric ranges
collection limits
non-null requirements
metadata restrictions
runtime limits
```

Canonical request enums include:

```text
SliceMode:
SLICE | RESLICE
```

Compatibility aliases such as:

```text
RESLICE_CONTEXT
CHANGE_ORIENTATION
DEFER_VOID
```

must not pass canonical request validation.

No Process artifact is created during this phase.

---

## 7. Phase 2 — Canonical Digest and Idempotency

After request-shape validation, compute the canonical request digest using the documented canonicalization version.

Candidate identity scope:

```text
(loop_id, idempotency_key)
```

### 7.1 No idempotency key

When `idempotency_key` is absent:

```text
a valid accepted execution
→ may create a new Process
```

The caller accepts normal retry risk unless another transport mechanism prevents duplication.

### 7.2 Matching completed replay

```text
same loop_id
+
same idempotency_key
+
same canonical request digest
+
previous completed result exists
=
return previous LoopStepResult
```

No new Process, Slice, StabilityResult, OperatorResponse, or continuity record is created.

The response should expose replay observability, for example:

```text
replayed = true
original_process_id
original_completed_at
```

These fields do not change Runtime semantics.

### 7.3 Conflicting reuse

```text
same loop_id
+
same idempotency_key
+
different canonical request digest
=
idempotency conflict
```

This is an API conflict, not an OperatorResponse.

### 7.4 In-progress duplicate

When the same key and digest are already executing, the implementation must not start a second Process.

It may:

```text
return a bounded conflict or in-progress API error
or
return the completed result if completion becomes available within a documented synchronous boundary
```

The first implementation should prefer a clear conflict response rather than hidden request waiting.

Exact HTTP mappings are defined in Priority E-8.

---

## 8. Phase 3 — Explicit Reference Resolution

Resolve every non-null explicit reference required for the current step.

Potential references include:

```text
source_ref
previous_state_ref
expected_current_scope_ref
trajectory_ref
context_refs
boundary_refs
boundary_state_refs
void_refs
continuity_refs
parent_process_ref
parent_slice_ref
requested_by_response_ref
policy_ref
```

Resolution rules:

```text
one reference
→ exactly one compatible record
```

The endpoint must not resolve an unidentified:

```text
latest SliceDone
latest Boundary
latest Context
latest Void evidence
latest Orientation
latest active Process
```

A cache may accelerate resolution, but cache location must not change record identity or meaning.

Missing or type-incompatible references fail before Process execution begins.

---

## 9. Phase 4 — Current-scope and Lineage Preconditions

Before Process identity creation, validate execution preconditions.

### 9.1 Initial Slice

For the first API:

```text
slice_request.mode = SLICE
→ source_type = RUNTIME_STRUCTURE
→ source_ref = structure.structure_id
```

### 9.2 Re-Slice

```text
slice_request.mode = RESLICE
```

requires:

```text
source_type identifies a retained Runtime source
source_ref resolves to the declared source type
parent_process_ref resolves
parent_slice_ref resolves
requested_by_response_ref resolves
referenced OperatorResponse.response_type = RESLICE
submitted request matches the request prepared or authorized by that response
```

### 9.3 Current-scope concurrency

When `expected_current_scope_ref` is present:

```text
expected_current_scope_ref
=
server current-scope ref
```

must hold.

A mismatch is an API conflict.
It must not be converted into:

```text
STOP
DEFER
JUMP
```

### 9.4 Limits

Client limits must not exceed server hard limits.

The first API requires:

```text
max_slice_operations = 1
```

Failure of any precondition prevents Process publication.

---

## 10. Phase 5 — Process Identity Reservation

Only after all pre-execution validation succeeds may the runtime reserve a new server-owned `process_id`.

Candidate Process record fields:

```text
process_id
loop_id
request_id
request_digest
process_index
source_type
source_ref
parent_process_ref
status
started_at
runtime_version
policy_ref
```

Initial internal status may be:

```text
RESERVED
```

The reserved Process is not yet a completed or externally published Runtime result.

A reserved identity must not be reused for another canonical request.

If execution later fails, the implementation may retain a diagnostic failed-attempt record, but it must not expose that record as a valid completed `LoopStepResult`.

---

## 11. Phase 6 — Slice Execution

Execute exactly one Slice operation using:

```text
RuntimeStructureInput
SliceRequest
OperatorOrientation
SlicePolicy
resolved retained evidence
RuntimeLimits
```

The internal Slice relation remains:

```text
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
```

Operator Orientation and Slice Policy are internal Runtime distinctions of Slice.
They are not independent Core stages.

The Slice Engine may produce:

```text
representation
Difference / Deviation
SliceReadability
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
```

It must not select:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

The Slice Engine must stop after one Slice operation for the first API.

---

## 12. Phase 7 — SliceDone Validation and Staging

Construct one `SliceDone` using server-owned identity.

Validate before continuing:

```text
slice_id uniqueness
process_id consistency
source identity consistency
orientation_ref consistency
slice_policy_ref consistency
Boundary evidence validity
Boundary State lineage validity
Context evidence validity
Void evidence validity
embedded/reference consistency
collection and payload limits
```

Important:

```text
Boundary-aware
≠ Boundary-required
```

A valid Slice may produce no BoundaryEvidence.

A `VOID` Boundary State is valid only when:

```text
relevant Boundary is identifiable
+
target relation is unreadable or unconnectable relative to it
```

If the Boundary itself is unreadable, stage unclassified Boundary evidence rather than forcing `VOID`.

The valid `SliceDone` remains staged and unpublished until the complete result group passes validation.

---

## 13. Phase 8 — Stability Reading

The Stability Engine reads one `StabilityResult` from the established `SliceDone` and applicable retained evidence.

```text
SliceDone
↓
StabilityResult
```

The Stability Engine may return:

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED
```

These are valid Runtime statuses.

The Stability Engine does not select OperatorResponse.

```text
continuability = true
≠ OperatorResponse = CONTINUE
```

Validate:

```text
StabilityResult.process_id = current process_id
StabilityResult.slice_id = SliceDone.slice_id
normalized numeric values are finite and within range
all evidence refs resolve
reason is present
```

---

## 14. Phase 9 — OperatorResponse Selection

The Loop Controller is the sole owner of OperatorResponse selection.

Decision inputs may include:

```text
SliceDone
StabilityResult
Difference / Deviation
Boundary readability
Boundary State records
ContextEvidence
VoidEvidence
Trajectory history
recoverability
retainability
Re-Slice viability
reconstruction necessity
Runtime limits
DamperPressureEvidence
Local Inertia evidence
policy
```

Canonical response values are:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

The policy must not be represented as universal Gyro Logic mappings such as:

```text
NORMAL → CONTINUE
UNKNOWN → RESLICE
VOID → DEFER
low Stability → STOP
large Deviation → JUMP
```

A deterministic first implementation is permitted when explicitly identified as implementation policy.

The resulting OperatorResponse must expose:

```text
reason
considered_evidence_refs
decisive_evidence_refs
conflicting_evidence_refs
response_confidence when implemented
selected_by_policy_ref
```

---

## 15. Phase 10 — RuntimeContinuityResult Construction

Construct the continuity relation resulting from the selected response.

Canonical mapping:

```text
CONTINUE → DIRECT_CONNECTION
ADJUST   → ADJUSTED_CONNECTION
RESLICE  → RESLICE_CONNECTION
JUMP     → JUMP_RECONNECTION
DEFER    → DEFERRED_PENDING_RELATION
STOP     → STOPPED_FOR_CURRENT_SCOPE
```

The continuity object records the result of the selected response.
It does not select or reinterpret the response.

Required consistency includes:

```text
continuity.process_id = current process_id
continuity.operator_response_ref = operator_response_id
continuity type matches response type
source_ref resolves
pending and termination flags match the continuity type
```

Special rules:

```text
DEFER
→ pending = true
→ terminated_for_current_scope = false
```

```text
STOP
→ terminated_for_current_scope = true
→ next_request = null
```

```text
JUMP
→ branch or reconnection lineage is explicit
```

---

## 16. Phase 11 — Optional Update and Next Process Preparation

This phase applies or prepares only what the selected OperatorResponse authorizes.

### 16.1 CONTINUE

The first API may return no prepared next request.
The next caller may construct a new request using returned current-scope references.

### 16.2 ADJUST

An `UpdateDecision` may describe a bounded adjustment such as:

```text
ORIENTATION_ADJUSTMENT
POLICY_ADJUSTMENT
STRUCTURE_PREPARATION
```

The Update Engine applies or prepares the selected change.
It does not select `ADJUST`.

### 16.3 RESLICE

`RESLICE` requires one prepared next `SliceRequest`.

```text
next_request.mode = RESLICE
next_request.requested_by_response_ref = current operator_response_id
next_request.parent_process_ref = current process_id
next_request.parent_slice_ref = current slice_id
next_request.source_ref identifies retained source
```

The current call must not execute this request.

### 16.4 JUMP

A `NextProcessPreparation` may identify:

```text
jump source
jump target or target candidate
trajectory branch ref
required retained evidence
```

The current call records the reconnection preparation but does not recursively execute the target Process.

### 16.5 DEFER

Create a separate `DeferredRelationRecord`.

```text
VoidEvidence
≠ DeferredRelationRecord
```

`next_request` should be null.

### 16.6 STOP

Do not prepare a next request for the current control scope.
Preserve evidence and lineage.

---

## 17. Phase 12 — Memory and Trajectory Record Preparation

Prepare records required to preserve evidence and continuity.

Candidate required records include:

```text
Process record
SliceDone record
StabilityRecord
OperatorResponseRecord
ContinuityRecord
BoundaryEvidence records
BoundaryStateRecord entries
ContextEvidence records
VoidEvidence records
DeferredRelationRecord when DEFER
TrajectoryEdge
CurrentScopeView update
```

Trajectory effects must remain distinct:

```text
CONTINUE = direct edge
ADJUST = adjusted continuous edge
RESLICE = retained-source lineage edge
JUMP = non-continuous reconnection branch
DEFER = pending relation edge
STOP = current-scope terminal boundary
```

No prior history is silently deleted.

```text
supersedes_for_current_scope
≠ universal invalidation
```

Memory Runtime and Trajectory Cache prepare or retain records.
They do not select OperatorResponse.

---

## 18. Phase 13 — Complete Result-group Validation

Before publication, validate the complete staged result:

```text
SliceDone
+
StabilityResult
+
OperatorResponse
+
RuntimeContinuityResult
+
UpdateDecision when present
+
NextProcessPreparation when present
+
created records
+
TrajectoryEdge
+
current-scope update
```

Required identity consistency includes:

```text
SliceDone.process_id
= StabilityResult.process_id
= OperatorResponse.process_id
= RuntimeContinuityResult.process_id
= current process_id
```

```text
OperatorResponse.stability_result_ref
= StabilityResult.stability_result_id
```

```text
RuntimeContinuityResult.operator_response_ref
= OperatorResponse.operator_response_id
```

Validate response-specific requirements, reference resolution, lineage acyclicity, evidence-subset rules, and embedded/reference digest consistency.

A failed generated-result validation is an execution/API failure.
It must not be transformed into a new fallback OperatorResponse.

Incorrect:

```text
invalid RESLICE result
→ silently replace response with STOP
```

Correct:

```text
invalid generated result
→ fail publication
→ return structured API error
```

---

## 19. Phase 14 — Atomic Publication

One `/loop/step` execution is one logical transaction.

Publication rule:

```text
all required Runtime artifacts are complete and valid
→ publish together
```

or:

```text
required Runtime artifact set is incomplete or invalid
→ publish no completed Process result
```

The first implementation should use one of these modes:

### 19.1 Persisted atomic mode

```text
stage records
→ validate complete group
→ commit records and current-scope update atomically
→ expose completed result
```

### 19.2 Complete direct-return mode

A stateless-compatible implementation may return a complete validated result without durable persistence.

It must still:

```text
return all required identities and lineage
avoid claiming durable record refs that were not persisted
identify persistence_mode
```

A partial durable commit followed by a successful response is prohibited.

Optional later compression or cold archive is outside the immediate transaction.

---

## 20. Phase 15 — LoopStepResult Return

The successful response returns one complete `LoopStepResult`.

Canonical high-level shape:

```text
LoopStepResult
├─ request_id
├─ loop_id
├─ process_id
├─ process_index
├─ slice_done
├─ stability
├─ operator_response
├─ continuity
├─ update_decision
├─ next_process_preparation
├─ created_record_refs
├─ current_scope_ref
├─ trajectory_ref
├─ request_digest
├─ runtime_version
├─ policy_ref
├─ persistence_mode
├─ replayed
├─ started_at
├─ completed_at
└─ metadata
```

A successful response means:

```text
the API execution contract completed successfully
```

It does not mean:

```text
StabilityStatus = STABLE
OperatorResponse = CONTINUE
Boundary State = NORMAL
application success
```

---

## 21. Process Status Model

The first implementation may use internal Process statuses:

```text
RESERVED
EXECUTING_SLICE
SLICE_DONE_STAGED
STABILITY_READ
RESPONSE_SELECTED
CONTINUITY_CREATED
RESULT_VALIDATED
COMPLETED
FAILED
```

Only:

```text
COMPLETED
```

may be exposed as a successful `LoopStepResult`.

A `STOP` OperatorResponse may still belong to a `COMPLETED` Process.

```text
Process execution completed successfully
+
OperatorResponse = STOP
```

is valid because API execution completion and Runtime continuation disposition are different responsibilities.

---

## 22. Timeout and Cancellation Boundary

A deadline or caller cancellation may occur before or during execution.

Rules:

```text
cancellation before Process reservation
→ no Process artifact
```

```text
cancellation after reservation but before atomic publication
→ no completed Process result
```

A diagnostic failed-attempt record may be retained if clearly separated from Runtime completion records.

Timeout must not automatically become:

```text
DEFER
STOP
JUMP
```

unless a valid Runtime result had already been selected and the complete transaction was successfully published before transport delivery failed.

If publication succeeded but response delivery failed, idempotent retry should return the prior completed result.

---

## 23. Failure Categories Within Execution

The execution contract distinguishes:

### 23.1 Pre-execution API failure

Examples:

```text
invalid request shape
missing reference
lineage conflict
idempotency conflict
current-scope conflict
```

No Process execution begins.

### 23.2 Runtime engine failure

Examples:

```text
Slice Engine exception
Stability Engine exception
Loop Controller failure
record construction failure
```

No completed result is published.

### 23.3 Generated-result inconsistency

Examples:

```text
response / continuity mismatch
invalid VOID classification
RESLICE without next_request
DEFER without pending relation
STOP with next_request
```

No completed result is published.

### 23.4 Valid Runtime uncertainty or non-continuation

Examples:

```text
UNKNOWN
VOID
NOT_EVALUABLE
DEFER
JUMP
STOP
```

These may be successful `2xx` Runtime results when the contract completed correctly.

Exact status mapping is deferred to E-8.

---

## 24. Observability Requirements

The endpoint should expose enough observability to reconstruct one step without relying on hidden mutable state.

At minimum retain or return:

```text
request_id
loop_id
process_id
request_digest
source identity
orientation identity
SlicePolicy identity
resolved evidence refs
created artifact IDs
selected response
continuity result
parent lineage
trajectory edge
runtime version
policy version
started_at
completed_at
```

Logs may include additional timing and implementation details.

Logs must not become the only location where required Runtime identity or lineage exists.

---

## 25. Security and Application Boundary

The endpoint may enforce transport authentication, authorization, payload limits, and tenant isolation.

Those controls are API infrastructure concerns.

GyroOS Runtime results must not be converted into application verdicts such as:

```text
authenticated
access_denied
fraud
malware
approved
rejected
```

Application layers may interpret GyroOS outputs separately.

```text
Gyro Logic
↓
GyroOS
↓
GyroAuth or another application
```

The lower Runtime layer does not redefine the application decision.

---

## 26. Prohibited Execution Patterns

The first API must not implement:

```text
recursive Process execution inside one /loop/step call
background continuation after response without explicit new request
implicit latest Context lookup
implicit latest SliceDone lookup
Stability-driven automatic response
Void-driven automatic response
Damper-driven response selection
Local-Inertia-driven response selection
support endpoint as alternate LoopController
partial successful publication
automatic fallback response after generated-result validation failure
application verdict generation
```

---

## 27. Minimal Implementation Components

A bounded implementation may use:

```text
LoopStepService
RequestSchemaValidator
IdempotencyGuard
ReferenceResolver
CurrentScopeGuard
LineageValidator
ProcessIdentityFactory
SliceEngine
StabilityEngine
LoopController
ContinuityBuilder
UpdateEngine
NextProcessPreparationBuilder
MemoryRuntime
TrajectoryCache
RuntimeResultValidator
TransactionManager
LoopStepResultSerializer
```

Ownership rule:

```text
LoopController
=
only OperatorResponse selector
```

All other components validate, execute, build, preserve, or serialize.

---

## 28. Execution Pseudocode

```python
def loop_step(request: LoopStepRequest) -> LoopStepResult:
    validate_request_shape(request)

    request_digest = canonical_digest(request)
    replay = idempotency_guard.find_completed(request, request_digest)
    if replay is not None:
        return replay

    idempotency_guard.reserve_or_reject(request, request_digest)

    resolved = reference_resolver.resolve_all(request)
    validate_preconditions(request, resolved)
    current_scope_guard.assert_expected(request)

    process = process_factory.reserve(request, request_digest)

    try:
        slice_done = slice_engine.execute_one(
            structure=request.structure,
            slice_request=request.slice_request,
            resolved=resolved,
            limits=request.runtime_limits,
            process=process,
        )
        validate_slice_done(slice_done, request, resolved, process)

        stability = stability_engine.read(slice_done, resolved)
        validate_stability(stability, slice_done, process)

        response = loop_controller.select(
            slice_done=slice_done,
            stability=stability,
            resolved=resolved,
            limits=request.runtime_limits,
            policy_ref=request.policy_ref,
        )

        continuity = continuity_builder.build(response, slice_done)
        update, next_preparation = prepare_selected_effects(
            response=response,
            slice_done=slice_done,
            process=process,
        )

        records = memory_and_trajectory.prepare_records(
            process=process,
            slice_done=slice_done,
            stability=stability,
            response=response,
            continuity=continuity,
            update=update,
            next_preparation=next_preparation,
        )

        result = build_loop_step_result(
            request=request,
            process=process,
            slice_done=slice_done,
            stability=stability,
            response=response,
            continuity=continuity,
            update=update,
            next_preparation=next_preparation,
            records=records,
        )

        validate_complete_result(result, resolved)
        transaction_manager.publish_atomically(result, records)
        idempotency_guard.mark_completed(request, request_digest, result)
        return result

    except Exception:
        transaction_manager.abort_unpublished(process)
        idempotency_guard.release_or_mark_failed(request, request_digest)
        raise
```

This pseudocode fixes responsibility order only.
It is not the final implementation code.

---

## 29. Acceptance Criteria

Priority E-6 is accepted when the execution contract guarantees:

```text
1. One request executes at most one Slice and one Gyro Process.
2. Pre-execution validation completes before Process publication.
3. Idempotent replay does not create duplicate Runtime artifacts.
4. Explicit references are resolved without implicit latest-object lookup.
5. SliceDone is produced before StabilityResult.
6. StabilityResult does not select OperatorResponse.
7. LoopController is the sole response owner.
8. RuntimeContinuityResult matches the selected response.
9. RESLICE prepares but does not execute the next Process.
10. DEFER creates a separate pending relation.
11. STOP ends only the current control-scope connection.
12. Complete result validation occurs before publication.
13. Required records publish atomically or are returned as a complete non-persisted result.
14. UNKNOWN, VOID, NOT_EVALUABLE, DEFER, JUMP, and STOP remain valid Runtime results.
15. GyroOS does not produce application verdicts.
```

---

## 30. E-6 Decision

```text
Priority E-6
Status: ACCEPTED
```

The canonical endpoint execution model is:

```text
validate
→ resolve
→ reserve one Process
→ execute one Slice
→ build SliceDone
→ read Stability
→ select one OperatorResponse
→ build RuntimeContinuityResult
→ prepare bounded next effects
→ preserve Memory / Trajectory records
→ validate complete result
→ publish atomically
→ return one LoopStepResult
```

The next Priority E step is:

```text
Priority E-7
= Supporting Endpoint Contract
```
