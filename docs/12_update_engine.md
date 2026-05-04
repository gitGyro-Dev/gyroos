# 12. Update Engine

---

## Overview

The Update Engine is an internal support component of the GyroOS v4.0 Loop Controller.

It is not the center of GyroOS v4.0.

In Gyro Logic, the core structure remains:

```text
Structure → Slice → Stability
```

GyroOS v4.0 implements the temporal process as:

```text
Structure
→ Operator Orientation
→ slice-ing
→ slice-done
→ Stability
→ Operator Response
→ Next Process
```

The Loop Controller implements **Operator Response**.

The Update Engine is used only when Operator Response requires modification of the next Operator Orientation, Slice Policy, resolution, weight, or transition structure.

Correct relation:

```text
Stability
→ Loop Controller / Operator Response
→ Update Engine if needed
→ Next Orientation
```

Incorrect relation:

```text
Stability
→ Update Engine
→ Loop Controller
```

---

## Role in GyroOS v4.0

The Update Engine does not decide whether the loop continues, stops, jumps, or enters void handling.

Those decisions belong to the Loop Controller as Operator Response.

The Update Engine receives a response request from the Loop Controller and produces an update decision.

```text
Operator Response
→ Update Engine
→ Update Decision
→ Next Orientation / Policy
```

---

## Core Responsibilities

### 1. Apply Operator Response

The Update Engine applies a response selected by the Loop Controller.

Examples:

```text
Adjust
Re-orient
Jump preparation
Resolution change
Weight redistribution
```

---

### 2. Update Operator Orientation

The primary output of the Update Engine is an updated Operator Orientation.

```text
Orientationₙ₊₁ = U(Orientationₙ, Responseₙ, Historyₙ)
```

The Update Engine may update:

```text
direction
weight
constraint
resolution
target dimension
context dependency
```

---

### 3. Update Slice Policy

When GyroOS represents Operator Orientation through a Slice Policy, the Update Engine may update that policy.

Slice Policy is therefore an implementation representation of Orientation, not the theory itself.

---

### 4. Adjust Resolution

The Update Engine may adjust observation resolution.

Examples:

```text
coarse → fine
fine → coarse
narrow → broad
local → global
```

Resolution change is not an answer.

It is a change in how the next slice-ing process will be oriented.

---

### 5. Adjust Weights

The Update Engine may redistribute weights among active dimensions or slice candidates.

Examples:

```text
increase weight of stable dimension
decrease weight of noisy dimension
preserve unstable dimension for further observation
```

Important:

```text
Δ must not be deleted.
Low stability does not automatically mean removal.
```

---

### 6. Prepare Jump

The Update Engine may prepare a non-continuous reconstruction when the Loop Controller selects Jump.

However:

```text
Jump is selected by the Loop Controller.
Jump is not initiated by the Update Engine itself.
```

The Update Engine only constructs the implementation-level transition.

---

### 7. Support Void Handling

When the Loop Controller detects or classifies a Void response mode, the Update Engine may prepare:

```text
reset orientation
hold state
re-orient
fallback policy
jump candidate
```

Important:

```text
Void does not act by itself.
The Loop Controller selects the response to Void.
```

---

## Data Model

```python
class UpdateDecision:
    process_index: int
    update_type: str
    reason: str

    previous_orientation: OperatorOrientation
    next_orientation: OperatorOrientation | None

    previous_policy: SlicePolicy | None
    next_policy: SlicePolicy | None

    jump_candidate: bool
    void_related: bool
```

---

```python
class UpdateRequest:
    process_index: int
    response_type: str

    current_orientation: OperatorOrientation
    current_policy: SlicePolicy | None

    slice_done: SliceDone
    stability: Stability
    deviation: Deviation

    history_ref: str | None
```

---

## Update Types

```text
orientation_adjustment
policy_adjustment
weight_adjustment
resolution_change
dimension_shift
context_rebinding
jump_preparation
void_reorientation
hold
```

---

## Execution Flow

```text
slice-done = X + Δ
        ↓
Stability
        ↓
Loop Controller
        ↓
Operator Response
        ↓
Update Engine if needed
        ↓
Update Decision
        ↓
Next Orientation / Policy
```

---

## Runtime Pseudocode

```python
def apply_response(response, current_orientation, current_policy=None):
    if response.response_type == "continue":
        return UpdateDecision(
            update_type="hold",
            previous_orientation=current_orientation,
            next_orientation=current_orientation,
            reason="continue without major orientation change"
        )

    if response.response_type == "adjust":
        return adjust_orientation(
            orientation=current_orientation,
            response=response,
            policy=current_policy
        )

    if response.response_type == "reorient":
        return reorient(
            orientation=current_orientation,
            response=response
        )

    if response.response_type == "jump":
        return prepare_jump(
            orientation=current_orientation,
            response=response
        )

    if response.response_type == "void":
        return prepare_void_reorientation(
            orientation=current_orientation,
            response=response
        )

    if response.response_type == "stop":
        return UpdateDecision(
            update_type="hold",
            previous_orientation=current_orientation,
            next_orientation=None,
            reason="process repetition stopped"
        )

    return UpdateDecision(
        update_type="hold",
        previous_orientation=current_orientation,
        next_orientation=current_orientation,
        reason="unknown response type; hold orientation"
    )
```

---

## Relation to slice-ing and slice-done

The Update Engine never operates during slice-ing.

It acts only after:

```text
slice-ing → slice-done → Stability → Operator Response
```

Therefore:

```text
Update Engine does not create slice-done.
Update Engine does not measure Stability.
Update Engine does not control slice-ing directly.
```

It prepares the conditions for the next slice-ing process by updating Orientation or Slice Policy.

---

## API Implications

The Update Engine may be exposed through an internal or auxiliary API:

```text
POST /update
```

However, `/update` should not be treated as the main runtime API.

The main runtime API remains:

```text
POST /loop/step
```

`POST /loop/step` should call the Update Engine only through the Loop Controller when Operator Response requires it.

---

## Design Constraints

The Update Engine MUST NOT:

```text
replace the Loop Controller
act before Stability is available
treat Stability as controller
delete Δ
treat Slice Policy as fixed
initiate Jump by itself
treat Void as an actor
mix GyroAuth authentication logic into GyroOS
```

The Update Engine MUST:

```text
act only under Operator Response
update Orientation or Slice Policy when requested
preserve Δ as signal
support continuous adjustment
support jump preparation
support void reorientation
return explicit UpdateDecision
```

---

## Key Insight

The Update Engine does not drive the Gyro Loop.

It implements part of the Operator Response selected by the Loop Controller.

In short:

```text
Loop Controller decides.
Update Engine applies.
```

---

## Summary

The Update Engine is a subordinate implementation module in GyroOS v4.0.

Its role is to transform Operator Response into an updated Orientation or Slice Policy for the next Gyro Process.

It should be understood as:

```text
Operator Response → Update Decision → Next Orientation
```

not as:

```text
Stability → Update → Loop
```

---

## Next

docs/13_slice_policy.md
