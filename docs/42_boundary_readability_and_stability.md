# 42. Boundary Readability and Stability

---

## 1. Overview

This document defines the relation between **Boundary Readability** and **Stability** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

The purpose is not to redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Boundary and Boundary State are Slice-derived runtime relations.

They are not new Core elements and they are not intermediate Runtime Stages inserted between Slice and Stability.

This document addresses:

```text
Priority C-4: Boundary Readability and Stability
```

---

## 2. Source Principle

Gyro Logic v3.1 defines Stability as:

```text
Stability is the state in which an opened path becomes readable
as an establishment that can continue.
```

Priority C-1 defines Boundary as:

```text
Boundary is a runtime-readable distinction produced or exposed by Slice
between relations that can be differentiated under the current Structure,
Operator Orientation, and Slice conditions.
```

Priority C-2 defines Boundary State as:

```text
Boundary State is a provisional runtime-readable classification
of how an observed or retained relation stands relative to a Boundary
exposed by the current Slice.
```

Therefore:

```text
Boundary Readability
≠ Stability
```

Boundary Readability concerns whether a distinction has become readable.

Stability concerns whether the opened path, including its readable result, has become an establishment that can continue.

---

## 3. Core Runtime Distinction

The adopted distinction is:

```text
Boundary Readability
= whether a Slice-relative distinction can be read and traced
  under the current Slice conditions

Stability
= whether the opened path and its Slice result can be read
  as an establishment that can continue
```

Japanese:

```text
Boundary Readability
= 現在のSlice条件のもとで、Slice-relativeな区別を
  読み取り、追跡できるか

Stability
= 開かれたPathとそのSlice結果が、継続可能な成立として
  読める状態にあるか
```

Boundary Readability is narrower than Stability.

A Boundary may be readable even when the overall path is not stable.

A path may also be stable without requiring an explicit Boundary record.

---

## 4. Correct Runtime Position

Incorrect:

```text
Structure
→ Slice
→ Boundary
→ Stability
```

Incorrect:

```text
Boundary confidence
→ Stability
```

Incorrect:

```text
Boundary State
→ Operator Response
```

Correct:

```text
Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  distinction formation / exposure
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
Stability reads the opened path and established Slice result
↓
Loop Controller / Operator Response selects the next runtime relation
```

Boundary evidence remains inside the readable result of Slice.

Stability is read from the established Slice result and its runtime relation.

---

## 5. Boundary Readability

Boundary Readability indicates that a distinction has become sufficiently readable to be represented or retained as Boundary evidence.

A readable Boundary should preserve enough information to answer:

```text
What distinction became readable?
Under which Slice did it become readable?
Relative to which Structure and Orientation?
At which resolution and Context?
With what evidence and uncertainty?
```

Candidate readability dimensions include:

```text
identifiability
traceability
distinction clarity
evidence sufficiency
source linkage
context adequacy
resolution adequacy
classification availability
```

These are implementation-level dimensions.

They do not redefine Boundary theoretically.

---

## 6. Boundary Readability Is Not Boundary Certainty

A Boundary may be readable without being certain, final, or complete.

```text
readable
≠ certain
≠ permanent
≠ globally valid
≠ complete
```

Examples:

```text
A Boundary is readable, but its state is Unknown.
A Boundary is readable, but multiple Boundary interpretations coexist.
A Boundary is readable, but evidence confidence is low.
A Boundary is readable, but later Re-Slice may refine it.
```

Therefore:

```text
Boundary readability allows retention and relation.
It does not guarantee final classification.
```

---

## 7. Stability Reads More Than Boundary

Stability must not be reduced to Boundary readability.

A Stability reading may consider:

```text
SliceDone readability
opened path coherence
Difference / Deviation
Boundary evidence
Boundary State evidence
Context
Void references
Trajectory relation
current Runtime Structure
continuability under current conditions
```

But no single field determines Stability automatically.

Incorrect:

```text
if boundary_readable:
    stability = stable
```

Incorrect:

```text
if boundary_state == Normal:
    stability = stable
```

Incorrect:

```text
if boundary_confidence >= threshold:
    stability = stable
```

Safer PoC-level reading:

```text
StabilityEngine reads the whole established Slice result
and determines whether the opened path is readable
as an establishment that can continue.
```

---

