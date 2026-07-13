# 15. Context Runtime

---

## 1. Overview

This document defines **Context** in GyroOS Runtime after the Gyro Logic v3.1 refinement and the Priority B / C alignment.

GyroOS does not redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Context is not a Core element, independent Runtime Stage, controller, or Operator Response.

---

## 2. Runtime Definition

```text
Context is Slice-relative runtime evidence of surrounding, retained,
or inferable relations that remain relevant to the opened Path
without being fully represented in the current Slice result.
```

Japanese:

```text
Contextとは、現在のSlice結果に完全にはrepresentationされていないが、
開かれたPathに関係し続ける周辺的・保持済み・推論可能な関係を示す、
Slice-relativeなRuntime evidenceである。
```

Context may be retained, inferred, reconstructed from Trajectory, supplied by policy or environment, provisional, or conflicting.

No source type defines Context by itself.

---

## 3. Slice-relative Position

Context is relative to:

```text
Runtime Structure
current Slice
Operator Orientation
Slice Policy
resolution
selected dimensions
Trajectory evidence
current control scope
```

The same relation may be Context under one Slice and explicit representation under a later Slice.

```text
Slice_A: relation R is retained as Context
Slice_B: relation R becomes representation
```

The later reading does not erase the earlier record.

Incorrect:

```text
Structure → Slice → Context → Stability
```

Correct:

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
    Boundary evidence
    Boundary State records
    Context evidence / references
    Void evidence / references
  }
}
↓
Stability
↓
Loop Controller / Operator Response
```

Context is Slice-derived or Slice-retained evidence, not an additional stage.

---

## 4. Context-aware SliceDone

Candidate model:

```python
class SliceDone:
    slice_id: str
    process_id: str
    structure_ref: str

    representation: dict
    deviation: dict

    boundary_evidence: list["BoundaryEvidence"]
    boundary_state_records: list["BoundaryStateRecord"]
    context_evidence: list["ContextEvidence"]
    void_evidence: list["VoidEvidence"]

    boundary_refs: list[str]
    boundary_state_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]

    orientation_ref: str
    slice_policy_ref: str
    trajectory_ref: str | None
    metadata: dict
```

The model is provisional.

```text
Context-aware ≠ Context-required
```

A valid SliceDone may contain no Context evidence.

---

## 5. ContextEvidence

```python
class ContextEvidence:
    context_id: str
    source_slice_id: str
    source_process_id: str
    trajectory_ref: str | None

    relation_refs: list[str]
    inferred_structure: dict

    source_type: str
    inference_basis_refs: list[str]

    context_readability: float | None
    context_confidence: float | None
    inferability_score: float | None

    resolution: str | None
    provisional: bool
    metadata: dict
```

Candidate `source_type` values:

```text
retained
observed_surrounding
inferred
trajectory_reconstructed
policy_supplied
environment_supplied
mixed
unknown
```

Source and evidence must remain traceable.

---

## 6. Readability and Confidence

The following values remain separate:

```text
context_readability
context_confidence
inferability_score
boundary_readability
boundary_state_confidence
stability
response_confidence
```

```text
context_readability
= how clearly the surrounding relation can be read and traced

context_confidence
= confidence in the current Context interpretation

inferability_score
= how much further relation may reasonably be inferred

stability
= whether the opened Path is readable as an establishment that can continue
```

Therefore:

```text
high Context confidence ≠ high Stability automatically
low Context confidence ≠ Void automatically
high inferability ≠ RESLICE automatically
```

---

## 7. Relation to Representation and Difference

```text
Representation
= what became explicitly readable in the current Slice result

Context
= surrounding, retained, or inferable relations relevant to that result
  without being fully represented in it
```

```text
Context ≠ Representation
```

Difference / Deviation and Context also remain distinct.

```text
Difference / Deviation
= readable separation, mismatch, or displacement

Context
= relation evidence relevant to interpreting that result
```

Context may explain or qualify Δ, but it does not replace or automatically neutralize Δ.

---

## 8. Relation to Boundary

Context may affect which Boundary becomes readable.

```text
same relation + Context_A → Boundary_A
same relation + Context_B → Boundary_B
```

However:

```text
Context ≠ Boundary
Context ≠ Boundary State
```

Context provides relation material. Boundary is the Slice-relative distinction. Boundary State is the provisional classification relative to that Boundary.

---

## 9. Relation to Void

Context and Void remain distinct.

```text
Context
= surrounding or retained relation is sufficiently readable or inferable
  to be preserved as relevant evidence

