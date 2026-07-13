# 55. StabilityResult, OperatorResponse, and RuntimeContinuity Schemas

---

## 1. Purpose

This document defines **Priority E-4: StabilityResult, OperatorResponse, and RuntimeContinuity Schemas** for the GyroOS API.

The purpose is to fix the canonical response-side contracts that follow `SliceDone` in one bounded Gyro Process.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The Runtime API relation is:

```text
SliceDone
↓
StabilityResult
↓
OperatorResponse
↓
RuntimeContinuityResult
```

These objects are related, but they are not interchangeable.

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

---

## 2. E-4 Decision Summary

The canonical result group is:

```text
LoopStepResult
├─ slice_done: SliceDone
├─ stability: StabilityResult
├─ operator_response: OperatorResponse
├─ continuity: RuntimeContinuityResult
├─ update_decision: UpdateDecision | null
├─ next_process_preparation: NextProcessPreparation | null
└─ created_record_refs
```

The primary responsibility separation is:

```text
StabilityResult
= reads whether the opened Path is readable as an establishment that can continue

OperatorResponse
= selects the next Runtime connection disposition

RuntimeContinuityResult
= records the connection relation resulting from the selected response
```

No field in one object may silently substitute for the responsibility of another object.

---

## 3. StabilityResult

Canonical model:

```python
class StabilityResult:
    stability_result_id: str
    process_id: str
    slice_id: str

    value: float | None
    status: StabilityStatus
    continuability: bool | None
    reason: str

    evidence_refs: list[str]
    supporting_evidence_refs: list[str]
    conflicting_evidence_refs: list[str]

    evaluation_policy_ref: str | None
    created_at: str
    metadata: dict
```

### Meaning

```text
StabilityResult
= a Runtime representation of whether the opened Path is readable as an establishment that can continue
```

Stability is read from the established Slice result.

It is not:

```text
HTTP success
Process completion
Operator Response
Boundary readability
Boundary State confidence
Context confidence
Response confidence
application verdict
```

---

## 4. StabilityResult Required and Optional Fields

### Required

```text
stability_result_id
process_id
slice_id
status
reason
evidence_refs
supporting_evidence_refs
conflicting_evidence_refs
created_at
```

### Optional and nullable

```text
value
continuability
evaluation_policy_ref
metadata
```

Collection fields must be present and default to empty lists.

### Identity rules

```text
stability_result_id
= server-owned Runtime artifact identity

process_id
= MUST equal SliceDone.process_id

slice_id
= MUST equal SliceDone.slice_id
```

---

## 5. StabilityStatus

Canonical initial Runtime values:

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED
```

These values are implementation statuses.

They are not new Gyro Logic definitions.

### Status meaning

#### STABLE

```text
The opened Path is readable as an establishment that can continue under the current evaluation policy.
```

#### ADAPTIVE

```text
The establishment remains readable and potentially continuable, but bounded modification or additional evidence may be relevant.
```

#### UNSTABLE

```text
The current established reading does not sufficiently support continuation under the current evaluation policy.
```

#### NOT_EVALUABLE

```text
The available Slice result and evidence are insufficient for a valid Stability reading.
```

#### VOID_RELATED

```text
The Stability reading is materially affected by Void-related evidence or a VOID Boundary State.
```

`VOID_RELATED` does not mean:

```text
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

---

## 6. Stability Value and Continuability

### value

When present:

```text
0.0 <= value <= 1.0
```

A null value is permitted when Stability is not numerically evaluable.

```text
status = NOT_EVALUABLE
→ value MAY be null
```

A numeric value is implementation-specific and must not replace the semantic fields:

```text
status
continuability
reason
```

### continuability

```text
continuability
= whether the current establishment is readable as capable of continuing under the Stability evaluation
```

It must remain distinct from the canonical response:

```text
continuability = true
≠ OperatorResponse = CONTINUE
```

A continuable establishment may still lead to:

```text
ADJUST
RESLICE
JUMP
DEFER
STOP
```

when other Runtime evidence, policy, or control-scope conditions justify it.

A null value means that continuability was not validly determined.

---

## 7. OperatorResponse

Canonical model:

```python
class OperatorResponse:
    operator_response_id: str
    process_id: str
    slice_id: str
    stability_result_ref: str

    response_type: OperatorResponseType
    reason: str
    response_confidence: float | None

    considered_evidence_refs: list[str]
    decisive_evidence_refs: list[str]
    conflicting_evidence_refs: list[str]

    next_request: SliceRequest | None
    update_decision_ref: str | None

    selected_by_policy_ref: str | None
    created_at: str
    metadata: dict
```

