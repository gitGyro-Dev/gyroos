# 53. Canonical Request Schema

---

## 1. Purpose

This document defines **Priority E-2: Canonical Request Schema** for the GyroOS API.

The purpose is to fix the request-side contract for:

```text
POST /loop/step
```

before response schemas, cross-reference validation, HTTP error semantics, or implementation code are finalized.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The request represents the input boundary of one bounded Gyro Process.

It does not redefine the Core.

---

## 2. E-2 Decision Summary

The canonical request object is:

```text
LoopStepRequest
├─ request_id
├─ loop_id
├─ idempotency_key
├─ client_trace_id
├─ structure
├─ slice_request
├─ runtime_limits
├─ previous_state_ref
├─ expected_current_scope_ref
├─ policy_ref
├─ request_context
└─ metadata
```

The first API follows these principles:

```text
one LoopStepRequest
=
one bounded Gyro Process request
```

```text
current Runtime Structure
+
current Slice execution context
+
explicit retained references when required
```

The request must not depend on an unidentified hidden current state.

---

## 3. Canonical JSON Shape

```json
{
  "request_id": "request_001",
  "loop_id": "loop_001",
  "idempotency_key": "loop_001-step-0001",
  "client_trace_id": null,
  "structure": {
    "structure_id": "structure_001",
    "current_mode": {},
    "retained_conditions": {},
    "continuity_refs": [],
    "constraints": {},
    "metadata": {}
  },
  "slice_request": {
    "mode": "SLICE",
    "source_type": "RUNTIME_STRUCTURE",
    "source_ref": "structure_001",
    "orientation": {
      "orientation_id": "orientation_001",
      "weights": {},
      "resolution": {},
      "target_dimensions": [],
      "constraints": {},
      "metadata": {}
    },
    "slice_policy": {
      "policy_id": "slice_policy_001",
      "policy_type": "DEFAULT",
      "parameters": {},
      "constraints": {},
      "metadata": {}
    },
    "context_refs": [],
    "boundary_refs": [],
    "boundary_state_refs": [],
    "void_refs": [],
    "parent_process_ref": null,
    "parent_slice_ref": null,
    "trajectory_ref": null,
    "requested_by_response_ref": null,
    "metadata": {}
  },
  "runtime_limits": {
    "max_slice_operations": 1,
    "max_reslice_depth": 2,
    "max_context_chain_length": 3,
    "max_branch_count": 2,
    "max_evidence_refs": 128,
    "max_payload_bytes": 1048576,
    "deadline_ms": 5000
  },
  "previous_state_ref": null,
  "expected_current_scope_ref": null,
  "policy_ref": "loop_policy_v1",
  "request_context": {
    "requested_at": null,
    "caller_type": "CLIENT",
    "locale": null,
    "tags": []
  },
  "metadata": {}
}
```

Exact serialization may evolve.

The semantic ownership and validation rules defined here are canonical for the first bounded API.

---

## 4. Required and Optional Fields

### Required

```text
request_id
loop_id
structure
slice_request
runtime_limits
```

### Optional and nullable

```text
idempotency_key
client_trace_id
previous_state_ref
expected_current_scope_ref
policy_ref
request_context
metadata
```

`metadata` may be omitted and default to an empty object.

The absence of an optional field must not silently imply a hidden server-side value unless the endpoint contract explicitly defines that default.

---

## 5. LoopStepRequest

Candidate model:

```python
class LoopStepRequest:
    request_id: str
    loop_id: str

    structure: RuntimeStructureInput
    slice_request: SliceRequest
    runtime_limits: RuntimeLimits

    idempotency_key: str | None = None
    client_trace_id: str | None = None

    previous_state_ref: str | None = None
    expected_current_scope_ref: str | None = None
    policy_ref: str | None = None

    request_context: RequestContext | None = None
    metadata: dict = {}
```

The implementation should use safe default factories rather than mutable class-level defaults.

---

## 6. Request Identity

### request_id

```text
request_id
= client-provided correlation identity for one API request
```

Rules:

```text
required
non-empty
client-owned
not reused for a different canonical request within the same operational scope
```

`request_id` is not `process_id`.

### loop_id

```text
loop_id
= logical Gyro Loop or execution-thread identity
```

Rules:

