# 11. Loop Controller

---

## Overview

The Loop Controller is the GyroOS implementation of **Operator Response**.

In Gyro Logic, the core structure is:

```text
Structure → Slice → Stability
```

This structure is timeless at the level of the Gyro Unit.

GyroOS does not redefine this structure.  
Instead, GyroOS implements its temporal execution as:

```text
Structure
→ Operator Orientation
→ slice-ing
→ slice-done
→ Stability
→ Operator Response
→ Next Process
```

The Loop Controller corresponds to the **Operator Response** phase.

It does not produce an answer.  
It does not directly modify Stability.  
It does not replace Structure → Slice → Stability.

It receives the Stability state of a completed slice-done and determines how the next process should proceed.

---

## Position in GyroOS v4.0

```text
Structure
   ↓
Operator Orientation
   ↓
Slice Engine
   ↓
slice-ing
   ↓
slice-done = X + Δ
   ↓
Stability
   ↓
Loop Controller
   ↓
Operator Response
   ↓
Next Process
```

The Loop Controller operates **after Stability**.

It is not part of Slice itself.  
It is not part of Stability itself.  
It is the post-Stability response mechanism.

---

## Core Definitions

### slice-ing

```text
slice-ing = the temporal process in which Slice is being executed
```

slice-ing is time-bearing.

It represents the ongoing execution from an oriented structure toward a completed slice result.

---

### slice-done

```text
slice-done = the completed, timeless result of Slice
```

slice-done is what is passed to Stability.

It may be represented as:

```text
slice-done = X + Δ
```

where:

```text
X = representation produced by Slice
Δ = deviation between Structure and Representation
```

---

### Stability

```text
Stability = state quantity appearing in slice-done
```

Stability is not a controller.

It does not decide the next loop step.  
It is observed, stored, and passed to Operator Response.

---

### Operator Response

```text
Operator Response = the post-Stability reaction of the Operator
```

In GyroOS v4.0, Operator Response is implemented by the Loop Controller.

It may decide:

```text
Continue
Adjust
Stop
Jump
Void handling
```

---

## Responsibilities

### 1. Receive Completed Process State

The Loop Controller receives:

```text
slice-done
Stability
Δ
current Orientation
current Process state
history
```

It only acts after the current slice process has completed.

---

### 2. Implement Operator Response

The Loop Controller determines the next response:

```text
Responseₙ = R(slice-doneₙ, Stabilityₙ, Δₙ, Historyₙ)
```

This response may produce:

```text
Continue
Adjust
Stop
Jump
Void
```

---

### 3. Prepare Next Orientation

Operator Response may update the next Operator Orientation:

```text
Responseₙ → Orientationₙ₊₁
```

Important:

```text
Stability does not directly update Orientation.
Loop Controller receives Stability and produces Response.
Response may then update Orientation.
```

---

### 4. Manage Gyro Process Repetition

The Loop Controller does not define the Gyro Unit.

It manages repetition of Gyro Process:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

This repetition forms the Gyro Loop.

---

### 5. Preserve Process History

The Loop Controller maintains:

```text
Orientation History
slice-done History
Deviation History
Stability History
Response History
Process History
```

These histories are not reduced away.

They are used as context for future Operator Response.

---

### 6. Handle Modes

The Loop Controller may classify the current response state as:

```text
stable
adaptive
divergent
void
jump
stopped
```

These modes are not Stability itself.

They are response modes derived by the controller after observing Stability and related state.

---

## Response Types

### Continue

```text
Continue = proceed to the next Gyro Process without major policy change
```

Used when Stability is sufficient and Δ is within acceptable range.

---

### Adjust

```text
Adjust = modify next Operator Orientation continuously
```

Used when the current process is viable but requires recalibration.

This may involve Update Engine internally.

---

### Jump

```text
Jump = non-continuous reconstruction of Orientation / Slice / Structure mapping
```

Used when continuous adjustment is insufficient.

Important:

```text
Void does not jump.
The Loop Controller selects Jump as Operator Response.
```

---

### Void

```text
Void = response mode when Stability is undefined, too low, or not evaluable
```

Void does not act by itself.

The Loop Controller decides how to respond to Void.

Possible responses:

```text
Reset
Jump
Hold
Terminate externally
Re-orient
```

---

### Stop

```text
Stop = externally or internally marked termination of process repetition
```

