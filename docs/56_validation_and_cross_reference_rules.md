# 56. Validation and Cross-reference Rules

---

## 1. Purpose

This document defines **Priority E-5: Validation and Cross-reference Rules** for the GyroOS API.

The purpose is to fix the validation contract for:

```text
POST /loop/step
```

before the full execution contract, supporting endpoints, HTTP error mapping, and implementation code are finalized.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Validation protects the Runtime representation of this Core.

It does not redefine the Core and does not select an OperatorResponse.

---

## 2. E-5 Decision Summary

Validation is divided into five ordered layers:

```text
1. Serialization and field validation
2. Identity and reference validation
3. Lineage and graph validation
4. Cross-object semantic validation
5. Execution-precondition validation
```

The canonical relation is:

```text
request received
↓
field-valid
↓
identity-valid
↓
reference-resolvable
↓
lineage-valid
↓
cross-object-consistent
↓
execution-preconditions satisfied
↓
one bounded Gyro Process may begin
```

No Process artifact should be published before pre-execution validation succeeds.

---

## 3. Validation Is Not Runtime Judgment

The API must distinguish:

```text
invalid API object relation
```

from:

```text
valid Runtime result expressing uncertainty, unreadability, or non-continuation
```

The following may be valid Runtime results:

```text
Boundary State = UNKNOWN
Boundary State = VOID
StabilityStatus = NOT_EVALUABLE
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

They are not validation errors merely because they express uncertainty, unreadability, pending relation, non-continuous reconnection, or current-scope termination.

Validation errors include:

```text
missing required field
unsupported enum
unresolvable explicit reference
conflicting duplicate identity
invalid parent lineage
response / continuity mismatch
RESLICE without a valid retained source
VOID classification without an identifiable Boundary
```

---

## 4. Validation Phases

### Phase 1: Request-shape validation

Validate the serialized `LoopStepRequest` without resolving external references.

Examples:

```text
required fields exist
field types are valid
enums use canonical values
numeric ranges are valid
collection elements are structurally valid
payload and list limits are respected
```

### Phase 2: Reference-resolution validation

Resolve every explicit Runtime reference required for the current step.

Examples:

```text
source_ref
previous_state_ref
expected_current_scope_ref
trajectory_ref
context_refs
boundary_refs
boundary_state_refs
void_refs
parent_process_ref
parent_slice_ref
requested_by_response_ref
```

### Phase 3: Semantic pre-execution validation

Validate relations among request objects and resolved records.

Examples:

```text
SliceMode and source_type compatibility
source_ref type compatibility
Re-Slice lineage completeness
current-scope optimistic concurrency
idempotency identity consistency
```

### Phase 4: Generated-result validation

After Runtime engines produce result objects, validate the complete result group before publication.

```text
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
UpdateDecision when present
NextProcessPreparation when present
created records and trajectory edges
```

### Phase 5: Persistence validation

Confirm that required records can be persisted atomically or returned as a complete non-persisted result according to the endpoint mode.

---

## 5. Common Field Rules

### 5.1 IDs and references

Every ID or reference must be:

```text
non-empty
trimmed
within configured length limits
free from control characters
```

IDs are opaque identifiers.

The API must not infer semantic type solely from a string prefix such as:

```text
ctx_
boundary_
void_
```

Type compatibility is established by the resolved object or registered record type.

### 5.2 Collection fields

Canonical collection fields must:

```text
be present when required
use arrays
contain no null elements
contain unique references unless ordering explicitly permits repetition
respect max_evidence_refs and payload limits
```

Empty lists are valid.

```text
empty list
≠ field not evaluated
```

Evaluation state must be represented explicitly when needed.

### 5.3 Numeric values

Confidence, readability, connectability, Stability value, and similar normalized values must satisfy:

```text
0.0 <= value <= 1.0
```

Numeric values must be finite.

The following are invalid:

```text
NaN
Infinity
-Infinity
```

### 5.4 Timestamps

Runtime timestamps must use one documented timezone-aware format.

Recommended first implementation:

```text
RFC 3339 / ISO 8601 in UTC
```

A timestamp must not be used as the sole lineage identifier.

### 5.5 Metadata

`metadata` may contain extension data but must not:

```text
override canonical fields
introduce an alternate OperatorResponse
hide required identity
hide unresolved references
change validation outcome without an explicit extension contract
```

---

## 6. Enum Validation

Canonical enums are case-sensitive in the first API.

### SliceMode

```text
SLICE
RESLICE
```

### OperatorResponseType

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

### RuntimeContinuityType

```text
DIRECT_CONNECTION
ADJUSTED_CONNECTION
RESLICE_CONNECTION
JUMP_RECONNECTION
DEFERRED_PENDING_RELATION
STOPPED_FOR_CURRENT_SCOPE
```

### StabilityStatus

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED
```

