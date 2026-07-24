# 62. Priority F — Proof of Concept Plan

---

## 1. Purpose

This document begins **Priority F: Bounded Runtime Proof of Concept** after completion of Priority E.

Priority E established:

```text
API contract
+
canonical models
+
minimal bounded /loop/step implementation
+
contract tests
```

Priority F verifies that the implementation can make the Runtime relation visible through concrete, repeatable scenarios.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The PoC does not redefine the Core.
It demonstrates the bounded Runtime representation of one Process at a time.

---

## 2. Priority F Goal

The PoC must demonstrate:

```text
one explicit LoopStepRequest
→ one bounded Gyro Process
→ one SliceDone
→ one StabilityResult
→ one OperatorResponse
→ one RuntimeContinuityResult
```

It must also make visible:

```text
Boundary evidence
Boundary State classification
Context evidence
Void evidence
Response / Continuity separation
Process identity
lineage preparation
record preservation
```

The target is not production behavior.
The target is a reproducible observation surface for the accepted Priority E contract.

---

## 3. Priority F Scope

```text
F-1  PoC Boundary and Scenario Contract
F-2  Scenario A — Readable Boundary / NORMAL / CONTINUE
F-3  Scenario B — UNKNOWN / Context / RESLICE preparation
F-4  Scenario C — VOID evidence / DEFER
F-5  Scenario D — Conflicting evidence / ADJUST or JUMP
F-6  PoC Runner and Result Artifact Generation
F-7  Trajectory, Memory, and Lineage Observation
F-8  PoC Test Execution through GitHub Actions
F-9  PoC Result Review and Refinement
F-10 Priority F Cross-document Review
```

The first implementation batch covers F-1 through F-7 and prepares F-8.
Actual CI execution status must be confirmed from GitHub Actions after the workflow runs.

---

## 4. PoC Boundary

The PoC uses the existing canonical endpoint:

```text
POST /loop/step
```

It does not create a second execution engine.

The execution boundary remains:

```text
one HTTP request
=
one bounded Gyro Process
```

For `RESLICE`:

```text
Process_n
→ OperatorResponse = RESLICE
→ prepare SliceRequest_{n+1}
→ return result
```

The PoC must not recursively execute the prepared request in the same call.

---

## 5. Scenario Matrix

| Scenario | Boundary State | Stability | Response | Continuity | Main observation |
|---|---|---|---|---|---|
| A | NORMAL | STABLE | CONTINUE | DIRECT_CONNECTION | Direct readable continuation |
| B | UNKNOWN | STABLE or ADAPTIVE | RESLICE | RESLICE_CONNECTION | Context retained as explicit next Slice source |
| C | VOID | VOID_RELATED | DEFER | DEFERRED_PENDING_RELATION | Void evidence remains distinct from DEFER |
| D1 | conflicting evidence | ADAPTIVE | ADJUST | ADJUSTED_CONNECTION | Bounded continuous modification |
| D2 | conflicting evidence | UNSTABLE or ADAPTIVE | JUMP | JUMP_RECONNECTION | Non-continuous reconnection |

These mappings are controlled PoC policy choices.
They are not universal Gyro Logic definitions.

---

## 6. Scenario Assertions

### Scenario A

```text
BoundaryEvidence exists
BoundaryStateRecord.state_type = NORMAL
StabilityResult.status = STABLE
OperatorResponse.response_type = CONTINUE
RuntimeContinuityType = DIRECT_CONNECTION
```

### Scenario B

```text
ContextEvidence exists
BoundaryStateRecord.state_type = UNKNOWN
OperatorResponse.response_type = RESLICE
next_request exists
next_request.mode = RESLICE
next_request.source_ref = explicit ContextEvidence identity
no recursive Process is created
```

### Scenario C

```text
identifiable BoundaryEvidence exists
BoundaryStateRecord.state_type = VOID
VoidEvidence exists
StabilityResult.status = VOID_RELATED
OperatorResponse.response_type = DEFER
RuntimeContinuityType = DEFERRED_PENDING_RELATION
VoidEvidence contains no deferred/resolved control flags
```

### Scenario D

```text
conflicting evidence is retained
OperatorResponse is explicitly selected by bounded policy
Response is ADJUST or JUMP
Continuity type matches the selected response
prior evidence is not deleted
```

---

## 7. Artifact Layout

```text
poc/
  scenarios/
    scenario_a_normal_continue.json
    scenario_b_unknown_reslice.json
    scenario_c_void_defer.json
    scenario_d_adjust.json
    scenario_d_jump.json
  run_poc.py
  README.md
  results/
    .gitkeep
```

The runner writes timestamp-independent scenario result files when an output directory is specified.
Generated IDs and timestamps remain Runtime artifacts and may differ between runs.

---

## 8. Observation Model

Each result artifact should expose a concise observation summary:

```text
scenario_id
process_id
slice_id
Boundary State values
Stability status and value
OperatorResponse
RuntimeContinuityType
evidence counts
next_request summary
created_record_refs
```

The complete `LoopStepResult` should also be preserved.

The summary is a view.
It does not replace the canonical Runtime objects.

---

## 9. Success Criteria

Priority F PoC is successful when:

```text
all scenario requests pass canonical validation
all scenarios return complete LoopStepResult objects
Response / Continuity mappings are correct
VOID remains distinct from DEFER
RESLICE prepares but does not recursively execute
records are retrievable by explicit identity
scenario runner produces repeatable JSON artifacts
contract and scenario tests pass in CI
```

---

## 10. Non-goals

Priority F does not yet provide:

```text
production policy learning
persistent database
multi-node execution
background autonomous loops
real operating-system scheduling
GyroAuth verdicts
UI dashboard
performance benchmarks
security hardening
```

These may be considered only after the bounded PoC is reviewed.

---

## 11. Initial Decision

```text
Priority F status:
STARTED

PoC contract:
ACCEPTED FOR IMPLEMENTATION
```