```text
required
non-empty
client-selected or previously issued
may be reused across multiple /loop/step calls
```

A successful non-replay execution creates a new server-owned `process_id` under the loop.

### idempotency_key

```text
idempotency_key
= optional retry identity within loop_id
```

Recommended scope:

```text
(loop_id, idempotency_key)
```

Rules:

```text
same key + same canonical request digest
→ return prior completed result

same key + different canonical request digest
→ identity conflict
```

The exact HTTP mapping is finalized in E-8.

### client_trace_id

Optional observability value.

It must not change Runtime semantics.

---

## 7. RuntimeStructureInput

Canonical model:

```python
class RuntimeStructureInput:
    structure_id: str
    current_mode: dict
    retained_conditions: dict
    continuity_refs: list[str]
    constraints: dict
    metadata: dict
```

### Meaning

```text
Runtime Structure
= the current Runtime mode in which a next establishment can become possible through Slice
```

It must not be reduced to:

```text
raw payload
initial input only
immutable container
application object verdict
```

### Required fields

```text
structure_id
current_mode
```

### Optional fields with empty defaults

```text
retained_conditions
continuity_refs
constraints
metadata
```

### Rules

```text
structure_id is non-empty
current_mode is an object
continuity_refs contain unique non-empty references
constraints are request-side execution constraints, not Operator Responses
```

A request must not send both an embedded Structure and a conflicting retained Structure under the same identity.

Conflict handling is finalized in E-5 and E-8.

---

## 8. SliceRequest

Canonical model:

```python
class SliceRequest:
    mode: SliceMode
    source_type: SliceSourceType
    source_ref: str

    orientation: OperatorOrientation
    slice_policy: SlicePolicy

    context_refs: list[str]
    boundary_refs: list[str]
    boundary_state_refs: list[str]
    void_refs: list[str]

    parent_process_ref: str | None
    parent_slice_ref: str | None
    trajectory_ref: str | None
    requested_by_response_ref: str | None

    metadata: dict
```

`SliceRequest` is the API representation of the Slice execution context.

Operator Orientation and Slice Policy remain internal to Slice.

They are not independent Core stages.

---

## 9. SliceMode

Canonical values:

```text
SLICE
RESLICE
```

Meaning:

```text
SLICE
= Slice over the current Runtime Structure or another explicitly valid initial source

RESLICE
= Slice applied again to a retained Runtime source relation
```

`RESLICE` is an implementation mode marker.

It does not introduce a second theoretical operation.

Compatibility values such as:

```text
RESLICE_CONTEXT
```

must not appear in the enum.

---

## 10. SliceSourceType

Canonical initial values:

```text
RUNTIME_STRUCTURE
SLICE_DONE
CONTEXT_EVIDENCE
BOUNDARY_EVIDENCE
BOUNDARY_STATE_RECORD
VOID_EVIDENCE
TRAJECTORY_SEGMENT
PRIOR_PROCESS_RESULT
RETAINED_RELATION
```

The vocabulary is implementation-controlled and may expand later.

It is not a new Gyro Logic classification.

### Initial Slice rule

For the first implementation:

```text
mode = SLICE
→ source_type SHOULD be RUNTIME_STRUCTURE
```

An alternative initial source type requires an explicitly documented support mode.

### Re-Slice rule

```text
mode = RESLICE
→ source_type MUST identify a retained Runtime source
```

Examples:

```text
CONTEXT_EVIDENCE
SLICE_DONE
BOUNDARY_EVIDENCE
VOID_EVIDENCE
TRAJECTORY_SEGMENT
RETAINED_RELATION
```

The existence of any such evidence does not itself select `RESLICE`.

The request represents a Re-Slice already selected by a prior `OperatorResponse` or an explicitly authorized execution caller.

---

## 11. source_ref

`source_ref` is required and non-null.

Rules:

```text
mode = SLICE
source_type = RUNTIME_STRUCTURE
→ source_ref MUST equal structure.structure_id
```

```text
mode = RESLICE
→ source_ref MUST resolve to an object compatible with source_type
```

Incorrect:

```text
source_type = CONTEXT_EVIDENCE
source_ref resolves to VoidEvidence
```

Incorrect:

```text
source_ref omitted because server knows the latest Context
```

The source identity must be explicit.

---