## 8. Readable Boundary with Low or Non-Evaluable Stability

A Boundary can be readable while Stability is low, unstable, or not evaluable.

Example:

```text
Boundary:
  readable distinction between supported and unsupported relation

Boundary State:
  Unknown

Difference / Deviation:
  high

Context:
  insufficient

Stability:
  not_evaluable
```

The Boundary remains useful evidence.

It may support later:

```text
Adjust
Re-Slice
Defer
Jump
Stop
```

However, the Boundary does not select those responses.

---

## 9. Stable Path Without Explicit Boundary

Boundary-aware Runtime must not require every SliceDone to contain a Boundary.

```text
Boundary-aware
≠ Boundary-required
```

A Slice may produce a readable established result in which no explicit Boundary distinction is relevant or exposed.

Example:

```text
SliceDone:
  representation: readable
  deviation: bounded
  boundary_refs: []
  context_refs: present

Stability:
  established and continuable
```

Therefore:

```text
Stability does not require Boundary existence by definition.
```

Boundary is optional Slice-derived evidence.

---

## 10. Boundary State and Stability

Boundary State classifies a relation relative to a Boundary.

Stability reads whether the opened path is a continuing establishment.

```text
Boundary State
= provisional relational classification

Stability
= state of continuing establishment
```

The following mappings are invalid:

```text
Normal  = Stable
Non     = Unstable
Un      = Unstable
Unknown = Not Stable
Void    = Stop
```

Boundary States may orient Stability reading, but they are not Stability labels.

Possible examples:

```text
Normal + high deviation
→ Stability may still be low

Unknown + bounded readable path
→ Stability may remain adaptive or evaluable

Non + coherent supported exclusion
→ Stability may be high

Void-related evidence + retained traceability
→ Stability may be not_evaluable while Runtime Continuity remains retainable
```

---

## 11. Boundary Confidence and Stability Value

Boundary confidence and Stability value must remain separate implementation quantities.

```text
boundary_confidence
= confidence that the Boundary distinction or classification is readable

stability_value
= implementation-level reading of whether the opened path is a continuing establishment
```

Recommended rule:

```text
boundary_confidence ≠ stability_value
```

They may be correlated in some implementations, but they must not be treated as interchangeable.

Candidate model:

```python
class BoundaryReadability:
    boundary_id: str
    readable: bool
    confidence: float | None
    evidence_refs: list[str]
    ambiguity_refs: list[str]
    resolution: str | None
    context_ref: str | None
    metadata: dict
```

```python
class StabilityResult:
    stability_id: str
    slice_done_ref: str
    value: float | None
    status: str
    continuable: bool | None
    evidence_refs: list[str]
    boundary_refs_considered: list[str]
    metadata: dict
```

These models are provisional.

---

## 12. Multiple Boundaries and Stability

One SliceDone may contain multiple readable Boundaries.

```text
one SliceDone
→ Boundary_A
→ Boundary_B
→ Boundary_C
```

They may:

```text
coexist
conflict
refine one another
apply to different dimensions
apply at different resolutions
```

Stability must not collapse multiple Boundary records into one unqualified boolean.

The Stability reading should preserve which Boundary evidence was considered and whether unresolved conflicts remain.

Example:

```text
Boundary_A: readable and Normal
Boundary_B: readable and Unknown
Boundary_C: conflicting evidence

Stability:
  adaptive
  continuable: true
  unresolved_boundary_refs: [Boundary_B, Boundary_C]
```

This is an implementation example, not a Gyro Logic definition.

---

## 13. Boundary Change Across Re-Slice

Re-Slice may produce a different Boundary or Boundary State.

```text
Slice_n
→ Boundary_n
→ Stability_n
→ Operator Response = RESLICE
→ Re-Slice operation
→ Boundary_n+1
→ Stability_n+1
```

The new Boundary does not silently overwrite the prior Boundary.

