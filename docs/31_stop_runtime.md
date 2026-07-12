# 31. Stop Runtime

---

## Overview

This document defines **Stop** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

Stop is not a theoretical endpoint of Gyro Logic.

The invariant theoretical Core remains:

```text
Structure → Slice → Stability
```

---

## Core Definition

```text
Stop is an Operator Response that ends the current execution connection
within the active control scope without redefining Stability as termination
and without erasing established trajectory evidence.
```

Japanese:

```text
Stopとは、Stabilityを終了とみなすことなく、
成立したTrajectory evidenceを消去せずに、
現在のcontrol scopeにおけるexecution connectionを終了する
Operator Responseである。
```

The phrase `within the active control scope` is essential. Stop does not assert the disappearance of all future connectability.

---

## Stop Is Not the End of the Core

```text
Stability ≠ Stop
Stop ≠ theoretical completion
Stop ≠ final truth
Stop ≠ deletion of Structure
Stop ≠ deletion of Trajectory
```

Stop occurs after runtime evidence becomes available and Operator Response selects that the current execution connection must end.

---

## Stop and Runtime Continuity

Runtime Continuity may preserve established or retained traceable relations beyond active execution.

```text
Operator Response = STOP
→ current execution connection ends within the active control scope
```

However:

```text
current execution connection ends
≠ all continuity evidence disappears
≠ a pending relation is automatically created
```

A stopped runtime may preserve:

```text
SliceDone
StabilityResult
Δ
Boundary / Boundary State
Context
Void reference
Operator Response history
Trajectory references
Memory references
```

---

## Stop and Defer

Stop and Defer must remain distinct.

```text
STOP
= end the current execution connection within the active control scope

DEFER
= retain the current relation as pending for possible future reconnection
```

Stop may preserve evidence and may allow later resume or reconstruction metadata. That does not make Stop a pending relation.

```text
preserved evidence
≠ pending relation
```

A later runtime may use retained Stop evidence as input to Continue, Re-Slice, Jump, or another Process. That later action is separate from Stop itself.

---

## Stop as Operator Response

Correct relation:

```text
SliceDone / retained runtime evidence
→ Stability or not-evaluable result
→ Loop Controller / Operator Response
→ STOP
```

Incorrect relations:

```text
low Stability → automatic Stop
Void → automatic Stop
Boundary State → automatic Stop
Gyro-OOM pressure → direct Stop
```

These may orient the response space, but the Loop Controller owns the decision.

---

## Stop Conditions

Possible implementation-level conditions include:

```text
continuation is no longer permitted
required resources are unavailable
runtime safety boundary is reached
bounded execution limit is reached
external cancellation is requested
current trajectory is intentionally closed
current control scope is complete
```

These are not Gyro Logic definitions.

---

## Stop Types

### Controlled Stop

The current execution ends after required runtime state is preserved.

### External Stop

The current execution ends because an external operator or system requests cancellation.

### Bounded Stop

The current execution ends because an implementation limit has been reached.

Examples:

```text
max_process_steps
max_reslice_depth
time budget
cost budget
memory safety threshold
```

### Protective Stop

The current execution ends because further execution would violate a runtime safety or consistency condition.

### Trajectory Closure

The active trajectory branch is marked as closed while its records remain readable.

These are implementation classifications, not new Gyro Logic concepts.

---

## Relation to Other Responses

```text
CONTINUE
= connect now through the current established path

ADJUST
= connect now with bounded continuous modification

RESLICE
= request a new Slice over a retained source

JUMP
= request a non-continuous reconstruction

DEFER
= retain the current relation as pending

STOP
= end the current execution connection in the active control scope
```

Stop does not itself prepare a new path. Jump and Re-Slice do.

---

## Stop and Void

Void does not stop the runtime by itself.

```text
Void ≠ Stop
```

Possible responses to Void include:

```text
DEFER_VOID
RESLICE
JUMP
STOP
VOID_HOLD
```

Stop is only one possible response.

---

## Memory Runtime and Trajectory Cache

Before Stop is finalized, required continuity evidence should be preserved.

Recommended retained material:

```text
final SliceDone or retained source reference
final StabilityResult if available
final OperatorResponse
Trajectory summary
Δ summary
Context references
Void references
Stop reason
Stop type
resume or reconstruction metadata
```

Trajectory Cache should record Stop as a readable event.

```python
class StopRecord:
    process_index: int
    stop_type: str
    reason: str
    final_slice_ref: str | None
    final_stability_ref: str | None
    trajectory_id: str
    resumable: bool
    reconstruction_allowed: bool
    pending_relation_created: bool = False
    metadata: dict
```

Recommended invariant:

```text
pending_relation_created is false unless a separate DEFER response is selected.
```

---

## API Implications

A `/loop/step` result may include:

```json
{
  "operator_response": "STOP",
  "continuity_state": "stopped",
  "stop_type": "controlled",
  "reason": "bounded execution completed",
  "trajectory_preserved": true,
  "pending_relation": false,
  "resumable": false,
  "reconstruction_allowed": true
}
```

```text
STOP response ≠ HTTP error by definition
STOP response ≠ runtime failure by definition
```

Stop may be a valid runtime result.

---

## Design Constraints

Stop MUST NOT:

```text
redefine Structure → Slice → Stability
treat Stability as termination
automatically follow low Stability
be triggered directly by Void or Boundary State
erase trajectory evidence
silently delete Δ, Context, or Void
be treated as Defer
create a pending relation implicitly
be treated as authentication failure
```

Stop MUST:

```text
be selected through Operator Response
end the active control-scope execution connection clearly
preserve required established evidence
record why execution stopped
state whether later resume or reconstruction is possible
remain an implementation-level runtime response
```

---

## Key Insight

```text
Stop ends the current execution connection,
not established meaning and not all future connectability.
```

Stop preserves evidence. Defer preserves a pending relation. The two responsibilities must not be collapsed.

---

## Refinement Record

This document incorporates the Priority B refinement pass defined in:

```text
docs/35_priority_b_runtime_continuity_review.md
docs/37_priority_b_refinement_pass.md
```
