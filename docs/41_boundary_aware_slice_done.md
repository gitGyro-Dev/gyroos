# 41. Boundary-aware SliceDone

---

## 1. Overview

This document defines **Boundary-aware SliceDone** in GyroOS after the Gyro Logic v3.1 Core Definition refinement and the Priority C Boundary-aware Runtime assessment.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Boundary-aware SliceDone does not add a new Core element or Runtime Stage.

It clarifies how the readable result of Slice may preserve Boundary-related evidence without collapsing Boundary, Boundary State, Stability, or Operator Response into one object.

This document addresses:

```text
Priority C-3: Boundary-aware SliceDone
```

---

## 2. Source Principles

Gyro Logic v3.1 defines:

```text
Structure
= the mode in which something can be established

Slice
= the process by which a path is opened through Structure toward an establishment

Stability
= the state in which the opened path becomes readable as an establishment that can continue
```

Priority C-1 defines Boundary as:

```text
Boundary
= a runtime-readable distinction produced or exposed by Slice
```

Priority C-2 defines Boundary State as:

```text
Boundary State
= a provisional runtime-readable classification of how a relation stands relative to a Boundary
```

Therefore, SliceDone may preserve Boundary and Boundary State evidence, but SliceDone is not identical to either concept.

---

## 3. Core Definition

```text
Boundary-aware SliceDone is the readable established result of Slice that preserves the representation, Difference / Deviation, and any Boundary-related evidence made readable under the current Structure, Operator Orientation, and Slice conditions.
```

Japanese:

```text
Boundary-aware SliceDoneとは、
現在のStructure・Operator Orientation・Slice条件のもとでSliceが読めるようにした、
representation・Difference / Deviation・Boundary関連evidenceを保持する、
読める成立済みSlice結果である。
```

A shorter runtime reading is:

```text
Boundary-aware SliceDone
= readable Slice result with traceable Boundary evidence
```

---

## 4. SliceDone Is a Result Container, Not a Decision

SliceDone preserves what became readable through Slice.

It does not decide:

```text
whether the runtime should Continue
whether the Orientation should Adjust
whether another Slice should be opened
whether Jump is required
whether the relation should be Deferred
whether execution should Stop
```

These are Operator Response responsibilities.

Therefore:

```text
SliceDone ≠ Operator Response
Boundary evidence ≠ Operator Response
Boundary State ≠ Operator Response
```

---

## 5. Position in the Core Mapping

Incorrect:

```text
Structure
→ Slice
→ Boundary
→ Boundary State
→ SliceDone
→ Stability
```

This incorrectly inserts Boundary and Boundary State as independent stages.

Correct:

```text
Structure
↓
Slice {
  Operator Orientation
  ↓
  slice-ing
  ↓
  distinctions become readable
  ↓
  slice-done {
    representation
    Difference / Deviation
    Boundary evidence
    Boundary State evidence
    Context references
    Void references
  }
}
↓
Stability
```

Boundary and Boundary State are Slice-derived readable relations preserved in or referenced from SliceDone.

---

## 6. Recommended Conceptual Model

A Boundary-aware SliceDone may be represented conceptually as:

```python
class SliceDone:
    slice_id: str
    process_id: str
    structure_ref: str

    representation: dict
    deviation: dict

    boundary_refs: list[str]
    boundary_state_refs: list[str]

    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str
    slice_policy_ref: str
    trajectory_ref: str | None

    readability: dict
    metadata: dict
```

This model is provisional.

It is an implementation mapping, not a Gyro Logic definition.

---

## 7. Boundary Evidence Model

Boundary evidence should remain traceable to the Slice that made it readable.

A candidate model is:

```python
class BoundaryEvidence:
    boundary_id: str
    source_slice_id: str
    source_process_id: str

    distinction_type: str
    relation_a_ref: str | None
    relation_b_ref: str | None

    evidence_refs: list[str]
    orientation_ref: str
    slice_policy_ref: str
    context_refs: list[str]

    resolution: str | None
    confidence: float | None
    metadata: dict
```

Important:

```text
confidence
≠ Stability
```

Confidence may describe how strongly a Boundary distinction is supported under the current Slice.

Stability reads whether the opened path has become a continuing establishment.

---

## 8. Boundary State Evidence Model

Boundary State should reference the Boundary relative to which the classification was made.

A candidate model is:

```python
class BoundaryStateEvidence:
    boundary_state_id: str
    boundary_id: str
    source_slice_id: str

    state_type: str
    subject_ref: str | None

    evidence_refs: list[str]
    provisional: bool
    confidence: float | None

    previous_state_ref: str | None
    metadata: dict
```

