# 17. Context Loop Controller

---

## 1. Overview

This document defines how GyroOS handles a **Context-linked Loop** after the Gyro Logic v3.1 Core Definition refinement and the Priority B / Priority C Runtime alignment.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Context Loop is not a new Core form and does not introduce a second controller.

It is a Runtime pattern in which retained Context evidence is selected as a source for a later Slice.

---

## 2. Core Definition

```text
Context-linked Loop
= a Gyro Loop in which Operator Response selects RESLICE
  and the next SliceRequest references retained Context evidence as its source
```

Short form:

```text
Gyro Processₙ
→ Operator Responseₙ: RESLICE
→ SliceRequest(source_type="context_evidence")
→ Gyro Processₙ₊₁
```

Context does not repeat the Loop by itself.

The Loop Controller selects the response.

The Re-Slice Engine executes the selected request.

---

## 3. Responsibility Separation

```text
ContextEvidence
= Slice-relative surrounding or retained relation evidence

StabilityResult
= whether the opened Path is readable as an establishment that can continue

Loop Controller
= selects OperatorResponse

RESLICE
= Operator Response requesting another Slice

Re-Slice Engine
= executes the selected SliceRequest
```

Therefore:

```text
ContextEvidence
≠ Context Loop Controller
≠ RESLICE
≠ Re-Slice execution
```

No separate theoretical or control owner is introduced by Context-linked behavior.

---

## 4. Runtime Position

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
StabilityResult
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
```

When `RESLICE` is selected with Context source references:

```text
OperatorResponse: RESLICE
↓
SliceRequest(mode="reslice", source_type="context_evidence")
↓
Re-Slice Engine
↓
new Slice
↓
new SliceDone
↓
new StabilityResult
```

---

## 5. Context Candidate Evaluation

The Loop Controller may evaluate whether retained Context evidence is usable as a next Slice source.

Candidate evidence may include:

```text
context_readability
context_confidence
inferability_score
source_type
relation_refs
Boundary relevance
Difference / Deviation relevance
trajectory recurrence
source availability
resolution adequacy
Re-Slice viability
Runtime limits
```

Context availability does not select `RESLICE` automatically.

Incorrect:

```text
Context exists → RESLICE
high Context confidence → RESLICE
```

Correct:

```text
Context evidence
+ StabilityResult
+ Difference / Deviation
+ Boundary evidence
+ Boundary State records
+ Void evidence
+ Trajectory evidence
+ Runtime limits
↓
Loop Controller
↓
OperatorResponse
```

---

## 6. Canonical Response Vocabulary

The canonical Operator Response vocabulary is:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Older names are compatibility aliases only:

```text
RESLICE_CONTEXT
→ RESLICE with Context source references

CHANGE_ORIENTATION
→ ADJUST

DEFER_VOID
→ DEFER with Void-related evidence
```

`Context Loop Decision` is not a separate response type.

It is an explanatory view of an ordinary `OperatorResponse` whose source references may include Context evidence.

---

## 7. SliceRequest for Context-linked Re-Slice

A Context-linked Re-Slice request may be represented as:

```python
class SliceRequest:
    request_id: str
    process_index: int

    mode: str                    # "reslice"
    source_type: str             # "context_evidence"
    source_ref: str

    orientation: OperatorOrientation
    slice_policy_ref: str | None

    parent_process_id: str
    parent_slice_id: str
    trajectory_ref: str | None

    context_refs: list[str]
    boundary_refs: list[str]
    boundary_state_refs: list[str]
    void_refs: list[str]

    metadata: dict
```

The request must preserve which evidence justified the source selection.

---

## 8. State and Traceability

A specialized implementation view may be retained for diagnostics, but it must not become a second controller.

```python
class ContextLoopTrace:
    loop_id: str
    process_index: int

    active_context_source_ref: str | None
    parent_process_id: str | None
    parent_slice_id: str | None

    context_chain: list[str]
    source_chain: list[str]
    reslice_depth: int
    max_reslice_depth: int

    cycle_detected: bool
    limit_evidence_refs: list[str]
    metadata: dict
