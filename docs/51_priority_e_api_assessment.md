# 51. Priority E — API Contract Assessment

---

## 1. Purpose

This document begins **Priority E: API Contract and Implementation Readiness** after the completion of:

```text
Priority A
= Gyro Logic v3.1 Core Runtime Mapping

Priority B
= Runtime Continuity and Operator Response refinement

Priority C
= Boundary-aware Runtime definition

Priority D
= Legacy document alignment
```

Priority E does not begin by writing a large FastAPI implementation.

It first converts the reviewed Runtime model into a precise, testable, and implementation-safe API contract.

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

## 2. Priority E Goal

Priority E establishes the contract for:

```text
POST /loop/step
```

and its supporting APIs.

The target is not merely a JSON example.

The target is a contract that defines:

```text
request ownership
object identity
required and optional fields
allowed enum values
validation rules
response responsibility
Runtime result versus HTTP error
lineage and reference rules
stateful and stateless execution boundaries
bounded execution limits
testable acceptance criteria
```

Priority E should leave the repository ready for a bounded API implementation without forcing unresolved conceptual choices into code.

---

## 3. Canonical Runtime Chain

All Priority E decisions must remain consistent with:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
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

Responsibility separation:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

No API convenience may collapse these objects.

---

## 4. Priority E Scope

Priority E is divided into the following steps.

```text
E-1  API Boundary and Execution Model
E-2  Canonical Request Schema
E-3  Canonical SliceDone and Evidence Schemas
E-4  StabilityResult, OperatorResponse, and Continuity Schemas
E-5  Validation and Cross-reference Rules
E-6  /loop/step Execution Contract
E-7  Supporting Endpoint Contract
E-8  HTTP Status, Runtime Status, and Error Model
E-9  API Implementation and Test Plan
E-10 Priority E Cross-document Review and Refinement
```

This order is intentional.

Schema fields should not be finalized before execution ownership and state boundaries are fixed.

Implementation should not begin before validation and error semantics are fixed.

---

## 5. E-1 — API Boundary and Execution Model

The first decision is whether `/loop/step` is:

```text
fully stateless
stateful by loop_id
stateful by explicit previous_state_ref
or hybrid
```

The current design contains both:

```text
loop_id
previous_state_ref
Runtime Structure
Memory / Trajectory references
```

Therefore, the safest initial direction is a bounded hybrid contract:

```text
The request carries the current Runtime Structure and SliceRequest.
The runtime may resolve retained state through explicit references.
The response returns all records created by the current step or references to them.
No hidden global state is required for semantic correctness.
```

A server implementation may retain state for convenience, but the contract must expose enough identity and lineage to reconstruct the step.

This decision must be confirmed before implementation.

---

## 6. E-2 — Canonical Request Schema

The current candidate request contains:

```text
loop_id
structure
slice_request
runtime_limits
previous_state_ref
```

Priority E must determine for each field:

```text
required
optional
nullable
server-generated
client-generated
immutable within one step
reference-only or embedded
```

Initial candidate object set:

```text
LoopStepRequest
RuntimeStructureInput
SliceRequest
OperatorOrientation
SlicePolicy
RuntimeLimits
PriorStateReference
```

Important rule:

```text
OperatorOrientation and SlicePolicy belong to Slice execution context.
They are not independent Core stages.
```

Priority E should also distinguish:

```text
initial Slice request
Re-Slice request
```

without creating different theoretical operations.

---

## 7. E-3 — Canonical SliceDone and Evidence Schemas

The response must use the Priority C/D naming discipline:

```text
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
```

Collection names:

```text
boundary_evidence
boundary_state_records
context_evidence
void_evidence
```

Reference names:

```text
boundary_refs
boundary_state_refs
context_refs
void_refs
```

Naming rule:

```text
*_evidence
= embedded or directly retained evidence

*_records
= identity-bearing classified Runtime records

*_refs
= references to separately retained records
```

Priority E must decide whether the first implementation permits:

