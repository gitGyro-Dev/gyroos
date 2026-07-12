# 39. Boundary Runtime Definition

---

## 1. Purpose

This document defines **Boundary** in the GyroOS runtime after the Gyro Logic v3.1 refinement.

The purpose is not to redefine Gyro Logic.

The purpose is to establish a precise runtime mapping for Boundary before defining Boundary State, Boundary-aware Stability, Boundary-aware Operator Response, API objects, or PoC behavior.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Boundary is not added to this Core.

This document addresses:

```text
Priority C-1: Boundary Runtime Definition
```

---

## 2. Source Principle

The Gyro Logic v3.1 reading adopted by GyroOS is:

```text
Boundary is a Slice-relative distinction that has become readable through Slice.
```

Japanese:

```text
Boundaryとは、Sliceを通じて読めるようになった、Slice-relativeな区別である。
```

This means that Boundary is not assumed to exist as a universally fixed line before Slice.

A Boundary becomes readable under a particular relation among:

```text
Structure
Operator Orientation
Slice conditions
Context
resolution
selected dimensions
```

Therefore:

```text
Boundary is relative to the Slice through which it becomes readable.
```

---

## 3. GyroOS Runtime Definition

```text
Boundary is a runtime-readable distinction produced or exposed by Slice
between relations that can be differentiated under the current Structure,
Operator Orientation, and Slice conditions.
```

Japanese:

```text
Boundaryとは、現在のStructure・Operator Orientation・Slice条件のもとで、
関係を区別可能にするものとしてSliceによって生成または顕在化され、
Runtime上で読めるようになった区別である。
```

A shorter runtime reading is:

```text
Boundary = Slice-readable distinction.
```

This definition is subordinate to Gyro Logic v3.1.

It is an implementation mapping, not a replacement theoretical definition.

---

## 4. Boundary Is Not a Fixed Line

Boundary must not be reduced to a static geometric line or pre-existing partition.

```text
Boundary ≠ universally fixed line
Boundary ≠ immutable border
Boundary ≠ preloaded classification table
Boundary ≠ hard-coded threshold by definition
Boundary ≠ external policy decision
```

A fixed threshold, access rule, geometric region, or schema boundary may be used as runtime material.

However, such material becomes a GyroOS Boundary only when it participates in a Slice-relative readable distinction.

Example:

```text
configured threshold
≠ Boundary by itself

configured threshold
+ current Structure
+ Slice conditions
↓
readable distinction
= Boundary representation
```

---

## 5. Boundary Is Slice-relative

Boundary is not independent from Slice.

A safe relation is:

```text
Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  distinction formation / exposure
  slice-done
}
↓
Boundary becomes readable in the Slice result
```

The same Structure may produce different readable Boundaries under different Slice conditions.

```text
Structure S
+ Orientation O1
+ Slice Policy P1
→ Boundary B1

Structure S
+ Orientation O2
+ Slice Policy P2
→ Boundary B2
```

This does not imply that Boundary is arbitrary.

The distinction must remain traceable to the Structure, Orientation, Slice conditions, and resulting evidence through which it became readable.

---

## 6. Boundary Is Not a New Runtime Stage

Incorrect:

```text
Structure
→ Slice
→ Boundary
→ Stability
```

This representation risks turning Boundary into a fourth Core element or mandatory stage.

Safer representation:

```text
Structure
↓
Slice {
  Operator Orientation
  → slice-ing
  → slice-done {
       representation
       deviation
       boundary evidence if readable
       context if readable
       void evidence if retained
     }
}
↓
Stability
```

Boundary is a readable relation within or from the Slice result.

It is not an independent theoretical stage between Slice and Stability.

---

## 7. Boundary Formation and Boundary Exposure

GyroOS should allow two implementation readings without collapsing them.

### 7.1 Boundary Formation

```text
Slice establishes a distinction that was not previously available as a readable runtime relation.
```

Example:

```text
continuous observations
↓ Slice
normal range / outside range becomes readable
```

### 7.2 Boundary Exposure

```text
Slice makes an already retained or latent distinction readable under the current conditions.
```

Example:

```text
retained policy or prior trajectory distinction
↓ current Slice
relevant Boundary becomes readable again
```

Both may be represented by Boundary evidence.

GyroOS must not require an unsupported metaphysical claim about whether every Boundary was created or merely discovered.