Recommended relations:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
replaces_for_current_scope
```

Stability readings should remain associated with the SliceDone from which they were read.

```text
Stability_n belongs to SliceDone_n
Stability_n+1 belongs to SliceDone_n+1
```

A later Stability result must not retroactively rewrite an earlier Stability result.

---

## 14. Void and Stability

Void requires careful separation.

```text
Void as Boundary State
≠ Void evidence
≠ Stability
≠ Operator Response
```

A Void-related relation may mean that the current Slice cannot sufficiently read or connect a relation.

Possible Stability outcomes include:

```text
not_evaluable
partially_evaluable
adaptive
unstable
```

The exact status is implementation-dependent.

However:

```text
Void does not automatically mean Stability failure.
Void does not automatically cause DEFER, JUMP, or STOP.
```

The Loop Controller selects the response using the full runtime context.

---

## 15. Operator Response Boundary

The responsibility boundary is:

```text
Slice
→ produces readable SliceDone and Boundary evidence

Stability Engine
→ reads whether the opened path is a continuing establishment

Loop Controller / Operator Response
→ selects CONTINUE / ADJUST / RESLICE / JUMP / DEFER / STOP
```

Boundary evidence and StabilityResult are decision inputs.

They are not decision owners.

Incorrect:

```text
Boundary State = Unknown
→ automatic RESLICE
```

Incorrect:

```text
Boundary confidence low
→ automatic DEFER
```

Correct:

```text
Boundary evidence
+ Boundary State
+ StabilityResult
+ Difference / Deviation
+ Context
+ Void evidence
+ Trajectory history
+ Runtime limits
↓
Loop Controller / Operator Response
↓
selected response
```

---

## 16. API Implications

For:

```text
POST /loop/step
```

Boundary readability and Stability should be represented separately.

Example:

```json
{
  "slice_done": {
    "slice_id": "slice-042",
    "boundary_refs": ["boundary-007"],
    "boundary_state_refs": ["boundary-state-011"]
  },
  "boundary_readability": [
    {
      "boundary_id": "boundary-007",
      "readable": true,
      "confidence": 0.81
    }
  ],
  "stability": {
    "value": 0.68,
    "status": "adaptive",
    "continuable": true,
    "boundary_refs_considered": ["boundary-007"]
  },
  "operator_response": {
    "response_type": "ADJUST"
  }
}
```

The API must not imply:

```text
boundary_readable = true
therefore
operator_response = CONTINUE
```

---

## 17. Memory and Trajectory Implications

Memory Runtime should preserve Boundary and Stability evidence separately.

Recommended retained relations:

```text
BoundaryRecord
BoundaryStateRecord
BoundaryReadabilityRecord
SliceDone
StabilityResult
OperatorResponse
Trajectory relation
```

Trajectory Cache should preserve:

```text
which Slice exposed the Boundary
which StabilityResult read the SliceDone
which Operator Response followed
which later Slice refined or contradicted the Boundary
```

Boundary history must not be inferred only from Stability history.

Stability history must not be inferred only from Boundary State history.

---

## 18. Design Constraints

Boundary-aware Stability handling MUST NOT:

```text
insert Boundary as a Core stage
insert Boundary as a mandatory Runtime Stage
equate Boundary readability with Stability
equate Boundary confidence with Stability value
equate Boundary State with Stability status
require every SliceDone to contain a Boundary
automatically select Operator Response from Boundary evidence alone
silently overwrite prior Boundary or Stability records
treat Void as an actor
```

Boundary-aware Stability handling MUST:

```text
preserve Structure → Slice → Stability
keep Boundary and Boundary State Slice-derived
keep Boundary readability and Stability distinct
allow readable Boundary with low or non-evaluable Stability
allow stable SliceDone without explicit Boundary
preserve Boundary and Stability lineage separately
provide both as inputs to Operator Response
```

---

## 19. Key Insight

The central distinction is:

```text
Boundary Readability asks:
What distinction became readable through this Slice?

Stability asks:
Can the opened path and its readable result stand as an establishment that can continue?
```

Japanese:

```text
Boundary Readabilityは、
「このSliceによって、どの区別が読めるようになったか」を扱う。

Stabilityは、
「開かれたPathとその読める結果が、継続可能な成立として立てるか」を扱う。
```

---

## 20. Summary

Boundary Readability and Stability are related but distinct runtime readings.

```text
Boundary Readability
= readability of a Slice-relative distinction

Stability
= readability of the opened path as a continuing establishment
```

Boundary evidence may contribute to Stability reading, but it does not determine Stability by itself.

Boundary State, Boundary confidence, StabilityResult, and Operator Response remain separate responsibilities.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 21. Next

```text
Priority C-5: Boundary-aware Operator Response
```