Compatibility aliases must not pass canonical request validation:

```text
CHANGE_ORIENTATION
RESLICE_CONTEXT
DEFER_VOID
VOID as OperatorResponse
```

Legacy records may be translated only by an explicit compatibility adapter before canonical validation.

---

## 7. Identity Ownership and Uniqueness

### Client-owned correlation identities

```text
request_id
loop_id
idempotency_key
client_trace_id
```

### Server-owned Runtime artifact identities

```text
process_id
slice_id
boundary_evidence_id
boundary_state_record_id
context_evidence_id
void_evidence_id
stability_result_id
operator_response_id
continuity_result_id
update_decision_id
trajectory_edge_id
record_id
```

Rules:

```text
all embedded Runtime artifact IDs are unique within one LoopStepResult
server-owned generated IDs do not collide with retained records
client correlation IDs do not substitute for Runtime artifact IDs
```

Imported records may retain externally supplied IDs only when:

```text
provenance is explicit
identity uniqueness is verified
content digest is known or computable
record type is known
```

---

## 8. Embedded Object and Reference Consistency

The API permits both:

```text
embedded object
+
explicit reference
```

When the same identity appears in both forms:

```text
embedded identity
=
resolved referenced identity
```

and:

```text
canonical embedded content digest
=
canonical resolved content digest
```

must hold.

Otherwise validation fails with a conflicting identity relation.

The API must not silently choose one side.

Incorrect:

```text
embedded ContextEvidence ctx_001 contains content A
context_refs includes ctx_001 resolving to content B
→ accept embedded version
```

Correct:

```text
→ reject as conflicting duplicate identity
```

---

## 9. Reference Resolution Rules

Every required explicit reference must resolve to exactly one compatible record.

### Type compatibility examples

```text
source_type = CONTEXT_EVIDENCE
→ source_ref resolves to ContextEvidence
```

```text
source_type = BOUNDARY_STATE_RECORD
→ source_ref resolves to BoundaryStateRecord
```

```text
stability_result_ref
→ resolves to StabilityResult
```

```text
operator_response_ref
→ resolves to OperatorResponse
```

A reference resolving to the wrong object type is invalid even when the ID exists.

### No implicit latest-object resolution

The API must not resolve:

```text
latest SliceDone
latest Boundary
latest Boundary State
latest Context
latest Void evidence
latest Orientation
```

unless an explicit current-scope reference contract identifies the object.

### Missing optional references

An optional null reference is valid only where the schema explicitly permits null.

```text
null optional reference
≠ unresolved non-null reference
```

---

## 10. Request Cross-object Rules

### 10.1 Initial Slice

For the first implementation:

```text
slice_request.mode = SLICE
→ slice_request.source_type = RUNTIME_STRUCTURE
→ slice_request.source_ref = structure.structure_id
```

An explicitly documented extension mode may support another initial source later.

### 10.2 Re-Slice

```text
slice_request.mode = RESLICE
```

requires:

```text
source_type identifies a retained Runtime source
source_ref resolves to that source type
parent_process_ref is present
parent_slice_ref is present
requested_by_response_ref is present
requested_by_response_ref resolves to OperatorResponseType.RESLICE
```

The referenced prior response must have prepared or authorized the submitted Re-Slice request.

### 10.3 Orientation and SlicePolicy

```text
orientation.orientation_id is non-empty
slice_policy.policy_id is non-empty
slice_policy.policy_type is non-empty
```

Orientation and SlicePolicy must not contain canonical OperatorResponse ownership fields.

### 10.4 Runtime limits

```text
max_slice_operations = 1
```

for the first API.

All configured limits must be positive and must not exceed server hard limits.

A client cannot expand the server's maximum execution boundary by submitting a larger value.

### 10.5 Current-scope concurrency

When `expected_current_scope_ref` is present:

```text
expected_current_scope_ref
=
server current-scope ref
```

must hold before execution.

Mismatch is a current-state conflict, not a Runtime `STOP` result.

---

## 11. Idempotency Validation

Recommended idempotency scope:

```text
(loop_id, idempotency_key)
```