Candidate `state_type` values:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

These values are provisional Runtime classifications.

They are not Operator Responses.

---

## 9. Boundary Is Optional in SliceDone

Not every Slice must expose a Boundary.

A valid SliceDone may contain:

```text
representation
Difference / Deviation
no readable Boundary
```

Therefore:

```text
Boundary-aware
≠ Boundary-required
```

Boundary-aware means that the runtime can preserve Boundary evidence when Slice makes it readable.

It does not mean that every Slice must produce a Boundary.

---

## 10. Multiple Boundaries

A single Slice may expose more than one distinction.

Example:

```text
SliceDone
├─ Boundary_A
├─ Boundary_B
└─ Boundary_C
```

GyroOS should not assume:

```text
one SliceDone = one Boundary
```

Multiple Boundaries may:

```text
coexist
nest
partially overlap
conflict
use different resolutions
refer to different relation pairs
```

Each Boundary must preserve its own evidence and lineage.

---

## 11. Boundary State Cardinality

A Boundary may have multiple Boundary State observations when different subjects, Contexts, resolutions, or trajectory sections are involved.

Example:

```text
Boundary_A
├─ Subject_1 → Normal
├─ Subject_2 → Non
└─ Subject_3 → Unknown
```

Therefore:

```text
Boundary ≠ single Boundary State
```

Also, the same subject may be reclassified by a later Slice:

```text
BoundaryState_1: Unknown
↓
new Slice / new evidence
↓
BoundaryState_2: Normal
```

The later classification must not silently overwrite the earlier record.

---

## 12. Difference / Deviation and Boundary

Difference / Deviation and Boundary remain distinct.

```text
Difference / Deviation
= readable difference between relations or between Structure and representation

Boundary
= readable distinction through which relations become differentiable
```

A Difference may contribute evidence to a Boundary.

But:

```text
large Δ does not automatically create a Boundary
small Δ does not automatically eliminate a Boundary
Boundary is not a thresholded Δ by definition
```

A Boundary-aware SliceDone may preserve both:

```text
deviation evidence
boundary evidence
```

without collapsing them.

---

## 13. Context and Boundary

Context may support, alter, or limit Boundary readability.

```text
Context
→ may make a distinction readable
→ may refine a Boundary
→ may reveal that an earlier Boundary was provisional
```

However:

```text
Context ≠ Boundary
```

Boundary-aware SliceDone should preserve Context references used in Boundary formation or exposure.

This allows a later Re-Slice to understand under which Context the Boundary became readable.

---

## 14. Void and Boundary-aware SliceDone

Void requires careful separation.

A SliceDone may preserve:

```text
Void as Boundary State evidence
Void-related unreadability evidence
Void reference retained for later handling
```

These are not identical.

Safe distinction:

```text
Void Boundary State
= provisional relation classification relative to a readable Boundary

Void evidence
= evidence that a relation could not be read or connected under current Slice conditions

Void reference
= retained Runtime reference for future Re-Slice, Defer, Jump, or other handling
```

And:

```text
Void ≠ DEFER_VOID
Void ≠ JUMP
Void ≠ STOP
```

Operator Response decides how Void-related evidence is handled.

---

## 15. SliceDone and Stability

SliceDone and Stability remain conceptually distinct.

```text
SliceDone
= readable established result of Slice

Stability
= state in which the opened path becomes readable as an establishment that can continue
```

A Boundary-aware SliceDone provides the evidence substrate from which Stability may be read.

Correct:

```text
Boundary-aware SliceDone
↓
Stability Engine reads the established result
↓
StabilityResult
```

Incorrect:

```text
Boundary State directly determines Stability
Boundary confidence equals Stability
Void automatically means unstable
Normal automatically means stable
```

Boundary-related evidence is one part of the Runtime evidence available to Stability.

---

## 16. SliceDone and Operator Response

After Stability becomes available, Loop Controller / Operator Response may consider:

```text
SliceDone readability
StabilityResult
Difference / Deviation
Boundary evidence
Boundary State evidence
Context
Void references
Trajectory history
Runtime limits
```

Then it may select:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Boundary-aware SliceDone does not select any of these responses by itself.

---

## 17. Traceability and Lineage

Boundary-aware SliceDone must preserve enough information to explain:

```text
which Structure was sliced
which Orientation directed the Slice
which Slice Policy was used
which Context was available
which distinctions became readable
which Boundary States were assigned
which evidence supported them
which resolution was used
which prior Slice or Trajectory section was referenced
```

Recommended relation:

