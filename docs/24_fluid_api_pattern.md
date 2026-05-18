# 24. Fluid API Pattern

---

## Overview

This document defines the **Fluid API Pattern** for GyroOS.

Fluid API is a conceptual interface pattern for connecting external applications to GyroOS runtime continuity.

It is not yet a fixed API specification.

It does not replace current GyroOS runtime APIs.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

---

## Status

Fluid API is:

```text
conceptual interface pattern
application connection model
runtime continuity access pattern
```

Fluid API is not:

```text
core Gyro Logic definition
replacement for /loop/step
GyroAuth-specific protocol
static token exchange protocol
```

---

## Core Idea

Traditional APIs often exchange static tokens or isolated request-response payloads.

Fluid API connects applications to a continuous runtime layer.

Instead of:

```text
request → response
```

Fluid API thinks in terms of:

```text
runtime trajectory
→ continuous state interpretation
→ application interaction
```

---

## Relation to GyroOS Runtime

GyroOS main runtime API remains:

```text
POST /loop/step
```

This means:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

Fluid API may be built on top of runtime outputs such as:

```text
SliceDone
Deviation
StabilityResult
Operator Response
Context
Trajectory Cache
Dynamic Equivalence Result
```

---

## Conceptual Flow

```text
External Application
   ↓
Fluid API Pattern
   ↓
GyroOS Runtime
   ↓
/loop/step
   ↓
SliceDone + Stability + Operator Response + Trajectory
   ↓
Application-level interpretation
```

Fluid API does not make GyroOS decisions.

It exposes continuity to applications.

---

## Difference from Static API

### Static API

```text
Client
→ token / request
→ server validates static state
→ response
```

### Fluid API Pattern

```text
Client / Observer / Application
→ continuous runtime relation
→ GyroOS evaluates trajectory continuity
→ application interprets result
```

---

## Fluid API and Trajectory

Fluid API should expose or reference Trajectory rather than only one-time state.

Possible objects:

```text
trajectory_id
process_index
stability_summary
deviation_summary
context_chain
dynamic_equivalence_result
operator_response
```

Applications can use these to interpret continuity.

---

## Fluid API and Context

Fluid API may expose Context as inferred surrounding structure.

However:

```text
Context is not Representation.
Context is not Void.
Context is not an application decision.
```

Applications may request Context-aware continuity, but GyroOS remains responsible for runtime evaluation.

---

## Fluid API and Dynamic Equivalence

Fluid API may expose Dynamic Equivalence results.

Example:

```text
equivalent
not_equivalent
undecidable
```

Application layers may interpret these differently.

Example:

```text
GyroAuth:
equivalent → AUTH_STABLE candidate
undecidable → RECONVERGING / REAUTH candidate
not_equivalent → AUTH_FAIL candidate
```

But these mappings belong to the application layer, not GyroOS core.

---

## Representative Application: GyroAuth

GyroAuth is a representative application of the Fluid API Pattern.

GyroAuth may use runtime continuity instead of one-time static token matching.

GyroAuth may consume:

```text
Trajectory
StabilityResult
Deviation
Operator Response
Dynamic Equivalence Result
Context
```

But GyroAuth must not redefine GyroOS.

Correct boundary:

```text
GyroOS:
continuity / equivalence / runtime response

GyroAuth:
authentication decision
```

---

## Possible Interface Objects

### FluidSession

```python
class FluidSession:
    session_id: str
    application_id: str
    trajectory_id: str
    current_process_index: int
    state: str
    metadata: dict
```

### FluidState

```python
class FluidState:
    trajectory_id: str
    stability: dict
    deviation: dict
    context: dict | None
    operator_response: dict
    equivalence: dict | None
```

### FluidEvent

```python
class FluidEvent:
    event_id: str
    session_id: str
    event_type: str
    process_index: int
    payload: dict
```

---

## Possible Endpoint Pattern

Fluid API may eventually define endpoints such as:

```text
POST /fluid/session/start
POST /fluid/session/step
GET  /fluid/session/{session_id}/state
GET  /fluid/session/{session_id}/trajectory
POST /fluid/equivalence/check
POST /fluid/session/close
```

These are not yet canonical GyroOS APIs.

The current canonical runtime API remains:

```text
POST /loop/step
```

---

## Stream-like Interaction

Fluid API may be implemented as:

```text
polling
server-sent events
websocket
streaming state updates
batch runtime steps
```

But implementation transport is secondary.

The important part is continuity:

```text
state over trajectory
not isolated request-response only
```

---

## Security Boundary

Fluid API may expose runtime continuity to applications.

It must not expose internal memory or raw trajectory data unnecessarily.

Recommended security principles:

```text
least privilege
trajectory-scoped access
context redaction
void redaction
application-specific projection
audit trail
```

---

## Relation to Memory Runtime

Fluid API may access Memory Runtime through controlled references.

It should expose:

```text
summary
vector
pointer
application projection
```

rather than raw internal memory by default.

---

## Relation to Gyro-OOM Damper

Fluid API usage may create pressure.

Examples:

```text
too many sessions
too many trajectory subscriptions
too many equivalence checks
stream overload
```

Gyro-OOM Damper may respond through runtime pressure control.

Fluid API should respect:

```text
rate limit
trajectory cache pressure
context chain depth
memory tier policy
```

---

## Design Constraints

Fluid API Pattern MUST NOT:

```text
redefine Structure → Slice → Stability
replace /loop/step as the core runtime meaning
turn GyroAuth into GyroOS core
expose raw internal state by default
reduce runtime continuity to static tokens
treat Dynamic Equivalence as authentication by itself
```

Fluid API Pattern MUST:

```text
preserve GyroOS / application boundary
expose continuity through controlled projection
support trajectory-aware interaction
support application-level interpretation
remain subordinate to Operator Response and runtime architecture
```

---

## Key Insight

Fluid API is not a protocol first.

It is a way for applications to interact with runtime continuity.

In short:

```text
Static API exchanges state.
Fluid API exposes continuity.
```

---

## Summary

Fluid API Pattern defines how applications may connect to GyroOS as a continuous runtime system.

It is especially relevant to GyroAuth, but it is not limited to authentication.

It preserves the invariant core:

```text
Structure → Slice → Stability
```

and remains below application-specific decisions.

---

## Next

```text
docs/25_local_inertia.md
```