### Meaning

```text
OperatorResponse
= the selected next Runtime connection disposition after considering SliceDone, StabilityResult, retained evidence, trajectory, limits, and policy
```

The response owner is:

```text
Loop Controller
```

The following do not own response selection:

```text
StabilityEngine
SliceEngine
ReSliceEngine
MemoryRuntime
TrajectoryCache
Gyro-OOM Damper
Local Inertia
ContextEvidence
VoidEvidence
BoundaryStateRecord
```

---

## 8. OperatorResponseType

Canonical values:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Compatibility aliases must not appear as enum values:

```text
CHANGE_ORIENTATION
RESLICE_CONTEXT
DEFER_VOID
VOID
```

Compatibility interpretation, when reading legacy records only:

```text
CHANGE_ORIENTATION → ADJUST
RESLICE_CONTEXT → RESLICE with Context source references
DEFER_VOID → DEFER with Void-related evidence or reason
```

`VOID` is never an OperatorResponse value.

---

## 9. OperatorResponse Semantics

### CONTINUE

```text
Preserve direct connection through the current established Path.
```

### ADJUST

```text
Preserve Runtime Continuity through bounded continuous modification.
```

### RESLICE

```text
Request another Slice from an explicitly retained Runtime source relation.
```

### JUMP

```text
Request non-continuous reconnection to another Runtime relation.
```

### DEFER

```text
Keep the relation pending while preserving future connectability.
```

### STOP

```text
End the execution connection in the current control scope while preserving evidence and lineage.
```

STOP does not mean:

```text
universal termination
history deletion
application rejection
runtime object destruction
```

---

## 10. OperatorResponse Required and Optional Fields

### Required

```text
operator_response_id
process_id
slice_id
stability_result_ref
response_type
reason
considered_evidence_refs
decisive_evidence_refs
conflicting_evidence_refs
created_at
```

### Optional and nullable

```text
response_confidence
next_request
update_decision_ref
selected_by_policy_ref
metadata
```

### Rules

```text
response_confidence, when present, MUST be within 0.0 to 1.0
reason MUST be non-empty
all evidence refs MUST be unique non-empty strings
```

`response_confidence` is distinct from:

```text
boundary_readability
boundary_state_confidence
context_confidence
stability value
```

---

## 11. Evidence Reference Rules

`considered_evidence_refs` records evidence examined by the response policy.

`decisive_evidence_refs` records evidence that materially contributed to the selected response.

`conflicting_evidence_refs` records evidence that opposed, limited, or complicated the selected response.

Rules:

```text
decisive_evidence_refs MUST be a subset of considered_evidence_refs
conflicting_evidence_refs SHOULD be a subset of considered_evidence_refs
all refs MUST resolve within the current result or retained state
```

The API must not encode universal direct mappings such as:

```text
NORMAL → CONTINUE
UNKNOWN → RESLICE
VOID → DEFER
low Stability → STOP
large Deviation → JUMP
Context exists → RESLICE
```

A bounded implementation may use deterministic policy rules, but those rules are implementation policy, not Gyro Logic definitions.

---

## 12. next_request Rules

`next_request` is permitted only when the selected response prepares a next Slice execution.

### RESLICE

```text
response_type = RESLICE
→ next_request MUST be present
→ next_request.mode MUST be RESLICE
→ next_request.requested_by_response_ref MUST equal operator_response_id
```

The current HTTP call does not execute that request.

```text
one HTTP request
=
one bounded Gyro Process
```

### CONTINUE

`next_request` may be null in the first API.

The next direct Process may be created by the next caller request using the returned continuity and current-scope references.

### ADJUST

`next_request` may be null when the update is represented through `UpdateDecision`.

If a prepared next SliceRequest is returned, its Orientation must reference or embed the selected adjusted Orientation.

### JUMP

A first implementation may represent JUMP through `NextProcessPreparation` rather than `next_request` if the target relation is not yet a valid Slice source.

### DEFER

`next_request` SHOULD be null.

A future retry or Re-Slice request is created only after additional evidence or explicit caller action.

### STOP

`next_request` MUST be null.

---

## 13. UpdateDecision

Canonical model:

```python
class UpdateDecision:
    update_decision_id: str
    process_id: str
    operator_response_ref: str

    update_type: UpdateType
    target_ref: str
    previous_value_ref: str | None
    next_value: dict | None
    reason: str

    created_at: str
    metadata: dict
```

Canonical initial update types:

```text
ORIENTATION_ADJUSTMENT
POLICY_ADJUSTMENT
STRUCTURE_PREPARATION
JUMP_TARGET_PREPARATION
```