Rules:

```text
same key + same canonical request digest
→ return previous completed LoopStepResult
```

```text
same key + different canonical request digest
→ identity conflict
```

Transient observability fields excluded from the canonical digest must be explicitly documented.

Examples may include:

```text
client_trace_id
transport receipt timestamp
```

Semantic fields must never be excluded merely for convenience.

---

## 12. SliceDone Validation

Generated `SliceDone` must satisfy:

```text
slice_id is unique
process_id equals current Process identity
structure_ref resolves to request Structure or retained source Structure
orientation_ref equals executed Orientation identity
slice_policy_ref equals executed SlicePolicy identity
source_type and source_ref equal the executed SliceRequest source
```

Collection fields must be present:

```text
boundary_evidence
boundary_state_records
context_evidence
void_evidence
boundary_refs
boundary_state_refs
context_refs
void_refs
```

`SliceDone` must not contain:

```text
OperatorResponse selection
RuntimeContinuity disposition
HTTP status
application verdict
```

---

## 13. BoundaryEvidence Validation

Each `BoundaryEvidence` must satisfy:

```text
boundary_evidence_id is unique
slice_id equals SliceDone.slice_id
process_id equals SliceDone.process_id
relation_ref is non-empty
boundary_readability is within 0.0 to 1.0
```

Lineage and relation reference lists must contain valid unique references.

A Slice may produce zero, one, or multiple BoundaryEvidence objects.

```text
no BoundaryEvidence
≠ invalid SliceDone
```

---

## 14. BoundaryStateRecord Validation

Each `BoundaryStateRecord` must satisfy:

```text
boundary_state_record_id is unique
slice_id equals SliceDone.slice_id
process_id equals SliceDone.process_id
boundary_ref resolves to BoundaryEvidence or a retained Boundary record
relation_ref is non-empty
state_type is a supported Boundary State value
boundary_state_confidence is within 0.0 to 1.0
classification_reason is non-empty
```

A later classification must not overwrite an earlier record under the same identity.

Reclassification requires a new identity and appropriate lineage such as:

```text
refined_from_refs
reclassified_from_refs
supersedes_for_current_scope_refs
```

---

## 15. VOID Boundary State Validation

A `BoundaryStateRecord` with:

```text
state_type = VOID
```

requires:

```text
1. boundary_ref resolves to an identifiable Boundary relation
2. relation_ref identifies the target relation
3. evidence supports insufficient target readability or connectability relative to that Boundary
```

When the Boundary distinction itself is unreadable:

```text
→ do not force state_type = VOID
```

Instead retain:

```text
unclassified Boundary evidence
or
unreadable distinction evidence
```

A `VOID` state does not require or imply:

