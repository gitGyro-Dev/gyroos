# 27. Claude PoC Implementation Prompt

---

## Purpose

This document is a prompt for implementing the first bounded GyroOS PoC using Claude.

The goal is not to build a real OS.

The goal is to implement the smallest bounded runtime demonstration of GyroOS.

Core target:

```text
Structure
→ Operator Orientation
→ slice-ing
→ SliceDone
→ StabilityResult
→ LoopController / OperatorResponse
→ Next Process
```

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

---

# Claude Prompt

You are an implementation AI for GyroOS v4/vNext PoC.

Your task is to implement a minimal, bounded runtime demonstration of GyroOS.

Do not redesign the theory.
Do not expand the scope.
Do not implement a real OS.

---

## 0. Non-negotiable Principle

The theoretical core is:

```text
Structure → Slice → Stability
```

Do not modify it.

GyroOS expands this into runtime:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

Stability is a state quantity.

Stability does not control the loop directly.

LoopController decides OperatorResponse.

---

## 1. What to Implement

Implement only the following minimal PoC objects:

```text
Structure
OperatorOrientation
SliceRequest
SliceDone
StabilityResult
OperatorResponse
UpdateDecision
LoopState
MemoryRuntime
TrajectoryCache
DamperState
LoopStepResult
GyroRuntime
SliceEngine
StabilityEngine
LoopController
UpdateEngine
```

Optional but allowed only if simple:

```text
ReSliceEngine
DamperAction
```

---

## 2. What NOT to Implement

Do not implement:

```text
real OS kernel
real authentication
GyroAuth
external database
distributed storage
network API
FastAPI
WebSocket
React UI
Streamlit UI
plugin system
background daemon
multi-user system
real security layer
persistent file storage
cloud sync
complex vector database
LLM integration
```

Also do not implement:

```text
Stability as controller
UpdateEngine as loop owner
automatic Re-Slice from Context existence
automatic Jump from Void existence
automatic Stop from low Stability
Dynamic Equivalence as authentication
Fluid API as real protocol
```

---

## 3. Runtime Limits

Hard-code these limits:

```python
MAX_PROCESS_STEPS = 10
MAX_RESLICE_DEPTH = 2
MAX_CONTEXT_CHAIN_LENGTH = 3
MAX_TRAJECTORY_ENTRIES = 20
MAX_VOID_RECORDS = 5
MAX_BRANCH_COUNT = 2
DYNAMIC_EQUIVALENCE_ENABLED = False
FLUID_API_ENABLED = False
GYROAUTH_ENABLED = False
```

No infinite loops.

No unbounded recursion.

No background process.

No real external I/O.

---

## 4. Implementation Style

Use Python only.

Recommended structure:

```text
gyroos_poc/
  README.md
  requirements.txt
  demo.py
```

Prefer a single-file implementation first.

Use Python standard library only if possible.

Optional:

```text
rich
```

If Rich is used, include it in `requirements.txt`.

---

## 5. Required Runtime Flow

Implement `GyroRuntime.loop_step()`.

It must execute:

```text
1. Create GyroProcess
2. Create SliceRequest
3. SliceEngine executes slice-ing
4. SliceEngine returns SliceDone
5. MemoryRuntime stores SliceDone
6. StabilityEngine measures StabilityResult
7. LoopController decides OperatorResponse
8. UpdateEngine applies update only if requested
9. TrajectoryCache appends process evidence
10. DamperState updates pressure signals
11. Return LoopStepResult
```

---

## 6. Required Scenarios

Implement three demo scenarios.

### Scenario 1: Normal / Continue

```text
low Δ
high Stability
OperatorResponse = CONTINUE
UpdateEngine not used
```

### Scenario 2: Drift / Adjust

```text
increasing Δ
lower Stability
OperatorResponse = ADJUST
UpdateEngine creates next orientation
```

### Scenario 3: Void / Defer or Jump

```text
large Δ or not_evaluable Stability
Void appears
LoopController selects DEFER_VOID or JUMP
UpdateEngine may prepare next orientation if JUMP
```

---

## 7. Required Data Classes

Use dataclasses.

### Structure

```python
@dataclass
class Structure:
    structure_id: str
    payload: dict
    metadata: dict = field(default_factory=dict)
```

### OperatorOrientation