`UpdateDecision` applies or describes a selected response.

It does not select the response.

For the first API:

```text
response_type = ADJUST
→ update_decision SHOULD be present
```

A response may omit it only when the adjustment has no materialized update object and that behavior is explicitly supported by policy.

---

## 14. RuntimeContinuityResult

Canonical model:

```python
class RuntimeContinuityResult:
    continuity_result_id: str
    process_id: str
    operator_response_ref: str

    continuity_type: RuntimeContinuityType
    source_ref: str
    target_ref: str | None

    connected: bool
    pending: bool
    terminated_for_current_scope: bool

    retained_relation_ref: str | None
    deferred_relation_ref: str | None
    trajectory_edge_ref: str | None

    reason: str
    created_at: str
    metadata: dict
```

### Meaning

```text
RuntimeContinuityResult
= the recorded relation between the current established or retained source and the next Runtime connection state after OperatorResponse
```

It is not another decision owner.

```text
OperatorResponse selects.
RuntimeContinuityResult records the resulting connection relation.
```

---

## 15. RuntimeContinuityType

Canonical values:

```text
DIRECT_CONNECTION
ADJUSTED_CONNECTION
RESLICE_CONNECTION
JUMP_RECONNECTION
DEFERRED_PENDING_RELATION
STOPPED_FOR_CURRENT_SCOPE
```

These values are Runtime result categories.

They are not OperatorResponse aliases.

---

## 16. Canonical Response-to-Continuity Mapping

The first API uses the following strict mapping:

| OperatorResponse | RuntimeContinuityType |
|---|---|
| CONTINUE | DIRECT_CONNECTION |
| ADJUST | ADJUSTED_CONNECTION |
| RESLICE | RESLICE_CONNECTION |
| JUMP | JUMP_RECONNECTION |
| DEFER | DEFERRED_PENDING_RELATION |
| STOP | STOPPED_FOR_CURRENT_SCOPE |

This mapping defines result consistency.

It does not mean that continuity selects the response.

---

## 17. Continuity Boolean Rules

### DIRECT_CONNECTION

```text
connected = true
pending = false
terminated_for_current_scope = false
```

### ADJUSTED_CONNECTION

```text
connected = true
pending = false
terminated_for_current_scope = false
```

### RESLICE_CONNECTION

For the current step:

```text
connected = true
pending = true
terminated_for_current_scope = false
```

The retained source and prepared next Slice request are connected by lineage, but the next Process has not yet executed.

### JUMP_RECONNECTION

```text
connected = true when a valid jump target relation is prepared or established
pending = implementation-dependent
terminated_for_current_scope = false
```

If no valid target is available, the Runtime must not falsely report an established jump reconnection.

A policy may instead select `DEFER` or `STOP`.

### DEFERRED_PENDING_RELATION

```text
connected = false
pending = true
terminated_for_current_scope = false
```

The relation is retained for future connectability.

### STOPPED_FOR_CURRENT_SCOPE

```text
connected = false
pending = false
terminated_for_current_scope = true
```

Evidence and history remain preserved.

---

## 18. DEFER and DeferredRelationRecord

When:

```text
response_type = DEFER
```

then:

```text
continuity_type MUST be DEFERRED_PENDING_RELATION
pending MUST be true
deferred_relation_ref MUST be present
```

The referenced record is separate from VoidEvidence.

```python
class DeferredRelationRecord:
    deferred_relation_id: str
    process_id: str
    operator_response_ref: str
    source_ref: str
    relation_ref: str
    retained_evidence_refs: list[str]
    revisit_conditions: dict
    created_at: str
    metadata: dict
```

Prohibited:

```text
VoidEvidence.deferred
VoidEvidence.resolved
```

---

## 19. STOP Boundary

When:

```text
response_type = STOP
```

then:

```text
continuity_type MUST be STOPPED_FOR_CURRENT_SCOPE
terminated_for_current_scope MUST be true
next_request MUST be null
```

STOP must preserve:

```text
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
Trajectory edge or stop boundary record
considered evidence references
```

STOP is a valid Runtime result and is not automatically an HTTP error.

---

## 20. RESLICE Boundary

When:

```text
response_type = RESLICE
```

then:

```text
next_request MUST be present
continuity_type MUST be RESLICE_CONNECTION
pending MUST be true
```

The next request must preserve:

```text
source_type
source_ref
parent_process_ref
parent_slice_ref
requested_by_response_ref
trajectory_ref when available
```

The existence of ContextEvidence, BoundaryEvidence, BoundaryStateRecord, or VoidEvidence does not itself authorize RESLICE.