```

This object records execution lineage.

It does not select the next response.

---

## 9. Loop Controller Inputs

The Loop Controller may consider:

```text
SliceDone readability
StabilityResult
Difference / Deviation
Context evidence and references
context_readability
context_confidence
inferability_score
Boundary evidence
Boundary State records
Void evidence
Trajectory history
source recoverability
Re-Slice viability
reslice_depth
source_chain length
cycle evidence
memory pressure
time / cost / policy limits
current control scope
```

No one field controls the result.

In particular:

```text
high Context confidence ≠ automatic RESLICE
low Context confidence ≠ automatic DEFER
cycle detected ≠ automatic STOP
Void evidence ≠ automatic JUMP
```

These conditions orient the response space and remain inputs to the Loop Controller.

---

## 10. Response Semantics in Context-linked Cases

### CONTINUE

Preserve direct connection through the current established Path without opening another Slice over Context evidence.

### ADJUST

Preserve continuity through bounded modification of Orientation or Slice Policy.

Context evidence may be retained for a later Slice.

### RESLICE

Request another Slice using Context evidence or another retained relation as source.

### JUMP

Request non-continuous reconnection when bounded continuation or Re-Slice is not the selected connection form.

### DEFER

Keep the Context-related source relation pending while preserving future connectability.

### STOP

End the execution connection in the current control scope while preserving evidence and lineage.

STOP is not pending preservation.

---

## 11. Recursion and Runtime Limits

Context-linked Re-Slice must remain bounded.

Candidate limits include:

```text
max_reslice_depth
max_context_chain_length
max_source_chain_length
cycle detection
time budget
cost budget
memory pressure
trajectory branch limit
```

Limit detection produces evidence.

It does not directly select a response.

Correct:

```text
limit evidence
↓
Loop Controller
↓
ADJUST | RESLICE | JUMP | DEFER | STOP
```

Incorrect:

```text
max depth reached → automatic STOP
cycle detected → automatic JUMP
```

---

## 12. Boundary-aware Context Loop

Context evidence may alter which Boundary becomes readable in a later Slice.

```text
ContextEvidence_A
↓ RESLICE selected
Slice_B
↓
Boundary_B becomes readable
```

However:

```text
Context ≠ Boundary
Context confidence ≠ Boundary readability
Boundary State ≠ Operator Response
```

A later Slice may reclassify a prior Boundary State.

The earlier record must remain traceable.

---

## 13. Void Relation

Context-linked execution may encounter Void-related evidence.

GyroOS must distinguish:

```text
Void as Boundary State
VoidEvidence
Void reference
DEFER response
RESLICE response
JUMP response
STOP response
```

Context absence or low Context confidence does not automatically create `VOID`.

A `VOID` Boundary State requires that the relevant Boundary is identifiable while the target relation remains insufficiently readable or connectable relative to it.

---

## 14. API Mapping

`POST /loop/step` remains the primary Runtime endpoint.

Example:

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 9,
  "operator_response": {
    "response_type": "RESLICE",
    "reason": "retained context evidence may open a more readable path",
    "decisive_evidence_refs": ["context_009", "deviation_009"],
    "next_request": {
      "mode": "reslice",
      "source_type": "context_evidence",
      "source_ref": "context_009",
      "parent_process_id": "process_009",
      "parent_slice_id": "slice_009"
    }
  },
  "context_loop_trace": {
    "active_context_source_ref": "context_009",
    "reslice_depth": 1,
    "context_chain": ["context_007", "context_009"],
    "cycle_detected": false
  }
}
```

The trace object is diagnostic.

The `operator_response` remains the decision owner.

---

## 15. Relation to Re-Slice Engine

Correct:

```text
Loop Controller
↓ selects RESLICE
SliceRequest with Context source refs
↓
Re-Slice Engine
↓ executes Slice
new SliceDone
```

Incorrect:

```text
Re-Slice Engine decides to continue the Context Loop
Context evidence starts Re-Slice directly
```

The Re-Slice Engine executes; it does not decide.

---

## 16. Relation to Stability

Stability is one input to Operator Response.

```text
StabilityResult
+ other Runtime evidence
↓
Loop Controller
↓
OperatorResponse
```

Stability does not start or stop a Context-linked Loop directly.

Also:

```text
continuability
≠ CONTINUE response
```

A continuable establishment may still lead to `RESLICE`, `ADJUST`, `DEFER`, `JUMP`, or `STOP` under the current control conditions.

---

## 17. Design Constraints

The Context-linked Loop design MUST NOT:

```text
redefine Structure → Slice → Stability
create a second Loop Controller
create Context as an independent Runtime Stage
auto-trigger from Context existence
auto-trigger from Context confidence
auto-trigger from Stability alone
allow unbounded Re-Slice recursion
treat Void as an actor
collapse Context, Boundary, Void, Stability, and Response
mix GyroAuth application decisions into GyroOS
```

It MUST:

```text
remain an ordinary Gyro Loop pattern
use the canonical Operator Response vocabulary
preserve source and parent linkage
retain Context evidence and lineage
keep Re-Slice bounded
preserve prior SliceDone and Boundary State records
let Loop Controller select the response
let Re-Slice Engine execute only a selected request
```

---

## 18. Key Insight

```text
Context Loop is not another loop.
It is a Gyro Loop whose selected next Slice source is Context evidence.
```

In short:

```text
Context provides a possible source.
Loop Controller selects the connection.
Re-Slice Engine executes the next Slice.
Trajectory preserves how the source changed.
```

---

## 19. Summary

A Context-linked Loop is represented by:

```text
Gyro Processₙ
→ OperatorResponseₙ: RESLICE
→ SliceRequest(source=context_evidence)
→ Re-Slice Engine
→ Gyro Processₙ₊₁
```

It preserves the invariant Core:

```text
Structure
↓
Slice
↓
Stability
```

The next Priority D target is:

```text
docs/21_memory_runtime.md
```