```python
@dataclass
class OperatorOrientation:
    orientation_id: str
    weights: dict[str, float]
    resolution: dict[str, float]
    target_dimensions: list[str]
    constraints: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

### SliceRequest

```python
@dataclass
class SliceRequest:
    request_id: str
    process_index: int
    source_type: str
    source_ref: str | None
    mode: str
    orientation: OperatorOrientation
    parent_process_id: str | None = None
    parent_slice_id: str | None = None
    metadata: dict = field(default_factory=dict)
```

### SliceDone

```python
@dataclass
class SliceDone:
    slice_id: str
    process_index: int
    representation: dict
    deviation: dict
    context: dict | None = None
    void: dict | None = None
    metadata: dict = field(default_factory=dict)
```

### StabilityResult

```python
@dataclass
class StabilityResult:
    process_index: int
    value: float | None
    status: str
    reason: str | None = None
    metadata: dict = field(default_factory=dict)
```

### OperatorResponse

```python
@dataclass
class OperatorResponse:
    process_index: int
    response_type: str
    reason: str
    next_request: SliceRequest | None = None
    update_decision: "UpdateDecision | None" = None
    metadata: dict = field(default_factory=dict)
```

### UpdateDecision

```python
@dataclass
class UpdateDecision:
    update_type: str
    previous_orientation: OperatorOrientation
    next_orientation: OperatorOrientation | None
    reason: str
    metadata: dict = field(default_factory=dict)
```

### LoopStepResult

```python
@dataclass
class LoopStepResult:
    loop_id: str
    process_index: int
    slice_done: SliceDone
    stability: StabilityResult
    operator_response: OperatorResponse
    update_decision: UpdateDecision | None
    trajectory_id: str
    next_ready: bool
    metadata: dict = field(default_factory=dict)
```

---

## 8. Required Response Types

Use exactly these response types:

```text
CONTINUE
ADJUST
RESLICE_CONTEXT
DEFER_VOID
JUMP
STOP
```

For the first PoC, implement only:

```text
CONTINUE
ADJUST
DEFER_VOID
JUMP
STOP
```

`RESLICE_CONTEXT` may be stubbed.

---

## 9. Decision Rules

Implement simple deterministic rules.

Example:

```python
if stability.status == "not_evaluable" or slice_done.void:
    response = "DEFER_VOID"
elif stability.value is not None and stability.value >= 0.75:
    response = "CONTINUE"
elif stability.value is not None and stability.value >= 0.45:
    response = "ADJUST"
else:
    response = "JUMP"
```

Important:

```text
These are PoC rules.
They are not Gyro Logic definitions.
```

---

## 10. Output Requirements

The demo must print each step.

Each step should show:

```text
Process index
Operator Orientation
slice-ing status
SliceDone representation X
Deviation Δ
Context / Void
StabilityResult
OperatorResponse
UpdateDecision if any
TrajectoryCache size
Damper pressure signals
```

---

## 11. Expected Console Demo

The console output should make this visible:

```text
[Process 1]
Orientation: default
slice-ing...
SliceDone: X={...}, Δ={...}
Stability: 0.91 stable
LoopController: CONTINUE

[Process 2]
Orientation: default
slice-ing...
SliceDone: X={...}, Δ={...}
Stability: 0.62 adaptive
LoopController: ADJUST
UpdateEngine: next orientation adjusted

[Process 3]
Orientation: adjusted
slice-ing...
SliceDone: X={...}, Δ={...}, Void={...}
Stability: not_evaluable
LoopController: DEFER_VOID
```

---

## 12. Theory Safety Requirements

The implementation must preserve the following:

```text
SliceDone is separate from StabilityResult.
StabilityResult is separate from OperatorResponse.
LoopController decides OperatorResponse.
UpdateEngine only applies requested updates.
MemoryRuntime stores references and summaries.
TrajectoryCache preserves continuity evidence.
DamperState reports pressure but does not control the loop.
```

---

## 13. Deliverables

Return:

```text
1. Short implementation explanation
2. File structure
3. requirements.txt
4. README.md
5. demo.py complete code
6. How to run
7. Expected output example
8. Notes on what is intentionally not implemented
```

---

## 14. Final Instruction

Implement the smallest bounded runtime demonstration of GyroOS.

Do not implement a real OS, real authentication, distributed storage, or unbounded autonomous loops.

The success condition is:

```text
A user can run demo.py and see a bounded GyroOS runtime loop:
Structure → slice-ing → SliceDone → StabilityResult → OperatorResponse → Next Process
```
