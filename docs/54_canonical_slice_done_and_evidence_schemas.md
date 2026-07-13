# 54. Canonical SliceDone and Evidence Schemas

---

## 1. Purpose

This document defines **Priority E-3: Canonical SliceDone and Evidence Schemas** for the GyroOS API.

The purpose is to fix the response-side contract for the completed Slice result and the Boundary-aware evidence objects produced or retained during one bounded Gyro Process.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

This document defines Runtime serialization.
It does not add new Core elements.

---

## 2. E-3 Decision Summary

The canonical completed Slice object is:

```text
SliceDone
├─ representation
├─ deviation
├─ readability
├─ BoundaryEvidence
├─ BoundaryStateRecord
├─ ContextEvidence
├─ VoidEvidence
├─ explicit record references
├─ Slice execution lineage
└─ metadata
```

The following objects remain distinct:

```text
BoundaryEvidence
≠ BoundaryStateRecord
≠ ContextEvidence
≠ VoidEvidence
```

They also remain distinct from:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

---

## 3. Canonical SliceDone Shape

```python
class SliceDone:
    slice_id: str
    process_id: str
    structure_ref: str

    representation: dict
    deviation: dict
    readability: SliceReadability

    boundary_evidence: list[BoundaryEvidence]
    boundary_state_records: list[BoundaryStateRecord]
    context_evidence: list[ContextEvidence]
    void_evidence: list[VoidEvidence]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str
    slice_policy_ref: str
    trajectory_ref: str | None

    parent_process_ref: str | None
    parent_slice_ref: str | None
    source_type: str
    source_ref: str

    created_at: str
    metadata: dict
```

`SliceDone` is the readable established result of one completed Slice execution.

It must not contain:

```text
OperatorResponse selection
RuntimeContinuity disposition
application verdict
HTTP status
memory compression action
```

---

## 4. Required and Optional SliceDone Fields

### Required

```text
slice_id
process_id
structure_ref
representation
deviation
readability
boundary_evidence
boundary_state_records
context_evidence
void_evidence
boundary_refs
boundary_state_refs
context_refs
void_refs
orientation_ref
slice_policy_ref
source_type
source_ref
created_at
```

### Optional and nullable

```text
trajectory_ref
parent_process_ref
parent_slice_ref
metadata
```

Collection fields must be present and default to empty lists.

This avoids ambiguity between:

```text
field omitted because not evaluated
```

and:

```text
field evaluated and no object was produced
```

If an implementation needs to distinguish those cases, it must use explicit evaluation metadata rather than field omission.

---

## 5. Identity Ownership

The following IDs are server-owned Runtime artifact identities:

```text
slice_id
boundary_evidence_id
boundary_state_record_id
context_evidence_id
void_evidence_id
```

Imported retained records may preserve external IDs only when provenance and uniqueness are validated.

Within one `LoopStepResult`, every embedded identity must be unique.

An embedded object and an external reference must not claim the same identity with conflicting content.

---

## 6. SliceReadability

Canonical model:

```python
class SliceReadability:
    representation_readable: bool
    deviation_readable: bool
    boundary_readability: float | None
    target_relation_readability: float | None
    unreadable_aspects: list[str]
    reason: str | None
    evidence_refs: list[str]
    metadata: dict
```

The API must keep separate:

```text
boundary_readability
≠ target_relation_readability
≠ boundary_state_confidence
≠ stability
≠ response_confidence
```

This separation is required for safe Void classification.

---

## 7. BoundaryEvidence

Canonical model:

```python
class BoundaryEvidence:
    boundary_evidence_id: str
    slice_id: str
    process_id: str

    relation_ref: str
    distinction_type: str
    side_a_ref: str | None
    side_b_ref: str | None

    boundary_readability: float
    readable_features: dict
    unreadable_features: list[str]

    source_evidence_refs: list[str]
    derived_from_refs: list[str]
    conflicts_with_refs: list[str]
    coexists_with_refs: list[str]

    created_at: str
    metadata: dict
```

### Meaning

```text
BoundaryEvidence
= evidence that a distinction or relation Boundary became readable through the current Slice
```

BoundaryEvidence is not:

```text
a fixed global line
a new Runtime Stage
a Boundary State classification
an Operator Response trigger
```

### Rules

```text
boundary_readability MUST be within 0.0 to 1.0
relation_ref MUST be non-empty
source_evidence_refs MUST contain unique non-empty refs
```

A Slice may produce zero, one, or multiple BoundaryEvidence objects.

```text
Boundary-aware
≠ Boundary-required
```

---

## 8. BoundaryStateRecord

Canonical model:

```python
class BoundaryStateRecord:
    boundary_state_record_id: str
    slice_id: str
    process_id: str

    boundary_ref: str
    relation_ref: str
    state_type: BoundaryStateType
    boundary_state_confidence: float
    classification_reason: str

    evidence_refs: list[str]

    refined_from_refs: list[str]
    reclassified_from_refs: list[str]
    conflicts_with_refs: list[str]
    coexists_with_refs: list[str]
    supersedes_for_current_scope_refs: list[str]
    reopened_from_refs: list[str]
    invalidated_by_evidence_refs: list[str]
    unreadable_under_refs: list[str]

    created_at: str
    metadata: dict
```