## 12. OperatorOrientation

Canonical model:

```python
class OperatorOrientation:
    orientation_id: str
    weights: dict[str, float]
    resolution: dict[str, float]
    target_dimensions: list[str]
    constraints: dict
    metadata: dict
```

### Required fields

```text
orientation_id
```

### Optional fields with empty defaults

```text
weights
resolution
target_dimensions
constraints
metadata
```

### Rules

```text
orientation_id is non-empty
weights contain finite numeric values
resolution contains finite non-negative numeric values
target_dimensions contain unique non-empty strings
```

Orientation describes the direction under which Slice is executed.

It must not contain an Operator Response such as:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

---

## 13. SlicePolicy

Canonical model:

```python
class SlicePolicy:
    policy_id: str
    policy_type: str
    parameters: dict
    constraints: dict
    metadata: dict
```

### Required fields

```text
policy_id
policy_type
```

### Optional fields with empty defaults

```text
parameters
constraints
metadata
```

### Rules

```text
policy_id is non-empty
policy_type is non-empty
parameters and constraints are objects
```

`SlicePolicy` is an implementation-level representation of Slice-internal Orientation conditions.

It does not own `OperatorResponse` selection.

---

## 14. Evidence Reference Collections

`SliceRequest` may contain:

```text
context_refs
boundary_refs
boundary_state_refs
void_refs
```

These are input references available to the current Slice.

They are not declarations that the referenced relation is currently true, active, or decisive.

Rules:

```text
all refs are non-empty
refs are unique within each collection
referenced records must exist or be resolvable
cross-type identity reuse is rejected unless explicitly modeled
```

Important:

```text
void_refs present
≠ mode must be RESLICE
≠ OperatorResponse must be DEFER
```

```text
boundary_state_refs contain VOID
≠ automatic DEFER
```

These collections provide evidence access only.

---

## 15. Parent and Lineage References

### parent_process_ref

Reference to the Process from which the current Slice request was prepared.

### parent_slice_ref

Reference to the prior Slice result from which the current request derives.

### trajectory_ref

Reference to the trajectory scope to extend or branch.

### requested_by_response_ref

Reference to the prior `OperatorResponse` that authorized or prepared this request.

### Initial Slice rule

For an initial independent Process:

```text
mode = SLICE
parent_process_ref = null
parent_slice_ref = null
requested_by_response_ref = null
```

A `trajectory_ref` may still be present when explicitly continuing an existing trajectory.

### Re-Slice rule

For the canonical first implementation:

```text
mode = RESLICE
→ parent_process_ref is required
→ parent_slice_ref is required
→ requested_by_response_ref is required
```

An administrative or replay execution may use an explicitly documented exception, but must still preserve equivalent provenance.

### Cycle rule

No reference may point to the Process or Slice being created by the same request.

Immediate self-cycles are invalid.

Deeper lineage cycle rules are finalized in E-5.

---

## 16. RuntimeLimits

Canonical model:

```python
class RuntimeLimits:
    max_slice_operations: int
    max_reslice_depth: int
    max_context_chain_length: int
    max_branch_count: int
    max_evidence_refs: int
    max_payload_bytes: int
    deadline_ms: int
```

### Required fields

The `runtime_limits` object is required.

For the first implementation, all fields should be explicit.

### Fixed initial invariant

```text
max_slice_operations = 1
```

This preserves:

```text
one HTTP request
=
one bounded Gyro Process
```

### Validation principles

```text
all values are positive integers
max_slice_operations must equal 1 in the first implementation
server policy may lower client-requested limits
client cannot exceed server maximums
```

A server lowering limits must expose the effective limits in the result or execution metadata.

Runtime limits constrain execution.

They do not select an Operator Response.

---

## 17. previous_state_ref

`previous_state_ref` is optional.

It may point to a retained prior state snapshot or current-scope view used to resolve explicit state.

Rules:

```text
must be resolvable when supplied
must belong to the same loop or an explicitly permitted imported scope
must not silently override embedded request data
```

If embedded data conflicts with the referenced prior state, the API must reject or explicitly resolve the conflict under a documented rule.

Silent precedence is not allowed.

---

## 18. expected_current_scope_ref

This optional field supports optimistic concurrency.

Meaning:

```text
execute this step only if the server current-scope pointer still equals this reference
```