```text
embedded only
references only
or both
```

The recommended initial contract permits both, with validation preventing ambiguous duplicate identity.

---

## 8. Boundary State Vocabulary

The controlled initial Runtime vocabulary remains:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

This is:

```text
an initial controlled vocabulary
≠ a permanent closed theoretical enum
```

The first bounded PoC may implement only:

```text
NORMAL
UNKNOWN
VOID
```

but the API schema must clearly label this as an implementation subset.

`VOID` is not an Operator Response.

---

## 9. E-4 — Result Object Separation

The main response should preserve:

```text
LoopStepResult
├─ slice_done: SliceDone
├─ stability: StabilityResult
├─ operator_response: OperatorResponse
├─ continuity: RuntimeContinuityResult
├─ update_decision: optional
├─ trajectory references
└─ metadata
```

### StabilityResult

Must remain separate from:

```text
Boundary readability
Boundary State confidence
Context confidence
Operator Response confidence
HTTP success
```

### OperatorResponse

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
RESLICE_CONTEXT
CHANGE_ORIENTATION
DEFER_VOID
VOID
```

### RuntimeContinuityResult

Must express the result of the selected response without becoming another response owner.

Candidate continuity types:

```text
direct_connection
adjusted_connection
reslice_connection
jump_reconnection
deferred_pending_relation
stopped_for_current_scope
```

---

## 10. E-5 — Validation Principles

Priority E must define both field validation and relational validation.

### Field validation

Examples:

```text
IDs are non-empty strings.
confidence values are within 0.0 to 1.0.
process_index is non-negative.
runtime limits are positive and bounded.
response_type uses the canonical vocabulary.
```

### Cross-object validation

Examples:

```text
BoundaryStateRecord.boundary_ref resolves to readable Boundary evidence or a retained Boundary record.
VOID Boundary State requires an identifiable Boundary relation.
VoidEvidence must not contain deferred or resolved control flags.
RESLICE requires a next SliceRequest or an explicit source reference.
DEFER requires a pending continuity result.
STOP requires terminated_for_current_scope = true.
OperatorResponse evidence refs must resolve within the response or retained state.
parent refs must not create an immediate self-cycle.
```

These are API consistency rules.

They are not Gyro Logic definitions.

---

## 11. E-6 — `/loop/step` Execution Contract

The endpoint should execute exactly one bounded Gyro Process.

Candidate execution order:

```text
1. Validate LoopStepRequest.
2. Resolve Runtime Structure and explicit retained references.
3. Create Process identity.
4. Execute Slice using Orientation and SlicePolicy.
5. Produce Boundary-aware SliceDone.
6. Read StabilityResult from the established Slice result.
7. Select OperatorResponse through LoopController policy.
8. Produce RuntimeContinuityResult.
9. Apply optional bounded update or prepare next SliceRequest.
10. Persist or return Memory / Trajectory records.
11. Return LoopStepResult.
```

The endpoint must not recursively execute unlimited next processes.

A `RESLICE` response may prepare the next request without executing it in the same call unless an explicitly bounded execution mode is later introduced.

Recommended first implementation:

```text
one HTTP request
=
one Gyro Process
```

---

## 12. E-7 — Supporting Endpoints

Supporting endpoints should remain subordinate to `/loop/step`.

Candidate read endpoints:

```text
GET /loop/state/{loop_id}
GET /loop/history/{loop_id}
GET /trajectory/{trajectory_id}
GET /memory/record/{record_id}
GET /health
```

Candidate bounded execution or maintenance endpoints:

```text
POST /reslice/execute
POST /memory/retrieve
POST /memory/compress
```

These endpoints must not become alternative response owners.

For example:

```text
POST /reslice/execute
= execute an already selected Re-Slice request
≠ decide RESLICE
```

Priority E should initially minimize supporting endpoints.

---

## 13. E-8 — HTTP Status and Runtime Result Separation

Runtime outcomes are not automatically HTTP errors.

The following may be valid `2xx` Runtime results:

```text
Boundary State = UNKNOWN
Boundary State = VOID
Stability status = not_evaluable
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

