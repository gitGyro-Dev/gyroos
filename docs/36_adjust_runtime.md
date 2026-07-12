# 36. Adjust Runtime

---

## 1. Overview

This document defines **Adjust** in GyroOS after the Gyro Logic v3.1 Core Definition refinement.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Adjust is not a new Core element.

Adjust is an **Operator Response** that preserves Runtime Continuity while applying a bounded, continuous modification to the next runtime relation.

---

## 2. Core Definition

```text
Adjust is an Operator Response that preserves Runtime Continuity
by applying a bounded, continuous modification to Orientation,
Slice Policy, resolution, target relation, or other runtime conditions.
```

Japanese:

```text
Adjustとは、Orientation・Slice Policy・resolution・target relationなどの
Runtime条件へ連続的かつ限定的な変更を加えながら、
Runtime Continuityを保持するOperator Responseである。
```

---

## 3. What Adjust Is Not

Adjust is not:

```text
new Core stage
Stability update
automatic correction
unbounded optimization
Jump
Re-Slice
silent mutation
application decision
```

Also:

```text
Adjust ≠ Continue without change
Adjust ≠ discontinuous reconstruction
```

---

## 4. Relation to Runtime Continuity

Adjust preserves connectability through a continuous modification.

```text
Current established relation
↓
Operator Response = ADJUST
↓
bounded runtime modification
↓
next relation remains directly connectable
```

The current Structure / Slice relation remains usable as the direct continuity substrate.

```text
Adjust preserves direct path continuity.
```

---

## 5. Relation to Stability

Stability does not automatically produce Adjust.

```text
Stability ≠ Adjust
```

A safer relation is:

```text
Slice Result
+ Stability
+ Δ
+ Boundary State
+ Context
+ Trajectory history
+ runtime constraints
↓
Loop Controller / Operator Response
↓
ADJUST
```

Stability remains a state quantity.

The Loop Controller owns the response decision.

---

## 6. Adjust and Continue

```text
Continue
= preserve Runtime Continuity without a significant runtime modification

Adjust
= preserve Runtime Continuity while applying a bounded continuous modification
```

Both preserve direct connectability.

They remain separate Operator Response types because their runtime effects differ.

---

## 7. Adjust and Jump

```text
Adjust
= continuous recalibration within the current path relation

Jump
= non-continuous reconstruction of the runtime connection
```

A safe distinction is:

```text
Adjust:
current Structure / Slice relation remains directly usable

Jump:
current Structure / Slice relation is not sufficient as the next direct path
```

---

## 8. Adjust and Re-Slice

Adjust changes runtime conditions for a next direct relation.

Re-Slice opens a new Slice over an established or retained source.

```text
ADJUST
→ Update Engine
→ next Orientation / Policy
→ next direct runtime relation
```

```text
RESLICE
→ ReSliceRequest
→ Re-Slice Engine
→ new Slice operation
```

Adjust may prepare conditions later used by Re-Slice, but Adjust is not Re-Slice.

---

## 9. Adjust and Defer

```text
Adjust
= modify and connect now

Defer
= retain connectability for later without immediate connection
```

Adjust requires the next direct relation to be sufficiently grounded and executable.

---

## 10. Adjust and Stop

```text
Adjust
= preserve current execution connection through bounded modification

Stop
= end the current execution connection within the current control scope
```

Stop does not perform an adjustment by itself.

---

## 11. Adjustment Targets

Possible implementation-level targets include:

```text
Operator Orientation
Slice Policy
resolution
granularity
target dimensions
weights
constraints
Context dependency
memory access priority
runtime budget allocation
```

These targets are implementation choices.

They do not modify Gyro Logic definitions.

---

## 12. Bounded Adjustment

Adjust must be bounded.

Possible limits:

```text
max adjustment magnitude
allowed target dimensions
minimum continuity confidence
maximum policy delta
maximum resolution change
runtime cost budget
safety constraints
```

When a required change exceeds the allowed continuous range, the Loop Controller may consider:

```text
RESLICE
JUMP
DEFER
STOP
```

The limit itself does not determine the response automatically.

---

## 13. Runtime Objects

```python
class AdjustDecision:
    adjust_id: str
    process_index: int

    source_process_id: str
    source_slice_id: str
    source_stability_ref: str

    target_type: str
    previous_value: object
    next_value: object
    adjustment_delta: object

    continuity_preserved: bool
    bounded: bool
    reason: str
    evidence_refs: list[str]
    metadata: dict
```

Recommended invariant:

```text
continuity_preserved = true
bounded = true
```

for a valid `ADJUST` response.

---

## 14. Runtime Flow

```text
Current Structure
↓
Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
↓
Stability
↓
Loop Controller / Operator Response
↓
ADJUST
↓
Update Engine
↓
Next Orientation / Slice Policy / Runtime Condition
↓
Next directly connectable runtime relation
```

The Update Engine applies the selected adjustment.

It does not decide whether Adjust should occur.

---

## 15. API Implications

A `/loop/step` result may include:

```json
{
  "operator_response": {
    "response_type": "ADJUST",
    "reason": "bounded orientation recalibration required"
  },
  "adjustment": {
    "target_type": "orientation",
    "continuity_preserved": true,
    "bounded": true,
    "next_ready": true
  }
}
```

`ADJUST` is a valid runtime result.

It is not an error response.

---

## 16. Design Constraints

Adjust MUST NOT:

```text
redefine Structure → Slice → Stability
be selected automatically by Stability alone
act as Jump
act as Re-Slice
apply unbounded changes
hide the adjustment delta
let Update Engine own the response decision
mix GyroAuth decisions into GyroOS
```

Adjust MUST:

```text
remain an Operator Response
preserve direct Runtime Continuity
apply a bounded continuous modification
record what changed and why
remain traceable in Trajectory Cache
be applied through Update Engine when implementation requires it
```

---

## 17. Key Insight

Adjust is not correction toward a fixed answer.

Adjust is bounded recalibration that keeps the current runtime relation directly connectable.

```text
Adjust changes conditions without abandoning the current path relation.
```

---

## 18. Summary

Adjust is an Operator Response that preserves Runtime Continuity through bounded continuous modification.

It is distinct from Continue, Re-Slice, Jump, Defer, and Stop.

The invariant Core remains unchanged:

```text
Structure → Slice → Stability
```