Candidate behavior:

```text
expected ref matches
→ execution may proceed

expected ref differs
→ current-state conflict
```

The likely HTTP result is `409 Conflict`, finalized in E-8.

This field does not replace complete history.

It only protects the selected current scope.

---

## 19. policy_ref

`policy_ref` identifies the Loop Controller or runtime policy version used for the current step.

It is optional at the schema level but recommended for replayability.

Rules:

```text
must be resolvable when supplied
must not refer to an application verdict policy as if it were GyroOS Core
must be recorded in the result or execution metadata
```

The policy may implement bounded deterministic rules.

Those rules remain implementation policy, not Gyro Logic definitions.

---

## 20. RequestContext

Candidate model:

```python
class RequestContext:
    requested_at: str | None
    caller_type: str
    locale: str | None
    tags: list[str]
```

Canonical initial caller types:

```text
CLIENT
INTERNAL
REPLAY
ADMINISTRATIVE
```

`RequestContext` is operational metadata.

It must not silently determine Boundary State, Stability, or Operator Response.

If caller type affects policy, the policy dependence must be explicit and traceable.

---

## 21. metadata

`metadata` is an extension object.

Rules:

```text
must be a JSON object
must not redefine canonical fields
must not contain hidden required values
must not carry an alternate Operator Response
must not carry application verdicts as GyroOS Runtime truth
```

Canonical fields always take precedence over similarly named metadata keys.

The implementation should reject reserved-key collisions where practical.

---

## 22. Embedded Object and Reference Rules

The request may combine:

```text
embedded Runtime Structure
+
explicit evidence references
```

The first implementation does not require embedded copies of all referenced evidence.

However:

```text
reference-only input
→ every required reference must be resolvable
```

```text
embedded object and retained object use same identity
→ canonical content must match
```

Ambiguous duplicate identity is invalid.

The API must not guess which representation is authoritative.

---

## 23. Initial Slice Request Example

```json
{
  "request_id": "request_initial_001",
  "loop_id": "loop_001",
  "idempotency_key": "loop_001-step-001",
  "structure": {
    "structure_id": "structure_001",
    "current_mode": {
      "signal": 0.72
    },
    "retained_conditions": {},
    "continuity_refs": [],
    "constraints": {},
    "metadata": {}
  },
  "slice_request": {
    "mode": "SLICE",
    "source_type": "RUNTIME_STRUCTURE",
    "source_ref": "structure_001",
    "orientation": {
      "orientation_id": "orientation_default",
      "weights": {},
      "resolution": {},
      "target_dimensions": ["signal"],
      "constraints": {},
      "metadata": {}
    },
    "slice_policy": {
      "policy_id": "slice_policy_default",
      "policy_type": "DEFAULT",
      "parameters": {},
      "constraints": {},
      "metadata": {}
    },
    "context_refs": [],
    "boundary_refs": [],
    "boundary_state_refs": [],
    "void_refs": [],
    "parent_process_ref": null,
    "parent_slice_ref": null,
    "trajectory_ref": null,
    "requested_by_response_ref": null,
    "metadata": {}
  },
  "runtime_limits": {
    "max_slice_operations": 1,
    "max_reslice_depth": 2,
    "max_context_chain_length": 3,
    "max_branch_count": 2,
    "max_evidence_refs": 128,
    "max_payload_bytes": 1048576,
    "deadline_ms": 5000
  },
  "previous_state_ref": null,
  "expected_current_scope_ref": null,
  "policy_ref": "loop_policy_v1",
  "request_context": {
    "requested_at": null,
    "caller_type": "CLIENT",
    "locale": null,
    "tags": []
  },
  "metadata": {}
}
```

---

## 24. Re-Slice Request Example