GyroOS v4.0 is generally non-terminating, but implementation may support Stop as a control response.

Stop is not the theoretical endpoint of Gyro Logic.  
It is a runtime control option.

---

## Relation to Update Engine

The Update Engine is not the center of GyroOS v4.0.

It is an internal mechanism used by the Loop Controller when the response type is:

```text
Adjust
Jump
Re-orient
```

Correct relation:

```text
Stability
→ Loop Controller / Operator Response
→ Update Engine if needed
→ Orientationₙ₊₁
```

Incorrect relation:

```text
Stability
→ Update Engine
→ Loop Controller
```

The Loop Controller owns the response decision.

---

## Data Model

```python
class LoopState:
    loop_id: str
    current_process_index: int

    current_orientation: OperatorOrientation
    current_mode: str

    orientation_history: list[OperatorOrientation]
    slice_done_history: list[SliceDone]
    deviation_history: list[Deviation]
    stability_history: list[Stability]
    response_history: list[OperatorResponse]

    last_response: OperatorResponse | None
```

```python
class OperatorResponse:
    process_index: int
    response_type: str
    reason: str

    next_orientation: OperatorOrientation | None
    update_decision: UpdateDecision | None

    jump_required: bool
    void_detected: bool
    stop_requested: bool
```

---

## Execution Flow

```text
Raw Structure
   ↓
Operator Orientation
   ↓
slice-ing
   ↓
slice-done = X + Δ
   ↓
Stability
   ↓
Loop Controller
   ↓
Operator Response
   ↓
Next Orientation / Stop / Jump / Void handling
   ↓
Next Gyro Process
```

---

## Runtime Pseudocode

```python
def loop_step(raw_structure, loop_state):
    n = loop_state.current_process_index

    # 1. Orientation
    orientation = loop_state.current_orientation

    # 2. slice-ing
    slice_process = SliceEngine.start(
        structure=raw_structure,
        orientation=orientation,
        process_index=n
    )

    # 3. slice-done
    slice_done = SliceEngine.complete(slice_process)

    # 4. Stability as state quantity
    stability = StabilityEngine.measure(
        slice_done=slice_done,
        history=loop_state.stability_history
    )

    # 5. Operator Response
    response = LoopController.respond(
        slice_done=slice_done,
        stability=stability,
        deviation=slice_done.deviation,
        orientation=orientation,
        history=loop_state
    )

    # 6. Optional update
    if response.response_type in ["adjust", "jump", "reorient"]:
        response.update_decision = UpdateEngine.apply_response(
            response=response,
            current_orientation=orientation
        )

    # 7. Advance or stop
    next_state = LoopController.advance(
        loop_state=loop_state,
        slice_done=slice_done,
        stability=stability,
        response=response
    )

    return next_state
```

---

## API Implications

### Main API

```text
POST /loop/step
```

This API executes one Gyro Process and one Operator Response.

It does not simply run:

```text
observe → evaluate → update
```

Rather, it runs:

```text
orientation
→ slice-ing
→ slice-done
→ stability
→ operator response
→ next process preparation
```

---

### Recommended APIs

```text
POST /loop/step
GET  /loop/state
GET  /loop/history
GET  /response/history
GET  /orientation/current
```

---

## Design Constraints

The Loop Controller MUST NOT:

```text
redefine Structure → Slice → Stability
treat Stability as controller
treat Update Engine as the primary loop owner
collapse slice-ing and slice-done
treat Slice as fixed
remove Δ
treat Void as an actor
mix GyroAuth authentication logic into GyroOS
```

The Loop Controller MUST:

```text
implement Operator Response
act only after Stability is available
preserve Δ
preserve process history
prepare next Orientation
support Continue / Adjust / Stop / Jump / Void handling
manage Gyro Process repetition
```

---

## Key Insight

The Loop Controller is not merely a scheduler.

It is the GyroOS implementation of:

```text
Stability → Operator Response → Next Process
```

It makes Gyro Loop possible without changing the timeless core:

```text
Structure → Slice → Stability
```

---

## Summary

The Loop Controller is the central runtime component of GyroOS v4.0.

Its role is not to compute the correct answer.  
Its role is to implement Operator Response after Stability appears in slice-done.

In short:

```text
Gyro Loop is not controlled by Stability directly.
Gyro Loop is continued, adjusted, stopped, or reconstructed by Operator Response.
```

---

## Next

docs/12_update_engine.md
