# 14. API Design

---

## Overview

This document defines the API model for GyroOS v4.0.

The central API is:

```text
POST /loop/step
```

This endpoint does not mean a simple input-output computation.

It executes one **Gyro Process** and one **Operator Response**.

GyroOS must preserve the invariant theoretical core:

```text
Structure → Slice → Stability
```

The API must not redefine this core.

---

## Runtime Meaning of /loop/step

`POST /loop/step` executes the following runtime sequence:

```text
Structure
→ Operator Orientation
→ slice-ing
→ slice-done = X + Δ
→ Stability
→ Operator Response
→ Next Process preparation
```

Therefore, `/loop/step` is not:

```text
observe → evaluate → update
```

It is:

```text
orientation
→ slice-ing
→ slice-done
→ stability measurement
→ operator response
→ next orientation / next process
```

---

## Key Constraint

Stability does not directly control the loop.

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

## Main Endpoint

```text
POST /loop/step
```

### Purpose

Execute one Gyro Process and produce an Operator Response.

### Request

```json
{
  "loop_id": "gyro_loop_001",
  "structure": {},
  "orientation": {},
  "context": {},
  "previous_state_ref": "optional"
}
```

### Response

```json
{
  "loop_id": "gyro_loop_001",
  "process_index": 12,
  "slice_done": {
    "representation": {},
    "deviation": {}
  },
  "stability": {},
  "operator_response": {
    "response_type": "continue | adjust | stop | jump | void",
    "reason": "string"
  },
  "update_decision": {},
  "next_orientation": {},
  "next_process_ready": true
}
```

---

## Internal Runtime Steps

### 1. Orientation

Apply Operator Orientation or Slice Policy.

```text
Structure → Operator Orientation
```

---

### 2. slice-ing

Execute the temporal Slice process.

```text
Operator Orientation → slice-ing
```

---

### 3. slice-done

Produce completed Slice result.

```text
slice-done = X + Δ
```

---

### 4. Stability Measurement

Measure Stability as a state quantity of slice-done.

```text
σ = Stab(X, Δ)
```

Stability is measured.
It does not decide.

---

### 5. Operator Response

Loop Controller generates Operator Response.

```text
Responseₙ = R(slice-doneₙ, Stabilityₙ, Δₙ, Historyₙ)
```

Possible responses:

```text
continue
adjust
stop
jump
void
```

---

### 6. Optional Update

Update Engine is called only when Operator Response requires it.

```text
Operator Response
→ Update Engine if needed
→ Next Orientation / Slice Policy
```

---

## Supporting Endpoints

### GET /loop/state

Returns current LoopState.

---

### GET /loop/history

Returns process, response, stability, deviation, and orientation history.

---

### GET /response/history

Returns Operator Response history.

---

### GET /orientation/current

Returns current Operator Orientation or Slice Policy.

---

### POST /observe

Optional low-level endpoint for executing Slice Engine directly.

This should not be treated as the main runtime endpoint.

---

### POST /update

Optional low-level endpoint for applying an UpdateDecision.

This should only be used under Operator Response.

---

## API Boundary

GyroOS provides runtime state and response information.

GyroOS does not make application-specific decisions such as authentication approval.

For example, GyroOS may return:

```text
Stability
Deviation
Operator Response
Next Orientation
```

GyroAuth may interpret these as:

```text
AUTH_STABLE
RECONVERGING
AUTH_FAIL
```

The application decision belongs to GyroAuth, not GyroOS core.

---

## Design Constraints

The API MUST NOT:

```text
redefine Structure → Slice → Stability
treat Stability as controller
collapse slice-ing and slice-done
make /update the main runtime endpoint
make Update Engine the loop owner
delete Δ
mix GyroAuth authentication decisions into GyroOS
```

The API MUST:

```text
expose /loop/step as the main runtime endpoint
represent one Gyro Process per step
return slice-done = X + Δ
return Stability as state quantity
return Operator Response
optionally return UpdateDecision
prepare Next Orientation / Next Process
```

---

## Summary

`POST /loop/step` is the primary runtime API of GyroOS v4.0.

It means:

```text
Run one Gyro Process and produce one Operator Response.
```

It does not mean:

```text
Compute one answer.
```

Correct runtime interpretation:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```