```json
{
  "request_id": "request_reslice_002",
  "loop_id": "loop_001",
  "idempotency_key": "loop_001-step-002",
  "structure": {
    "structure_id": "structure_002",
    "current_mode": {},
    "retained_conditions": {
      "parent_slice_ref": "slice_001"
    },
    "continuity_refs": ["continuity_001"],
    "constraints": {},
    "metadata": {}
  },
  "slice_request": {
    "mode": "RESLICE",
    "source_type": "CONTEXT_EVIDENCE",
    "source_ref": "context_001",
    "orientation": {
      "orientation_id": "orientation_context_002",
      "weights": {},
      "resolution": {},
      "target_dimensions": ["surrounding_relation"],
      "constraints": {},
      "metadata": {}
    },
    "slice_policy": {
      "policy_id": "slice_policy_context_002",
      "policy_type": "CONTEXT_FOCUSED",
      "parameters": {},
      "constraints": {},
      "metadata": {}
    },
    "context_refs": ["context_001"],
    "boundary_refs": [],
    "boundary_state_refs": ["boundary_state_unknown_001"],
    "void_refs": [],
    "parent_process_ref": "process_001",
    "parent_slice_ref": "slice_001",
    "trajectory_ref": "trajectory_001",
    "requested_by_response_ref": "response_001",
    "metadata": {}
  },
  "runtime_limits": {
    "max_slice_operations": 1,
    "max_reslice_depth": 2,
    "max_context_chain_length": 3,
    "max_branch_count": 2,
    "max_evidence_refs": 128,
    "max_payload_bytes": 1048576,
    "deadline_ms": 5000
  },
  "previous_state_ref": "state_scope_001",
  "expected_current_scope_ref": "state_scope_001",
  "policy_ref": "loop_policy_v1",
  "request_context": {
    "requested_at": null,
    "caller_type": "CLIENT",
    "locale": null,
    "tags": ["reslice"]
  },
  "metadata": {}
}
```

---

## 25. Invalid Request Examples

### Hidden latest Context

```json
{
  "slice_request": {
    "mode": "RESLICE",
    "source_type": "CONTEXT_EVIDENCE",
    "source_ref": null
  }
}
```

Invalid because the source identity is not explicit.

### Mismatched initial source

```text
mode = SLICE
source_type = RUNTIME_STRUCTURE
source_ref != structure.structure_id
```

Invalid because the Slice source conflicts with the embedded Structure.

### Re-Slice without lineage

```text
mode = RESLICE
parent_process_ref = null
parent_slice_ref = null
requested_by_response_ref = null
```

Invalid in the canonical first implementation.

### Response encoded in Orientation

```json
{
  "orientation": {
    "next_action": "DEFER"
  }
}
```

Invalid as canonical semantics.

Orientation does not own Operator Response.

### Void implies Defer

```json
{
  "void_refs": ["void_001"],
  "metadata": {
    "forced_response": "DEFER"
  }
}
```

Invalid because evidence presence does not directly determine Response.

---

## 26. Security and Resource Safety

The request schema must support bounded parsing and execution.

Minimum safeguards:

```text
maximum body size
maximum metadata depth
maximum collection length
maximum string length
finite numeric validation
reference count limit
execution deadline
```

Client-supplied limits cannot weaken server safety policy.

Unknown metadata must not bypass canonical validation.

---

## 27. Canonicalization for Idempotency

Before calculating a request digest, the implementation should canonicalize:

```text
object key ordering
explicit defaults
normalized enum casing
unique reference ordering when order is semantically irrelevant
excluded transient fields
```

Candidate transient fields excluded from semantic digest:

```text
client_trace_id
request_context.requested_at
non-semantic observability metadata
```

The exact canonicalization algorithm is finalized during implementation planning.

It must be versioned.

---

## 28. Acceptance Criteria

Priority E-2 is complete when:

```text
1. LoopStepRequest fields are identified.
2. Required, optional, and nullable fields are distinguished.
3. Client-owned and server-owned identities remain separate.
4. RuntimeStructureInput is not reduced to a raw payload.
5. OperatorOrientation and SlicePolicy remain internal to Slice execution context.
6. SLICE and RESLICE use explicit source identity.
7. Re-Slice lineage is required and traceable.
8. Evidence references do not act as automatic response triggers.
9. Runtime limits preserve one request = one Process.
10. Embedded and referenced identity conflicts are rejected rather than guessed.
11. Metadata cannot replace canonical semantics.
12. The schema is ready for Pydantic modeling after E-5 validation rules are finalized.
```

---

## 29. Priority E-2 Decision

```text
Status: ACCEPTED
```

The canonical request schema is fixed at the conceptual API-contract level.

The next step is:

```text
Priority E-3
= Canonical SliceDone and Evidence Schemas
```
