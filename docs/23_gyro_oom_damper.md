# 23. Gyro-OOM Damper

---

## Overview

This document defines the Gyro-OOM Damper for GyroOS.

Gyro-OOM Damper is a runtime pressure-control mechanism for preventing uncontrolled expansion of Context Loop, Re-Slice, Trajectory Cache, and Memory Runtime.

It does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

Gyro-OOM Damper is not a kill switch.

It is a controlled damping mechanism.

---

## Core Definition

```text
Gyro-OOM Damper = runtime mechanism that reduces expansion pressure without erasing trajectory continuity.
```

It handles situations such as:

```text
recursive Re-Slice growth
Context chain expansion
Trajectory Cache explosion
Void accumulation
hot memory overflow
Dynamic Equivalence evidence explosion
```

---

## What Gyro-OOM Damper Is Not

Gyro-OOM Damper is not:

```text
process kill
history deletion
Deviation erasure
Void erasure
forced convergence
Stability controller
```

It must not destroy the runtime evidence needed for Dynamic Equivalence or future Re-Slice.

---

## Runtime Position

```text
Memory Runtime
→ pressure signals
→ Loop Controller / Operator Response
→ Gyro-OOM Damper action if selected
→ resolution decay | defer | compress | branch control | stop
```

Important:

```text
Gyro-OOM Damper does not independently control the Loop.
Loop Controller / Operator Response selects damping actions.
```

---

## Pressure Signals

Possible pressure signals:

```text
memory_pressure
hot_tier_overflow
context_chain_growth
reslice_depth_exceeded
trajectory_count_high
trajectory_branch_explosion
void_accumulation
equivalence_group_expansion
cycle_detected
cost_budget_exceeded
```

These signals are inputs to Operator Response.

They do not directly force action.

---

## Damping Actions

Recommended actions:

```text
RESOLUTION_DECAY
CONTEXT_COMPRESSION
TRAJECTORY_COMPRESSION
DEFER_VOID
LIMIT_RESLICE
BRANCH_FREEZE
COLD_ARCHIVE
REQUEST_JUMP
REQUEST_STOP
```

---

## RESOLUTION_DECAY

Reduce resolution without deleting continuity.

```text
full → summary → vector → pointer
```

Use when:

```text
object is old
low access frequency
low local inertia
low current relevance
memory pressure exists
```

Do not use when:

```text
object is active trajectory evidence
object is unresolved high-severity Void
object is needed for current Dynamic Equivalence check
```

---

## CONTEXT_COMPRESSION

Compress ContextRecord while preserving context chain references.

Correct:

```text
ContextRecord.full → ContextRecord.summary
```

Incorrect:

```text
ContextRecord → delete
```

Context compression must preserve:

```text
source_slice_id
source_process_id
confidence
inferability_score
context_chain
```

---

## TRAJECTORY_COMPRESSION

Compress Trajectory Cache entries.

Possible reduction:

```text
process_refs → stability_summary + deviation_summary + response_summary
```

Trajectory compression must preserve:

```text
branch points
Jump boundaries
Void references
Dynamic Equivalence evidence
```

---

## DEFER_VOID

Defer unresolved Void rather than resolving it immediately.

```text
VoidRecord.deferred = true
```

Use when:

```text
Void inferability is low
Re-Slice would likely expand pressure
Jump is premature
future Context may clarify the Void
```

---

## LIMIT_RESLICE

Limit or stop recursive Re-Slice expansion.

Triggers:

```text
reslice_depth_exceeded
context_chain_cycle
reslice_branch_explosion
cost_budget_exceeded
```

Possible response:

```text
DEFER_VOID
CHANGE_ORIENTATION
BRANCH_FREEZE
REQUEST_JUMP
REQUEST_STOP
```

---

## BRANCH_FREEZE

Freeze a trajectory branch without deleting it.

Use when:

```text
branch is unstable
branch is too expensive
branch has low local inertia
branch has insufficient evidence
```

Frozen branches may be restored later.

---

## COLD_ARCHIVE

Move low-activity trajectory or context records to cold or external storage.

Preserve local pointer.

```text
full / summary → pointer
```

Cold archive should preserve retrieval capability.

---

## REQUEST_JUMP

Gyro-OOM Damper may recommend Jump.

It does not execute Jump by itself.

Correct relation:

```text
pressure signal
→ Operator Response
→ JUMP
→ Update Engine / Re-orientation
```

Incorrect relation:

```text
Gyro-OOM Damper → Jump directly
```

---

## REQUEST_STOP

Gyro-OOM Damper may recommend Stop when runtime cost becomes unrecoverable.

Stop remains an Operator Response decision.

---

## Damper Policy Model

```python
class DamperPolicy:
    max_reslice_depth: int
    max_context_chain_length: int
    max_hot_entries: int
    max_active_branches: int
    max_void_records: int
    memory_pressure_threshold: float
    cold_archive_enabled: bool
    stop_allowed: bool
```

---

## DamperAction Model

```python
class DamperAction:
    action_id: str
    action_type: str
    target_ref: str
    reason: str
    reversible: bool
    metadata: dict
```

---

## Runtime Flow

```text
Memory Runtime / Trajectory Cache
   ↓
Pressure Signal
   ↓
Loop Controller / Operator Response
   ↓
DamperAction selected
   ├─ RESOLUTION_DECAY
   ├─ CONTEXT_COMPRESSION
   ├─ TRAJECTORY_COMPRESSION
   ├─ DEFER_VOID
   ├─ LIMIT_RESLICE
   ├─ BRANCH_FREEZE
   ├─ COLD_ARCHIVE
   ├─ REQUEST_JUMP
   └─ REQUEST_STOP
```

---

## API Implications

Possible future endpoints:

```text
GET  /damper/state
GET  /damper/pressure
POST /damper/apply
POST /damper/policy
```

These are support endpoints.

The main runtime endpoint remains:

```text
POST /loop/step
```

---

## Design Constraints

Gyro-OOM Damper MUST NOT:

```text
redefine Structure → Slice → Stability
act as Stability controller
kill processes by default
delete Δ silently
delete Void silently
erase trajectory branches
execute Jump directly
make authentication decisions
```

Gyro-OOM Damper MUST:

```text
preserve trajectory continuity
prefer resolution decay over deletion
preserve references for retrieval
report pressure to Operator Response
support reversible compression where possible
protect Dynamic Equivalence evidence
limit uncontrolled Re-Slice and Context Loop recursion
```

---

## Key Insight

Gyro-OOM Damper does not forget by destruction.

It reduces runtime pressure by lowering resolution, deferring unresolved regions, and preserving continuity references.

In short:

```text
Damping is not deletion.
Damping is controlled reduction of runtime pressure.
```

---

## Summary

Gyro-OOM Damper prevents GyroOS runtime expansion from becoming uncontrollable.

It protects Memory Runtime, Trajectory Cache, Context Loop, Re-Slice, Void, and Dynamic Equivalence evidence.

It preserves the invariant core:

```text
Structure → Slice → Stability
```

and acts only as a runtime support mechanism under Operator Response.

---

## Next

```text
docs/24_fluid_api_pattern.md
```