Void as Boundary State
= the relevant Boundary is identifiable,
  but the target relation is not sufficiently readable or connectable
```

Also separate:

```text
ContextEvidence
VoidEvidence
Void as Boundary State
DEFER response
```

Incorrect:

```text
missing Context → automatic DEFER
low Context confidence → automatic VOID
Void evidence → automatic JUMP
```

---

## 10. Relation to Stability

Context may contribute evidence to Stability reading.

```text
SliceDone readability
+ Difference / Deviation
+ Boundary evidence
+ Boundary State records
+ Context evidence
+ Void evidence
+ Trajectory evidence
↓
Stability reading
```

But:

```text
Context ≠ Stability
Context confidence ≠ Stability value
Context absence ≠ instability automatically
```

---

## 11. Relation to Operator Response

Context does not select the next Runtime relation.

```text
Context evidence
+ SliceDone
+ StabilityResult
+ Difference / Deviation
+ Boundary / Boundary State evidence
+ Void evidence
+ Trajectory history
+ Runtime limits
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
```

Incorrect:

```text
Context exists → RESLICE
Context conflicts → JUMP
Context missing → STOP
```

Context is evidence, not the response owner.

---

## 12. Context as Re-Slice Source

Context may become a retained source candidate for another Slice.

```python
class ReSliceCandidate:
    candidate_id: str
    source_type: str
    source_ref: str
    source_slice_id: str
    reason: str
    evidence_refs: list[str]
    viability: float | None
    expected_resolution_gain: float | None
    cost_estimate: float | None
    metadata: dict
```

For Context-derived candidates:

```text
source_type = context
```

Correct:

```text
ContextEvidence retained
↓
Loop Controller selects RESLICE
↓
ReSliceEngine executes another Slice
```

Incorrect:

```text
Context exists → Re-Slice automatically starts
```

---

## 13. Memory and Trajectory

Context records must not be silently overwritten.

Recommended relations:

```text
refined_from
reclassified_from
promoted_to_representation
conflicts_with
coexists_with
supersedes_for_current_scope
unreadable_under
```

Memory Runtime preserves evidence and lineage.

Trajectory Cache preserves how Context readability changes across Processes.

Neither selects Operator Response.

---

## 14. API Implications

`POST /loop/step` may return Context separately from Stability and Operator Response.

```json
{
  "slice_done": {
    "representation": {},
    "deviation": {},
    "context_evidence": [
      {
        "context_id": "context_007",
        "source_type": "inferred",
        "context_readability": 0.81,
        "context_confidence": 0.72,
        "inferability_score": 0.68
      }
    ],
    "context_refs": []
  },
  "stability": {
    "value": 0.84,
    "status": "stable"
  },
  "operator_response": {
    "response_type": "CONTINUE",
    "considered_context_refs": ["context_007"]
  }
}
```

The fields remain conceptually separate.

---

## 15. Compatibility Names

Earlier documents may contain:

```text
RESLICE_CONTEXT
CHANGE_ORIENTATION
DEFER_VOID
```

Canonical mappings are:

```text
RESLICE_CONTEXT
→ RESLICE with Context source references

CHANGE_ORIENTATION
→ ADJUST when modification is bounded and continuous

DEFER_VOID
→ DEFER with Void-related evidence references
```

Compatibility names do not create new response categories.

---

## 16. Design Constraints

Context Runtime MUST NOT:

```text
redefine Structure → Slice → Stability
place Context as an independent Runtime Stage
treat Context as Representation, Boundary, Boundary State, Void, or Stability
automatically trigger Re-Slice
make Context the Loop Controller
collapse Context confidence into Stability
mix GyroAuth decisions into GyroOS
```

Context Runtime MUST:

```text
preserve Context as Slice-relative runtime evidence
retain source, resolution, confidence, and lineage
allow Context to become a candidate source for another Slice
keep SliceDone, StabilityResult, and OperatorResponse separate
preserve historical Context records
let Loop Controller select the next Runtime relation
```

---

## 17. Key Insight

```text
Slice makes a Path readable.
Context preserves relevant surrounding relations.
Stability reads the Path.
Operator Response selects the next connection.
Trajectory preserves how Context changed.
```

---

## 18. Summary

Context Runtime preserves surrounding, retained, and inferable relations without changing the Core.

Context remains:

```text
Slice-relative
provisional
traceable
non-controlling
available as evidence for Stability and Operator Response
available as a retained source for a later Slice
```

The next legacy alignment target is:

```text
Priority D-4: docs/16_reslice_engine.md Alignment
```
