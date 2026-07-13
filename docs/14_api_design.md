# 14. API Design

---

## 1. Overview

This document defines the API model for GyroOS v4.0 / vNext after the Gyro Logic v3.1 Core Definition refinement and the Priority B / Priority C Runtime alignment.

The central API remains:

```text
POST /loop/step
```

This endpoint executes one bounded **Gyro Process** and produces one **Operator Response**.

The invariant theoretical Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The API represents this Core in Runtime.

It does not redefine it.

Boundary, Boundary State, Context, Void evidence, StabilityResult, and OperatorResponse are not additional Core elements.

---

## 2. Canonical Runtime Meaning of `/loop/step`

`POST /loop/step` executes the following responsibility chain:

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
    Boundary evidence if readable
    Boundary State records if classifiable
    Context references
    Void evidence / references if retained
  }
}
↓
StabilityResult
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
Runtime Continuity result
↓
Next Process preparation when applicable
```

This ordering is operational.

It must not be interpreted as adding independent theoretical stages between Structure, Slice, and Stability.

In particular:

```text
Operator Orientation
slice-ing
slice-done
```

are internal Runtime distinctions of Slice.

---

## 3. Responsibility Separation

The API contract must preserve the following separation:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

### SliceDone

```text
The readable established result of Slice.
```

### StabilityResult

```text
A Runtime representation of whether the opened Path is readable as an establishment that can continue.
```

### OperatorResponse

```text
The selected next connection disposition.
```

### RuntimeContinuityResult

```text
The resulting relation between the current established or retained source and the next Runtime connection state.
```

No one object may silently substitute for another.

---

## 4. Main Endpoint

```text
POST /loop/step
```

### Purpose

Execute one bounded Gyro Process over the current Runtime Structure and return:

```text
Boundary-aware SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
```

### Request

```json
{
  "loop_id": "gyro_loop_001",
  "structure": {
    "structure_id": "structure_012",
    "current_mode": {},
    "retained_conditions": {},
    "continuity_refs": [],
    "constraints": {},
    "metadata": {}
  },
  "slice_request": {
    "request_id": "slice_request_012",
    "mode": "slice",
    "source_type": "structure",
    "source_ref": "structure_012",
    "orientation": {
      "orientation_id": "orientation_003",
      "weights": {},
      "resolution": {},
      "target_dimensions": [],
      "constraints": {},
      "metadata": {}
    },
    "slice_policy": {},
    "context_refs": [],
    "parent_process_id": null,
    "parent_slice_id": null,
    "metadata": {}
  },
  "runtime_limits": {},
  "previous_state_ref": null
}
```

The exact serialization is provisional.

The semantic requirement is that Operator Orientation and Slice Policy remain part of the Slice request and execution context, not independent Core stages.

---

## 5. Response Contract

```json
{
  "loop_id": "gyro_loop_001",
  "process_id": "process_012",
  "process_index": 12,
  "slice_done": {
    "slice_id": "slice_012",
    "representation": {},
    "deviation": {},
    "boundary_evidence": [],
    "boundary_state_records": [],
    "context_refs": [],
    "void_evidence": [],
    "boundary_refs": [],
    "boundary_state_refs": [],
    "void_refs": [],
    "orientation_ref": "orientation_003",
    "slice_policy_ref": "slice_policy_003",
    "trajectory_ref": "trajectory_001",
    "readability": {},
    "metadata": {}
  },
  "stability": {
    "value": 0.72,
    "status": "adaptive",
    "continuability": true,
    "reason": "opened path remains readable with bounded uncertainty",
    "evidence_refs": [],
    "metadata": {}
  },
  "operator_response": {
    "response_type": "ADJUST",
    "reason": "current path remains connectable through bounded modification",
    "considered_boundary_refs": [],
    "considered_boundary_state_refs": [],
    "decisive_evidence_refs": [],
    "conflicting_evidence_refs": [],
    "response_confidence": 0.81,
    "next_request": null,
    "metadata": {}
  },
  "update_decision": {
    "update_type": "orientation_adjustment",
    "previous_orientation_ref": "orientation_003",
    "next_orientation": {},
    "reason": "bounded continuous modification requested",
    "metadata": {}
  },
  "continuity": {
    "continuity_type": "direct_adjusted_connection",
    "source_ref": "slice_012",
    "target_ref": "pending_next_process",
    "pending": false,
    "terminated_for_current_scope": false,
    "metadata": {}
  },
  "next_process_ready": true,
  "trajectory_id": "trajectory_001",
  "metadata": {}
}
```

Fields may be omitted when not applicable.

However, the conceptual objects must remain distinguishable.

---

## 6. Boundary-aware SliceDone Mapping

A Boundary-aware API does not mean that every Slice must produce a Boundary.

```text
Boundary-aware
≠ Boundary-required
```

A valid `SliceDone` may contain:

```text
representation
Difference / Deviation
no readable Boundary
```

When Boundary-related information is available, the naming rule is:

```text
*_evidence
= embedded or directly retained evidence objects