Candidate HTTP categories:

```text
200
= valid Gyro Process result

400
= malformed request syntax or unsupported enum

404
= explicitly referenced retained record does not exist

409
= lineage, identity, or current-state conflict

422
= semantically invalid object relation

429
= bounded runtime or rate policy rejects execution

500
= unexpected implementation failure
```

Priority E must define a structured API error object separately from Runtime result objects.

---

## 14. API Error Object Candidate

```python
class ApiError:
    error_code: str
    message: str
    field_path: str | None
    related_refs: list[str]
    retryable: bool
    details: dict
```

An API error must not masquerade as:

```text
StabilityResult
Boundary State
VoidEvidence
OperatorResponse
RuntimeContinuityResult
```

---

## 15. E-9 — Implementation and Test Plan

Implementation should begin only after E-1 through E-8 are stable.

Recommended first implementation scope:

```text
Python
FastAPI
Pydantic models
in-memory repository
one-process-per-request
no background worker
no database
no authentication
no distributed state
no automatic recursive loop
```

Required test categories:

```text
schema validation tests
cross-reference validation tests
response vocabulary tests
Boundary / Void separation tests
continuity consistency tests
one-process execution tests
bounded limit tests
HTTP versus Runtime result tests
lineage preservation tests
```

The PoC decision policy may be deterministic, but must be isolated from the schema and labeled as implementation policy.

---

## 16. Documents Likely Affected

Priority E will likely create or update:

```text
docs/14_api_design.md
docs/26_poc_runtime_object_graph.md
docs/27_claude_poc_implementation_prompt.md
new Priority E schema documents
new API implementation plan
new API test specification
README.md
README_jp.md
```

Actual source-code paths must be assessed before code creation.

Priority E should not assume a package structure that has not yet been selected.

---

## 17. Initial Risks

### Risk 1: Over-large request and response

The complete conceptual model may produce an impractically large first API schema.

Mitigation:

```text
define canonical full model
+
define bounded first implementation profile
```

### Risk 2: Hidden server state

A convenient stateful server may make lineage impossible to reconstruct externally.

Mitigation:

```text
explicit IDs
explicit refs
explicit parent lineage
explicit continuity result
```

### Risk 3: Schema becoming theory

Pydantic classes and enums may be mistaken for permanent theoretical definitions.

Mitigation:

```text
label implementation vocabulary and subsets explicitly
```

### Risk 4: Decision policy embedded in validation

Validation such as `VOID → DEFER` would collapse evidence and response responsibility.

Mitigation:

```text
validation checks consistency
policy selects response
```

### Risk 5: Support endpoints becoming alternate controllers

Mitigation:

```text
all support execution requires an already selected request or explicit maintenance command
```

---

## 18. Priority E Acceptance Criteria

Priority E is complete when:

```text
1. API execution and state boundaries are explicit.
2. Request and response schemas are canonical and testable.
3. Embedded evidence and external references are unambiguous.
4. Boundary State vocabulary and implementation subsets are labeled correctly.
5. SliceDone, StabilityResult, OperatorResponse, and RuntimeContinuityResult remain separate.
6. Canonical response vocabulary is enforced.
7. Cross-object validation rules are defined.
8. Runtime outcomes are separated from HTTP errors.
9. Supporting endpoints do not own Operator Response.
10. A bounded FastAPI implementation and test plan is ready.
```

---

## 19. Priority E Decision

Priority E will proceed slowly as an API contract refinement before implementation.

The first step is:

```text
Priority E-1
= API Boundary and Execution Model
```

E-1 should decide:

```text
stateful versus stateless boundary
one-request / one-process rule
identity ownership
embedded objects versus references
persistence expectations
replay and reconstruction requirements
```

No endpoint code should be treated as canonical until these boundaries are fixed.