```text
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

---

## 16. ContextEvidence Validation

Each `ContextEvidence` must satisfy:

```text
context_evidence_id is unique
slice_id equals SliceDone.slice_id
process_id equals SliceDone.process_id
relation_ref is non-empty
source_type is supported
context_confidence is within 0.0 to 1.0
```

When present:

```text
context_readability
inferability
```

must each be within `0.0` to `1.0`.

Parent Context references must not create an immediate self-cycle.

The existence of ContextEvidence does not validate or select `RESLICE` by itself.

---

## 17. VoidEvidence Validation

Each `VoidEvidence` must satisfy:

```text
void_evidence_id is unique
slice_id equals SliceDone.slice_id
process_id equals SliceDone.process_id
boundary_ref resolves to an identifiable Boundary relation
relation_ref is non-empty
reason is non-empty
```

When present:

```text
target_relation_readability
connectability
```

must each be within `0.0` to `1.0`.

The following fields are prohibited:

```text
deferred
resolved
should_defer
should_jump
should_stop
```

VoidEvidence does not select an OperatorResponse.

---

## 18. StabilityResult Validation

`StabilityResult` must satisfy:

```text
process_id = SliceDone.process_id
slice_id = SliceDone.slice_id
status uses StabilityStatus
reason is non-empty
value, when present, is within 0.0 to 1.0
```

When:

```text
status = NOT_EVALUABLE
```

`value` and `continuability` may be null.

Validation must not force:

```text
continuability = true
→ OperatorResponse = CONTINUE
```

`evidence_refs`, `supporting_evidence_refs`, and `conflicting_evidence_refs` must resolve within current-step objects or retained state.

---

## 19. OperatorResponse Validation

`OperatorResponse` must satisfy:

```text
process_id = SliceDone.process_id
slice_id = SliceDone.slice_id
stability_result_ref = StabilityResult.stability_result_id
response_type uses canonical OperatorResponseType
reason is non-empty
response_confidence, when present, is within 0.0 to 1.0
```

Evidence rules:

```text
decisive_evidence_refs ⊆ considered_evidence_refs
conflicting_evidence_refs SHOULD be a subset of considered_evidence_refs
all refs resolve
```

The API must not validate a response solely through a direct universal mapping such as:

```text
NORMAL → CONTINUE
UNKNOWN → RESLICE
VOID → DEFER
low Stability → STOP
large Deviation → JUMP
```

A deterministic bounded policy is valid only when it is an explicit implementation policy and the response retains its evidence references and reason.

---

## 20. Response-specific Validation

### CONTINUE

```text
next_request MAY be null
continuity_type MUST be DIRECT_CONNECTION
pending MUST be false
terminated_for_current_scope MUST be false
```

### ADJUST

```text
continuity_type MUST be ADJUSTED_CONNECTION
update_decision_ref or explicit adjusted next preparation SHOULD be present
pending MUST be false
terminated_for_current_scope MUST be false
```

### RESLICE

```text
next_request MUST be present
next_request.mode MUST be RESLICE
next_request.requested_by_response_ref MUST equal operator_response_id
next_request source_ref MUST resolve to an explicit retained Runtime source
continuity_type MUST be RESLICE_CONNECTION
```

The current HTTP request must not execute `next_request`.

### JUMP

```text
continuity_type MUST be JUMP_RECONNECTION
jump source MUST be explicit
jump target or target candidate MUST be explicit
trajectory branch relation MUST be retained
```

### DEFER

```text
next_request SHOULD be null
continuity_type MUST be DEFERRED_PENDING_RELATION
pending MUST be true
terminated_for_current_scope MUST be false
DeferredRelationRecord MUST be created or explicitly referenced
```

VoidEvidence must not be mutated with deferred state.

### STOP

```text
next_request MUST be null
continuity_type MUST be STOPPED_FOR_CURRENT_SCOPE
pending MUST be false
terminated_for_current_scope MUST be true
```

STOP must not erase history or imply an application rejection.

---

## 21. RuntimeContinuityResult Validation

`RuntimeContinuityResult` must satisfy:

```text
process_id = SliceDone.process_id
operator_response_ref = OperatorResponse.operator_response_id
source_ref identifies the current established or retained source
continuity_type matches OperatorResponse.response_type
```

Canonical mapping:

| OperatorResponse | RuntimeContinuityType |
|---|---|
| CONTINUE | DIRECT_CONNECTION |
| ADJUST | ADJUSTED_CONNECTION |
| RESLICE | RESLICE_CONNECTION |
| JUMP | JUMP_RECONNECTION |
| DEFER | DEFERRED_PENDING_RELATION |
| STOP | STOPPED_FOR_CURRENT_SCOPE |

`RuntimeContinuityResult` records the resulting relation.

It does not select or override the OperatorResponse.

---

## 22. UpdateDecision Validation

When `UpdateDecision` is present:

```text
process_id = current Process identity
operator_response_ref = OperatorResponse.operator_response_id
reason is non-empty
target_ref is non-empty
```

The update type must be compatible with the selected response.

Examples:

```text
ADJUST
→ ORIENTATION_ADJUSTMENT or POLICY_ADJUSTMENT may be valid
```

```text
JUMP
→ JUMP_TARGET_PREPARATION may be valid
```

An `UpdateDecision` must not introduce a different OperatorResponse.

---

## 23. Lineage Validation

Lineage validation must cover:

```text
parent Process
parent Slice
prior OperatorResponse
source evidence
Boundary State reclassification
Context chain
Trajectory branch
Deferred relation
current-scope supersession
```

### Immediate self-cycle prohibition

An object must not directly reference itself through:

```text
parent_ref
refined_from_ref
reclassified_from_ref
requested_by_response_ref
source_ref
```

### Bounded ancestry validation

The first implementation should validate ancestry up to a configured bound.

```text
validation_depth <= server hard maximum
```

If complete ancestry is external and cannot be resolved, the API must either:

```text
reject when ancestry is required for semantic correctness
or
mark provenance as externally verified under an explicit trust contract
```

It must not silently assume valid lineage.

### Reclassification preservation

A later BoundaryStateRecord may supersede another for current scope but must not reuse or delete the prior identity.

```text
supersedes_for_current_scope
≠ universal invalidation
```

---

## 24. Trajectory Graph Validation

Each generated trajectory edge must have:

```text
unique trajectory_edge_id
valid source Process or continuity ref
valid target Process, pending target, prepared target, or scope boundary
edge type compatible with RuntimeContinuityType
```

JUMP creates a branch or non-continuous reconnection edge.

DEFER creates a pending relation edge.

STOP creates a current-scope terminal boundary edge.

No edge type may silently erase previous branches.

---

## 25. Current-scope Validation

Current-scope views select currently active references without deleting history.

Rules:

```text
all current-scope refs resolve
no two mutually exclusive refs are active unless coexistence is explicit
superseded refs remain historically retrievable
expected_current_scope_ref must match before mutation
```

A current-scope conflict is an API state conflict.

It is not automatically:

```text
OperatorResponse = ADJUST
OperatorResponse = RESLICE
OperatorResponse = STOP
```

---

## 26. Validation Ordering and Short-circuiting

Recommended order:

```text
1. Parse and schema validate
2. Enforce payload and collection limits
3. Canonicalize request for idempotency
4. Check idempotency conflict or replay
5. Resolve explicit references
6. Validate type compatibility
7. Validate request lineage and current scope
8. Begin logical Process transaction
9. Execute one bounded Process
10. Validate generated result objects
11. Validate cross-object and trajectory relations
12. Persist atomically
13. Publish LoopStepResult
```

Validation may short-circuit on failure.

However, an error response should report enough structured detail to identify:

```text
validation layer
error code
field path
related refs
retryability
```

Exact HTTP mapping and error object shape are finalized in E-8.

---

## 27. Validation Severity

Recommended internal categories:

```text
FIELD_INVALID
ENUM_UNSUPPORTED
LIMIT_EXCEEDED
REFERENCE_MISSING
REFERENCE_TYPE_MISMATCH
IDENTITY_CONFLICT
LINEAGE_INVALID
CURRENT_SCOPE_CONFLICT
CROSS_OBJECT_INCONSISTENT
RESULT_INCOMPLETE
PERSISTENCE_PRECONDITION_FAILED
```

These are API validation categories.

They are not:

```text
Boundary States
Stability statuses
Operator Responses
Runtime Continuity types
```

---

## 28. Atomic Publication Rule

A successful `LoopStepResult` must not be published unless the required result group is complete and internally consistent:

```text
SliceDone
+
StabilityResult
+
OperatorResponse
+
RuntimeContinuityResult
+
required lineage and record refs
```

Candidate atomicity rule:

```text
required records persist together
or
no completed Process is published
```

Optional later compression or archive operations remain outside the immediate transaction.

---

## 29. Implementation Guidance

The first implementation should separate:

```text
Pydantic field validators
cross-model validators
reference resolver
lineage validator
result consistency validator
transaction coordinator
```

Do not place every rule in one large endpoint function.

Recommended conceptual services:

```text
RequestSchemaValidator
ReferenceResolver
LineageValidator
RuntimeResultValidator
CurrentScopeGuard
IdempotencyGuard
```

These services validate or guard execution.

They do not own OperatorResponse selection.

---

## 30. Acceptance Criteria

Priority E-5 is complete when:

```text
1. Field validation and relational validation are separated.
2. Explicit references resolve to compatible record types.
3. Embedded and referenced duplicate identities cannot conflict.
4. Re-Slice requires explicit source and parent lineage.
5. Boundary State reclassification preserves prior records.
6. VOID requires an identifiable Boundary relation.
7. ContextEvidence and VoidEvidence do not select responses.
8. Stability, Response, and Continuity remain distinct.
9. Every response type has a consistent continuity result.
10. DEFER creates a separate pending relation.
11. STOP terminates only the current control scope.
12. Current-scope conflicts remain API conflicts.
13. Valid UNKNOWN, VOID, NOT_EVALUABLE, DEFER, JUMP, and STOP outcomes remain valid Runtime results.
14. A result is published only after complete cross-object validation.
```

---

## 31. E-5 Decision

```text
Priority E-5
Status: ACCEPTED
```

The canonical validation boundary is:

```text
validate structure
+
resolve identity
+
validate lineage
+
validate cross-object relations
+
validate execution preconditions
```

without converting Runtime uncertainty or Runtime response outcomes into API validation failures.

The next step is:

```text
Priority E-6
= /loop/step Execution Contract
```