*_records
= classified Runtime records with identity and lineage

*_refs
= references to separately retained records
```

Preferred object names:

```text
BoundaryEvidence
BoundaryStateRecord
VoidEvidence
```

Preferred `SliceDone` fields:

```python
boundary_evidence: list[BoundaryEvidence]
boundary_state_records: list[BoundaryStateRecord]
void_evidence: list[VoidEvidence]

boundary_refs: list[str]
boundary_state_refs: list[str]
void_refs: list[str]
```

---

## 7. Boundary and Void API Semantics

The API must distinguish:

```text
Boundary
Boundary State
Void as Boundary State
VoidEvidence
Void reference
OperatorResponse
```

`VOID` is not an Operator Response.

Incorrect:

```json
{
  "operator_response": {
    "response_type": "void"
  }
}
```

Correct separation:

```json
{
  "slice_done": {
    "boundary_state_records": [
      {
        "state_type": "VOID",
        "boundary_ref": "boundary_003",
        "relation_ref": "relation_017",
        "boundary_state_confidence": 0.76
      }
    ],
    "void_evidence": [
      {
        "void_id": "void_012",
        "boundary_ref": "boundary_003",
        "relation_ref": "relation_017",
        "reason": "target relation is not sufficiently readable or connectable"
      }
    ]
  },
  "operator_response": {
    "response_type": "DEFER",
    "reason": "future context may restore connectability"
  }
}
```

A `VOID` Boundary State requires:

```text
the relevant Boundary is identifiable
+
the target relation is not sufficiently readable or connectable relative to it
```

If the Boundary distinction itself is unreadable, the API should return:

```text
unclassified Boundary evidence
or
unreadable distinction evidence
```

rather than forcing `VOID`.

---

## 8. Stability API Semantics

Stability is not:

```text
completion status
success flag
stop signal
controller output
Boundary confidence
Boundary State confidence
```

The API mapping is:

```text
StabilityResult
= a Runtime representation of whether the opened Path is readable as an establishment that can continue
```

Recommended fields:

```python
class StabilityResult:
    process_id: str
    value: float | None
    status: str
    continuability: bool | None
    reason: str | None
    evidence_refs: list[str]
    metadata: dict
```

Possible implementation statuses may include:

```text
stable
adaptive
unstable
not_evaluable
void_related
```

These are Runtime statuses, not new Gyro Logic definitions.

Important:

```text
continuability
≠ CONTINUE response
```

A continuable establishment may still lead to:

```text
ADJUST
RESLICE
JUMP
DEFER
STOP
```

when other Runtime evidence or control-scope conditions justify it.

---

## 9. Operator Response API Semantics

The canonical response vocabulary is:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

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
Request another Slice from a retained source relation.
```

### JUMP

```text
Request non-continuous reconnection.
```

### DEFER

```text
Keep the relation pending while preserving future connectability.
```

### STOP