The runtime requirement is:

```text
The distinction became readable through the current Slice.
```

---

## 8. Boundary and Difference / Deviation

Boundary and Difference are related but not identical.

```text
Difference / Deviation
= measurable or readable separation, mismatch, or displacement within the Slice result

Boundary
= distinction through which relations become differentiable under the current Slice
```

Therefore:

```text
Δ may support Boundary readability.
Boundary may organize the meaning of Δ.
Boundary ≠ Δ.
```

A large Δ does not automatically create a Boundary.

A small Δ does not automatically eliminate a Boundary.

Example:

```text
Δ = 0.02
```

may still be Boundary-relevant if the active Slice distinguishes a critical transition at that scale.

Likewise:

```text
Δ = 0.80
```

may remain an undifferentiated deviation if the current Slice cannot form a readable distinction.

---

## 9. Boundary and Context

Context may affect which Boundary becomes readable.

```text
same observed relation
+ Context A
→ Boundary readable as B1

same observed relation
+ Context B
→ Boundary readable as B2
```

However:

```text
Context ≠ Boundary
```

Context provides surrounding Structure or relation material.

Boundary is the Slice-relative distinction that becomes readable through that material.

Context existence alone does not create Boundary.

---

## 10. Boundary and Operator Orientation

Operator Orientation is an internal directional condition of Slice.

Therefore, Orientation influences:

```text
what is distinguished
which dimensions are selected
what resolution is used
what relation is treated as relevant
which latent distinction may become readable
```

A safe runtime relation is:

```text
Operator Orientation
↓ represented by Slice Policy
Slice execution
↓
Boundary evidence
```

But:

```text
Operator Orientation ≠ Boundary
Slice Policy ≠ Boundary
```

They orient Boundary formation or exposure.

They do not replace the Boundary itself.

---

## 11. Boundary and SliceDone

Boundary may be represented in `SliceDone` when it has become sufficiently readable.

Candidate object:

```python
class BoundaryEvidence:
    boundary_id: str
    source_slice_id: str
    source_process_id: str

    distinction_type: str
    relation_a_ref: str | None
    relation_b_ref: str | None

    orientation_ref: str | None
    slice_policy_ref: str | None
    context_refs: list[str]

    readability: float | None
    resolution: str | None
    evidence_refs: list[str]

    provisional: bool
    metadata: dict
```

Candidate `SliceDone` relation:

```python
class SliceDone:
    slice_id: str
    representation: dict
    deviation: dict

    boundary_evidence: list[BoundaryEvidence]
    context_refs: list[str]
    void_refs: list[str]

    metadata: dict
```

These models are provisional.

They must not be treated as canonical API definitions yet.

Important:

```text
BoundaryEvidence stored in SliceDone
≠ Boundary is merely a data field
```

The field is only an implementation representation of a Slice-relative readable distinction.

---

## 12. Boundary Readability

Boundary may be:

```text
readable
partially readable
provisional
conflicting
not readable under the current Slice
```

Boundary readability should not be reduced to a single universal threshold.

Candidate runtime evidence may include:

```text
relation contrast
Difference / Deviation pattern
Context support
trajectory recurrence
resolution adequacy
consistency across observations
Slice Policy constraints
```

The exact policy is implementation-dependent.

The conceptual invariant is:

```text
Boundary must remain traceable to the Slice through which it became readable.
```

---

## 13. Boundary and Stability

Boundary does not decide Stability.

Stability does not create Boundary by itself.

The safe relation is:

```text
Slice
↓
SliceDone with readable Boundary evidence if available
↓
Stability reads whether the opened path is readable as an establishment that can continue
```

Boundary may affect Stability reading because the opened path may depend on whether distinctions are sufficiently readable.

However:

```text
Boundary ≠ Stability
Boundary readability ≠ automatic Stability
Boundary ambiguity ≠ automatic instability
```

Detailed Boundary-aware Stability behavior is reserved for:

```text
Priority C-4: Boundary Readability and Stability
```

---

## 14. Boundary Does Not Select Operator Response

Boundary is not an actor.

Boundary does not select:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Correct relation:

```text
Boundary evidence
+ Boundary State when available
+ Stability
+ Δ
+ Context
+ Trajectory history
+ Runtime limits
↓
Loop Controller / Operator Response
↓
selected response
```