Canonical initial vocabulary:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

This vocabulary is an initial controlled Runtime vocabulary.
It is not a permanently closed theoretical enum.

### Boundary State rules

```text
boundary_ref MUST resolve to BoundaryEvidence or a retained Boundary record
boundary_state_confidence MUST be within 0.0 to 1.0
classification_reason MUST be non-empty
```

A later classification must not silently overwrite an earlier record.

Use lineage such as:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
supersedes_for_current_scope
```

`supersedes_for_current_scope` does not mean universal deletion or invalidation.

---

## 9. VOID Boundary State Rule

A `VOID` Boundary State requires both:

```text
1. the relevant Boundary relation is identifiable
2. the target relation is not sufficiently readable or connectable relative to that Boundary
```

Therefore:

```text
boundary_readability exists
+
target relation unreadable or unconnectable
→ VOID may be classifiable
```

But:

```text
Boundary distinction itself unreadable
≠ automatic VOID
```

When the Boundary itself is unreadable, retain:

```text
unclassified Boundary evidence
or
unreadable distinction evidence
```

without forcing a `VOID` state.

---

## 10. ContextEvidence

Canonical model:

```python
class ContextEvidence:
    context_evidence_id: str
    slice_id: str
    process_id: str

    relation_ref: str
    source_type: ContextSourceType
    content: dict

    context_readability: float | None
    context_confidence: float
    inferability: float | None

    source_evidence_refs: list[str]
    parent_context_refs: list[str]
    trajectory_refs: list[str]

    created_at: str
    metadata: dict
```

Canonical initial source types:

```text
RETAINED
OBSERVED_SURROUNDING
INFERRED
TRAJECTORY_RECONSTRUCTED
POLICY_SUPPLIED
ENVIRONMENT_SUPPLIED
```

### Meaning

```text
ContextEvidence
= retained, observed, or inferred evidence about a surrounding relation not fully represented in the current Slice result
```

ContextEvidence is not:

```text
BoundaryEvidence
Runtime Structure itself
an automatic Re-Slice request
an Operator Response
```

### Rules

```text
context_confidence MUST be within 0.0 to 1.0
context_readability, when present, MUST be within 0.0 to 1.0
inferability, when present, MUST be within 0.0 to 1.0
```

The existence of ContextEvidence does not select `RESLICE`.

---

## 11. VoidEvidence

Canonical model:

```python
class VoidEvidence:
    void_evidence_id: str
    slice_id: str
    process_id: str

    boundary_ref: str
    relation_ref: str
    target_ref: str | None

    reason: str
    target_relation_readability: float | None
    connectability: float | None

    supporting_evidence_refs: list[str]
    conflicting_evidence_refs: list[str]
    retained_for_future_refs: list[str]

    created_at: str
    metadata: dict
```

### Meaning

```text
VoidEvidence
= retained evidence supporting unreadability or unconnectability of a target relation relative to an identifiable Boundary
```

VoidEvidence is not:

```text
Void as actor
VOID response
DEFER response
DeferredRelationRecord
resolved or deferred lifecycle state
```

The following fields are prohibited:

```text
deferred
resolved
should_defer
should_jump
should_stop
```

### Rules

```text
boundary_ref MUST be non-empty and resolvable
relation_ref MUST be non-empty
reason MUST be non-empty
```

If `target_relation_readability` or `connectability` is present, it must be within `0.0` to `1.0`.

The existence of VoidEvidence does not select `DEFER`, `JUMP`, or `STOP`.

---

## 12. Embedded Objects and References

The first API permits both:

```text
embedded evidence objects
+
explicit external references
```

Example:

```text
boundary_evidence
= objects produced directly in the current step