```text
End the execution connection in the current control scope while preserving evidence.
```

The following older names are compatibility aliases only and should not be used as the canonical response vocabulary:

```text
CHANGE_ORIENTATION → ADJUST
RESLICE_CONTEXT → RESLICE
DEFER_VOID → DEFER with Void-related reason/evidence
```

`VOID` is never a response alias.

---

## 10. Operator Response Decision Inputs

The Loop Controller owns Operator Response selection.

A Boundary-aware decision may consider:

```text
SliceDone readability
StabilityResult
Difference / Deviation
Boundary readability
Boundary State records
Context availability
Void evidence
Trajectory history
recoverability
Re-Slice viability
retainability
reconstruction necessity
Runtime limits
policy
```

The API must not encode direct universal mappings such as:

```text
NORMAL → CONTINUE
UNKNOWN → RESLICE
VOID → DEFER
low Stability → STOP
large Δ → JUMP
```

A bounded PoC may use deterministic policy rules, but the response payload should expose:

```text
reason
considered evidence references
decisive evidence references
conflicting evidence references
response confidence when implemented
```

---

## 11. UpdateDecision Semantics

The Update Engine applies a selected response.

It does not own the response decision.

Correct:

```text
Loop Controller
↓ selects ADJUST
OperatorResponse
↓
Update Engine
↓ applies bounded modification
UpdateDecision
```

Incorrect:

```text
Update Engine detects low Stability
↓
chooses ADJUST or JUMP
```

`UpdateDecision` is optional.

It is typically relevant to:

```text
ADJUST
JUMP preparation
some RESLICE preparations
```

It is not required for every response.

---

## 12. Runtime Continuity Mapping

Recommended continuity result vocabulary:

```text
direct_connection
direct_adjusted_connection
retained_source_for_reslice
non_continuous_reconnection_requested
pending_future_connection
current_scope_connection_ended
```

Suggested mapping:

```text
CONTINUE
→ direct_connection

ADJUST
→ direct_adjusted_connection

RESLICE
→ retained_source_for_reslice

JUMP
→ non_continuous_reconnection_requested

DEFER
→ pending_future_connection

STOP
→ current_scope_connection_ended
```

These mappings describe continuity effects.

They do not redefine the Operator Responses.

---

## 13. Internal Runtime Steps

### 13.1 Create Runtime Structure Reference

Resolve the current Runtime mode in which establishment remains possible.

Structure is not limited to raw request payload.

It may include:

```text
current state
constraints
retained prior effects
Context
Difference
Trajectory-derived continuity
conditions for the next Slice
```

### 13.2 Execute Slice

```text
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
```

The Slice Engine opens a bounded Runtime Path through the current Structure.

### 13.3 Produce SliceDone

```text
slice-done
= the state in which the Slice has become readable as an established result
```

It is not merely:

```text
execution finished
```

### 13.4 Read Stability

The Stability Engine reads the established Slice result.

It does not control the loop.

### 13.5 Select Operator Response

The Loop Controller integrates Runtime evidence and selects one canonical response.

### 13.6 Apply Response Effects

Depending on the selected response, the Runtime may invoke:

```text
Update Engine
Re-Slice Engine
Jump preparation
Defer retention
Stop scope closure
```

### 13.7 Preserve Memory and Trajectory

The Runtime stores or references:

```text
SliceDone
Boundary evidence
Boundary State records
Void evidence
StabilityResult
OperatorResponse
Runtime Continuity result
lineage
```

---

## 14. Supporting Endpoints

Supporting endpoints are subordinate to `POST /loop/step`.

They do not become alternate owners of Runtime control.

### GET `/loop/state`

Returns the current `LoopState` and active references.

### GET `/loop/history`

Returns Process, SliceDone, Stability, response, continuity, Boundary, Void, orientation, and trajectory history.

### GET `/response/history`

Returns Operator Response records and their evidence references.

### GET `/orientation/current`

Returns the current Operator Orientation / Slice Policy representation.