Incorrect:

```text
Boundary → JUMP
Boundary → STOP
Boundary → RESLICE
```

A Boundary may orient the response space.

It does not determine the response automatically.

---

## 15. Boundary and Runtime Continuity

Boundary may affect how Runtime Continuity remains connectable.

Examples:

```text
readable ordinary Boundary
→ current Path may remain directly connectable

provisional Boundary
→ ADJUST, RESLICE, or DEFER may be considered

critical Boundary relation
→ JUMP or STOP may be considered

unreadable retained distinction
→ DEFER or Void-related handling may be considered
```

These are examples only.

The actual response remains an Operator Response decision.

Boundary itself is not a continuity disposition.

---

## 16. Boundary Identity and Versioning

Because Boundary is Slice-relative, GyroOS should preserve version and source relations.

A Boundary must not be silently overwritten when a later Slice produces a different distinction.

Recommended relation:

```text
Boundary B1
├─ source_slice: S1
├─ orientation: O1
├─ resolution: R1
└─ evidence: E1

Boundary B2
├─ source_slice: S2
├─ orientation: O2
├─ resolution: R2
└─ evidence: E2
```

Possible relations between Boundary records may include:

```text
refined_from
supersedes_for_current_context
conflicts_with
coexists_with
resliced_from
trajectory_related_to
```

These are implementation-level lineage relations.

They do not imply that one universal Boundary must replace all previous Boundaries.

---

## 17. Boundary Preservation

Memory Runtime and Trajectory Cache may preserve:

```text
Boundary evidence
source Slice reference
Operator Orientation reference
Slice Policy reference
Context references
Difference / Deviation evidence
readability information
resolution
lineage relations
```

They do not create Boundary.

They preserve enough evidence for:

```text
future Re-Slice
comparison across Trajectory
Boundary refinement
conflict reading
later Operator Response
```

Detailed preservation rules are reserved for:

```text
Priority C-7: Boundary Memory and Trajectory Preservation
```

---

## 18. What Boundary Is Not

Boundary is not:

```text
a new Core element
a mandatory Runtime Stage
a universal fixed line
a controller
an Operator Response
a Stability value
a Difference value
a Context object
a Void response
a GyroAuth access decision
a final classification by definition
```

---

## 19. Design Constraints

Boundary-aware GyroOS MUST NOT:

```text
insert Boundary into Structure → Slice → Stability
assume Boundary exists as a universally fixed line
reduce Boundary to a static threshold
let Boundary select Operator Response directly
collapse Boundary into Difference / Deviation
collapse Boundary into Context
collapse Boundary into Stability
treat Boundary as an application-layer authorization decision
silently overwrite prior Boundary evidence
```

Boundary-aware GyroOS MUST:

```text
treat Boundary as Slice-relative
preserve source Slice traceability
preserve Orientation and Slice-condition references where relevant
allow Boundary formation or exposure through Slice
represent Boundary evidence without redefining the theory
keep Boundary distinct from Boundary State
keep Boundary distinct from Void evidence and Operator Response
preserve lineage across Re-Slice and Trajectory
```

---

## 20. Initial Runtime Mapping

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  ↓
  Slice Policy
  ↓
  slice-ing
  ↓
  distinction becomes readable
  ↓
  slice-done {
    representation
    Difference / Deviation
    Boundary evidence if readable
    Context references if readable
    Void references if retained
  }
}
↓
Stability
↓
Loop Controller / Operator Response
```

The invariant Core remains:

```text
Structure → Slice → Stability
```

Boundary is a Slice-relative readable distinction within this runtime mapping.

---

## 21. Priority C-1 Decision

The following definition is adopted as the current GyroOS working definition:

```text
Boundary is a runtime-readable distinction produced or exposed by Slice
between relations that can be differentiated under the current Structure,
Operator Orientation, and Slice conditions.
```

Japanese:

```text
Boundaryとは、現在のStructure・Operator Orientation・Slice条件のもとで、
関係を区別可能にするものとしてSliceによって生成または顕在化され、
Runtime上で読めるようになった区別である。
```

This definition remains subordinate to Gyro Logic v3.1.

It does not modify the invariant Core.

---

## 22. Next

```text
Priority C-2: Boundary State Runtime Definition
```