The authorization is the selected `OperatorResponse`.

---

## 21. JUMP Boundary

When:

```text
response_type = JUMP
```

then:

```text
continuity_type MUST be JUMP_RECONNECTION
```

JUMP must create or prepare an explicit target relation.

The response or preparation object must expose:

```text
jump source
jump target or target candidate
reason
lineage boundary
trajectory branch reference
```

JUMP does not erase the prior trajectory.

The new branch must remain linked to the previous branch point.

---

## 22. NextProcessPreparation

Canonical model:

```python
class NextProcessPreparation:
    preparation_id: str
    process_id: str
    operator_response_ref: str

    preparation_type: str
    next_structure: dict | None
    next_structure_ref: str | None
    next_slice_request: SliceRequest | None
    jump_target_ref: str | None

    parent_process_ref: str
    parent_slice_ref: str
    trajectory_ref: str | None

    created_at: str
    metadata: dict
```

This object prepares a future Process.

It does not execute it.

```text
NextProcessPreparation
≠ next Gyro Process
```

---

## 23. Cross-object Identity Rules

For one `LoopStepResult`:

```text
StabilityResult.process_id
= OperatorResponse.process_id
= RuntimeContinuityResult.process_id
= SliceDone.process_id
```

```text
StabilityResult.slice_id
= OperatorResponse.slice_id
= SliceDone.slice_id
```

```text
OperatorResponse.stability_result_ref
= StabilityResult.stability_result_id
```

```text
RuntimeContinuityResult.operator_response_ref
= OperatorResponse.operator_response_id
```

If `UpdateDecision` is present:

```text
UpdateDecision.operator_response_ref
= OperatorResponse.operator_response_id
```

All identities must be unique within the result unless they explicitly refer to the same object.

---

## 24. Canonical LoopStepResult Shape

```python
class LoopStepResult:
    request_id: str
    loop_id: str
    process_id: str
    process_index: int

    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    continuity: RuntimeContinuityResult

    update_decision: UpdateDecision | None
    next_process_preparation: NextProcessPreparation | None

    trajectory_ref: str | None
    current_scope_ref: str | None
    previous_state_ref: str | None

    created_record_refs: list[str]
    request_digest: str | None
    policy_ref: str | None
    runtime_version: str

    created_at: str
    metadata: dict
```

The first API returns one result for one bounded Gyro Process.

---

## 25. Valid Runtime Outcomes

The following combinations may be valid `2xx` Runtime results:

```text
StabilityStatus = NOT_EVALUABLE
BoundaryState = UNKNOWN
BoundaryState = VOID
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

They must not be converted into API errors merely because the Runtime result is uncertain, pending, non-continuous, or stopped for the current scope.

HTTP error separation is finalized in E-8.

---

## 26. Prohibited Collapses

The API must not implement:

```text
stability.value >= threshold → response hard-coded as CONTINUE by schema
continuability = true → response_type = CONTINUE
BoundaryState = VOID → response_type = DEFER
response_type = STOP → HTTP 500
continuity_type selecting OperatorResponse
VoidEvidence carrying deferred or resolved flags
RuntimeContinuityResult containing application verdicts
```

Policy may evaluate evidence deterministically, but schema semantics must remain separate.

---

## 27. Serialization Rules

Canonical enum serialization uses uppercase strings.

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED

CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP

DIRECT_CONNECTION
ADJUSTED_CONNECTION
RESLICE_CONNECTION
JUMP_RECONNECTION
DEFERRED_PENDING_RELATION
STOPPED_FOR_CURRENT_SCOPE
```

Rules:

```text
IDs are non-empty strings.
Timestamps use RFC 3339 / ISO 8601 UTC form.
Confidence and normalized numeric values are within 0.0 to 1.0.
Reference lists contain unique non-empty values.
Collection fields are present even when empty.
metadata defaults to an empty object.
```

---

## 28. Acceptance Criteria

Priority E-4 is accepted when:

```text
1. StabilityResult remains separate from OperatorResponse.
2. continuability remains separate from CONTINUE.
3. OperatorResponse uses only the six canonical response values.
4. response confidence remains separate from other confidence values.
5. RuntimeContinuityResult records rather than selects the connection relation.
6. each response has one canonical continuity type.
7. RESLICE returns a prepared next request without executing it.
8. DEFER creates a separate DeferredRelationRecord.
9. STOP ends only the current control-scope connection and preserves evidence.
10. all cross-object identities and references are traceable.
```

---

## 29. E-4 Decision

```text
Priority E-4
Status: ACCEPTED
```

The next step is:

```text
Priority E-5
= Validation and Cross-reference Rules
```