boundary_refs
= retained Boundary records or separately persisted current-step records
```

### Identity rule

If an identity appears both embedded and referenced:

```text
embedded object identity
=
referenced retained identity
```

then the resolved content must be semantically identical.

Conflicting duplicate identity is invalid.

### No implicit latest-object rule

The API must not resolve:

```text
latest Boundary
latest Context
latest Void
latest SliceDone
```

without an explicit reference or documented current-scope reference.

---

## 13. Lineage and Provenance

Every evidence object must be traceable to:

```text
process_id
slice_id
source relation or evidence refs
created_at
```

When evidence is derived from a prior Process, preserve:

```text
parent record refs
trajectory refs
reclassification refs
conflict refs
```

The API must preserve historical traceability and current-scope selection separately.

```text
current-scope selection
≠ deletion of prior evidence
```

---

## 14. Canonical JSON Example

```json
{
  "slice_id": "slice_001",
  "process_id": "process_001",
  "structure_ref": "structure_001",
  "representation": {
    "result": "candidate relation"
  },
  "deviation": {
    "value": 0.22
  },
  "readability": {
    "representation_readable": true,
    "deviation_readable": true,
    "boundary_readability": 0.88,
    "target_relation_readability": 0.31,
    "unreadable_aspects": ["target_connection"],
    "reason": "boundary is readable but target connection remains insufficient",
    "evidence_refs": ["boundary_evidence_001"],
    "metadata": {}
  },
  "boundary_evidence": [
    {
      "boundary_evidence_id": "boundary_evidence_001",
      "slice_id": "slice_001",
      "process_id": "process_001",
      "relation_ref": "relation_001",
      "distinction_type": "RELATIONAL",
      "side_a_ref": "side_a_001",
      "side_b_ref": "side_b_001",
      "boundary_readability": 0.88,
      "readable_features": {},
      "unreadable_features": [],
      "source_evidence_refs": [],
      "derived_from_refs": [],
      "conflicts_with_refs": [],
      "coexists_with_refs": [],
      "created_at": "2026-07-13T00:00:00Z",
      "metadata": {}
    }
  ],
  "boundary_state_records": [
    {
      "boundary_state_record_id": "boundary_state_001",
      "slice_id": "slice_001",
      "process_id": "process_001",
      "boundary_ref": "boundary_evidence_001",
      "relation_ref": "relation_001",
      "state_type": "VOID",
      "boundary_state_confidence": 0.76,
      "classification_reason": "target relation is not sufficiently readable relative to the identified boundary",
      "evidence_refs": ["boundary_evidence_001", "void_evidence_001"],
      "refined_from_refs": [],
      "reclassified_from_refs": [],
      "conflicts_with_refs": [],
      "coexists_with_refs": [],
      "supersedes_for_current_scope_refs": [],
      "reopened_from_refs": [],
      "invalidated_by_evidence_refs": [],
      "unreadable_under_refs": [],
      "created_at": "2026-07-13T00:00:00Z",
      "metadata": {}
    }
  ],
  "context_evidence": [],
  "void_evidence": [
    {
      "void_evidence_id": "void_evidence_001",
      "slice_id": "slice_001",
      "process_id": "process_001",
      "boundary_ref": "boundary_evidence_001",
      "relation_ref": "relation_001",
      "target_ref": "target_001",
      "reason": "target relation is not sufficiently connectable",
      "target_relation_readability": 0.31,
      "connectability": 0.25,
      "supporting_evidence_refs": ["boundary_evidence_001"],
      "conflicting_evidence_refs": [],
      "retained_for_future_refs": [],
      "created_at": "2026-07-13T00:00:00Z",
      "metadata": {}
    }
  ],
  "boundary_refs": ["boundary_evidence_001"],
  "boundary_state_refs": ["boundary_state_001"],
  "context_refs": [],
  "void_refs": ["void_evidence_001"],
  "orientation_ref": "orientation_001",
  "slice_policy_ref": "slice_policy_001",
  "trajectory_ref": "trajectory_001",
  "parent_process_ref": null,
  "parent_slice_ref": null,
  "source_type": "RUNTIME_STRUCTURE",
  "source_ref": "structure_001",
  "created_at": "2026-07-13T00:00:00Z",
  "metadata": {}
}
```

This example demonstrates schema separation only.

It does not imply:

```text
VOID → DEFER
```

The OperatorResponse is selected later by the Loop Controller using multiple Runtime inputs.

---

## 15. Prohibited Collapses

The API must not collapse:

```text
BoundaryEvidence into BoundaryStateRecord
BoundaryStateRecord into OperatorResponse
ContextEvidence into RESLICE
VoidEvidence into DEFER
boundary_readability into stability
boundary_state_confidence into response_confidence
current-scope selection into historical deletion
```

It must also not use a generic field such as:

```text
context_or_void
boundary_result
runtime_status
```

when that field would erase responsibility distinctions.

---

## 16. Initial Implementation Subset

A first bounded PoC may limit Boundary State values to:

```text
NORMAL
UNKNOWN
VOID
```

It may also implement reduced evidence fields.

However, the reduced implementation must preserve:

```text
separate object identities
separate confidence values
Boundary-relative VOID condition
lineage references
no automatic response mapping
```

A reduced schema must not redefine the canonical contract.

---

## 17. Acceptance Criteria

Priority E-3 is accepted when:

```text
1. SliceDone is separate from StabilityResult, OperatorResponse, and RuntimeContinuityResult.
2. BoundaryEvidence, BoundaryStateRecord, ContextEvidence, and VoidEvidence have distinct schemas.
3. Boundary readability and target relation readability are separate.
4. VOID requires an identifiable Boundary relation.
5. Unreadable Boundary evidence is not automatically classified as VOID.
6. VoidEvidence contains no deferred or resolved control flags.
7. Embedded objects and external refs have a non-conflicting identity rule.
8. Evidence lineage is preserved across Process and Slice boundaries.
9. Boundary State reclassification does not overwrite history.
10. No evidence object directly selects an OperatorResponse.
```

---

## 18. E-3 Decision

```text
Priority E-3
Status: ACCEPTED
```

The next step is:

```text
Priority E-4
= StabilityResult, OperatorResponse, and RuntimeContinuity Schemas
```