```text
RuntimeStructure
↓
SliceRequest / Slice Policy
↓
Slice
↓
SliceDone
├─ BoundaryEvidence
├─ BoundaryStateEvidence
├─ Context references
└─ Void references
```

---

## 18. Preservation Across Re-Slice

Re-Slice must not silently replace prior Boundary-aware SliceDone records.

Correct:

```text
SliceDone_A
↓ RESLICE selected
SliceDone_B
```

with lineage:

```text
SliceDone_B.parent_slice_ref = SliceDone_A
```

Boundary relations may be recorded as:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
replaces_for_current_scope
```

The prior evidence remains traceable.

---

## 19. Memory Runtime Implications

Memory Runtime should preserve Boundary-aware SliceDone according to bounded retention policy.

Possible retention forms:

```text
full record
summary
vectorized evidence
reference pointer
archived lineage record
```

Resolution decay is allowed when traceability remains.

Silent removal of all evidence required to understand a Boundary relation is not allowed within the active continuity policy.

---

## 20. API Implications

A future `/loop/step` response may represent Boundary-aware SliceDone as:

```json
{
  "slice_done": {
    "slice_id": "slice-001",
    "representation": {},
    "deviation": {},
    "boundaries": [
      {
        "boundary_id": "boundary-001",
        "distinction_type": "relation_separation",
        "evidence_refs": ["evidence-001"]
      }
    ],
    "boundary_states": [
      {
        "boundary_state_id": "boundary-state-001",
        "boundary_id": "boundary-001",
        "state_type": "UNKNOWN",
        "provisional": true
      }
    ],
    "context_refs": [],
    "void_refs": []
  }
}
```

This API shape is provisional.

Priority C-8 will define the canonical API mapping later.

---

## 21. Design Constraints

Boundary-aware SliceDone MUST NOT:

```text
add Boundary as a new Core stage
treat Boundary as a mandatory output of every Slice
collapse Boundary into Difference / Deviation
collapse Boundary State into Boundary
collapse Boundary State into Stability
select Operator Response
turn Void into an actor
overwrite prior Boundary evidence silently
assume one SliceDone has only one Boundary
mix GyroAuth-specific policy into GyroOS
```

Boundary-aware SliceDone MUST:

```text
remain the readable established result of Slice
preserve representation and Difference / Deviation
preserve Boundary evidence when readable
preserve Boundary State evidence when classified
retain Slice-relative provenance
retain Orientation, Policy, Context, and lineage references
remain compatible with Stability reading
remain compatible with Runtime Continuity
support bounded Memory and Trajectory preservation
```

---

## 22. Key Insight

Boundary-aware SliceDone does not decide what a Boundary means for the next action.

It preserves what the current Slice made readable.

In short:

```text
Slice makes distinctions readable.
SliceDone preserves those readable distinctions.
Stability reads continuable establishment.
Operator Response selects the next Runtime relation.
```

Japanese:

```text
Sliceは区別を読めるようにする。
SliceDoneはその読める区別を保持する。
Stabilityは継続可能な成立を読む。
Operator Responseは次のRuntime関係を選ぶ。
```

---

## 23. Priority C-3 Decision

The following definition is adopted as the current GyroOS working definition:

```text
Boundary-aware SliceDone is the readable established result of Slice that preserves the representation, Difference / Deviation, and any Boundary-related evidence made readable under the current Structure, Operator Orientation, and Slice conditions.
```

This definition remains subordinate to Gyro Logic v3.1.

It does not modify the invariant Core.

---

## 24. Next

```text
Priority C-4: Boundary Readability and Stability
```

---

## Priority C-10 Refinement

The recommended naming for directly embedded objects and external references is:

```text
*_evidence
= directly retained evidence objects

*_records
= identified classification records with lineage

*_refs
= references to externally retained records
```

A refined embedded form is:

```python
class SliceDone:
    boundary_evidence: list[BoundaryEvidence]
    boundary_state_records: list[BoundaryStateRecord]
    void_evidence: list[VoidEvidence]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    void_refs: list[str]
```

Implementations may use embedded objects, references, or both, but the naming must reveal which form is being used.

`BoundaryStateRecord` is the preferred name for an identified provisional classification with lineage. `BoundaryStateEvidence` should be reserved for unregistered evidence that has not yet become such a record.

The following values must remain separate:

```text
boundary_readability
boundary_state_confidence
Stability
response_confidence
```

Also:

```text
Boundary not sufficiently readable
≠ automatic VOID Boundary State
```

In that case, `SliceDone` may retain unclassified or unreadable Boundary evidence without forcing a Boundary State classification.