### GET `/boundary/{boundary_id}`

Returns one retained Boundary record or evidence representation.

### GET `/boundary/{boundary_id}/history`

Returns Boundary lineage and current-scope relations.

### GET `/boundary-state/{boundary_state_id}`

Returns one Boundary State record.

### GET `/trajectory/{trajectory_id}/boundaries`

Returns Boundary and Boundary State references associated with a trajectory.

### POST `/observe`

Optional low-level Slice execution endpoint.

It must not be treated as the main Runtime endpoint.

It must not select Operator Response.

### POST `/update`

Optional low-level Update Engine endpoint.

It applies an already selected `UpdateDecision`.

It must not choose a response.

### POST `/reslice/execute`

Optional Re-Slice execution endpoint.

It executes an already selected `RESLICE` request.

```text
POST /reslice/execute
≠ RESLICE decision owner
```

---

## 15. HTTP Status Semantics

GyroOS Runtime outcomes are not automatically HTTP errors.

The following may be valid `200` Runtime responses:

```text
Boundary State = UNKNOWN
Boundary State = VOID
Stability status = not_evaluable
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

HTTP errors should represent transport, contract, authorization, server, or request-processing failures.

They should not be used as aliases for GyroOS relational states.

Example:

```json
{
  "slice_done": {
    "boundary_state_records": [
      {
        "state_type": "VOID"
      }
    ]
  },
  "stability": {
    "status": "not_evaluable"
  },
  "operator_response": {
    "response_type": "DEFER"
  }
}
```

may still return:

```text
HTTP 200
```

---

## 16. API Boundary with GyroAuth

GyroOS returns Runtime relations and response information.

GyroOS does not make application-specific authentication decisions.

GyroOS may return:

```text
SliceDone
Difference / Deviation
Boundary evidence
Boundary State records
Void evidence
StabilityResult
OperatorResponse
Trajectory evidence
Runtime Continuity result
```

GyroAuth may interpret those Runtime outputs as application states such as:

```text
AUTH_STABLE
RECONVERGING
REAUTH_REQUIRED
AUTH_FAIL
```

Those application states belong to GyroAuth.

They are not GyroOS Core or Operator Response values.

---

## 17. Design Constraints

The API MUST NOT:

```text
redefine Structure → Slice → Stability
represent Operator Orientation as a fourth Core stage
collapse slice-ing and slice-done
reduce SliceDone to only X + Δ
place Stability inside SliceDone by definition
treat Stability as controller
treat Boundary State as Stability
treat Boundary confidence as Stability
treat Void as an action or response
automatically map Boundary State to Operator Response
make /update the main Runtime endpoint
make Update Engine the loop owner
delete Difference / Deviation history
overwrite Boundary State history silently
mix GyroAuth authentication decisions into GyroOS
```

The API MUST:

```text
expose /loop/step as the main Runtime endpoint
represent one bounded Gyro Process per step
keep Operator Orientation inside the Slice mapping
return a readable established SliceDone
keep SliceDone, StabilityResult, and OperatorResponse separate
support Boundary-aware but not Boundary-required SliceDone
separate Void evidence from DEFER / JUMP / STOP
use CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP as canonical responses
preserve evidence and lineage
return Runtime Continuity effects
prepare the next Process only when applicable
```

---

## 18. Summary

`POST /loop/step` is the primary Runtime API of GyroOS v4.0 / vNext.

It means:

```text
Run one bounded Gyro Process,
read its continuing establishment state,
select one Operator Response,
and preserve the resulting Runtime Continuity relation.
```

It does not mean:

```text
compute one answer
classify one final state
let Stability control the loop
let Boundary or Void choose an action
```

The canonical API relation is:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  slice-ing
  slice-done
}
↓
StabilityResult
↓
OperatorResponse
↓
Runtime Continuity
↓
Next Process when applicable
```

This preserves:

```text
Structure → Slice → Stability
```

while exposing the Runtime distinctions required by GyroOS.