# 25. Local Inertia

---

## Overview

This document defines **Local Inertia** in GyroOS.

Local Inertia explains why some Trajectories, Contexts, and runtime references remain locally available instead of being aggressively compressed, archived, or externalized.

It is not a replacement for Memory Runtime.

It is not a cache implementation by itself.

It is a runtime persistence principle used by Memory Runtime, Trajectory Cache, and Fluid API patterns.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

---

## Core Definition

```text
Local Inertia = tendency of runtime objects to remain locally available when they are repeatedly relevant to ongoing Gyro Processes.
```

Local Inertia is created by repeated use, stability relevance, trajectory continuity, context relevance, and unresolved runtime dependency.

---

## What Local Inertia Is Not

Local Inertia is not:

```text
static cache pinning
manual favorite marking
permanent storage
authentication decision
Stability controller
```

It should be understood as runtime persistence pressure.

---

## Runtime Position

```text
Gyro Process
→ SliceDone
→ Stability
→ Operator Response
→ Memory Runtime
→ Trajectory Cache
→ Local Inertia update
```

Local Inertia does not control the loop.

It influences memory tiering, retrieval priority, compression resistance, and offline availability.

---

## Objects Affected

Local Inertia may apply to:

```text
TrajectoryRecord
ContextRecord
SliceDoneRecord
VoidRecord
DynamicEquivalence evidence
OperatorResponse history
FluidSession state
```

---

## Inertia Factors

Recommended factors:

```text
access_frequency
recency
stability_relevance
trajectory_continuity
context_relevance
void_severity
equivalence_importance
application_demand
offline_requirement
```

---

## Local Inertia Score

Example model:

```python
local_inertia_score = (
    w_access * access_frequency
    + w_recency * recency
    + w_stability * stability_relevance
    + w_trajectory * trajectory_continuity
    + w_context * context_relevance
    + w_void * void_severity
    + w_equivalence * equivalence_importance
    + w_application * application_demand
)
```

This score is implementation-dependent.

It should not be treated as a Gyro Logic definition.

---

## Storage Tier Impact

Local Inertia influences storage tier decisions.

High inertia:

```text
hot or warm storage
reduced compression
faster retrieval
offline availability candidate
```

Low inertia:

```text
summary
vector
pointer
cold archive
external reference
```

---

## Relation to Resolution Decay

Local Inertia resists resolution decay.

```text
high local inertia → slower decay
low local inertia → faster decay
```

However, it must not prevent all compression.

Gyro-OOM Damper may still request compression under pressure.

---

## Relation to Trajectory Cache

Trajectory Cache may compute and store Local Inertia.

```text
TrajectoryCacheEntry.local_inertia_score
```

High local inertia indicates that a trajectory remains important for runtime continuity.

This may be because it is:

```text
frequently accessed
stability-relevant
needed for Dynamic Equivalence
connected to unresolved Void
part of active Context Loop
```

---

## Relation to Context

Context may gain Local Inertia when it is repeatedly selected or referenced.

Examples:

```text
Context repeatedly selected for Re-Slice
Context explains persistent deviation
Context stabilizes future trajectory
Context is used by Fluid API session
```

Context with high Local Inertia should remain retrievable.

---

## Relation to Void

Void may also create Local Inertia.

An unresolved Void with high severity should not disappear simply because it is unresolved.

```text
high-severity Void → local persistence pressure
```

However, unresolved Void may be compressed or deferred.

It must remain traceable.

---

## Relation to Fluid API

Fluid API sessions may increase Local Inertia for objects used in active application continuity.

Example:

```text
active FluidSession
→ trajectory subscription
→ increased local inertia
```

This supports continuous interaction without requiring constant full retrieval from external storage.

---

## Offline Continuity

Local Inertia can support offline or degraded-network continuity.

When network access is unavailable, high-inertia objects may remain locally available.

Candidates:

```text
active trajectories
recent contexts
high-confidence SliceDone summaries
required Dynamic Equivalence evidence
unresolved high-severity Void references
```

Offline continuity does not mean full system replication.

It means preserving enough trajectory substrate to continue limited runtime operation.

---

## Inertia Decay

Local Inertia should decay over time.

Possible decay factors:

```text
time since last access
reduced relevance
resolved Void
trajectory branch freeze
application session closed
external archive confirmed
```

Decay should be gradual unless Gyro-OOM pressure is severe.

---

## API Implications

Possible future endpoints:

```text
GET  /inertia/state
GET  /inertia/object/{object_id}
POST /inertia/update
POST /inertia/policy
```

These are support endpoints.

The main runtime endpoint remains:

```text
POST /loop/step
```

---

## Design Constraints

Local Inertia MUST NOT:

```text
redefine Structure → Slice → Stability
control the Loop directly
prevent Gyro-OOM damping absolutely
be treated as permanent memory
make authentication decisions
expose raw memory to applications by default
```

Local Inertia MUST:

```text
support runtime continuity
influence memory tiering
resist inappropriate resolution decay
preserve traceability of relevant Void and Context
support offline continuity when possible
remain subordinate to Memory Runtime and Operator Response
```

---

## Key Insight

Local Inertia is not memory hoarding.

It is runtime relevance becoming local persistence.

In short:

```text
Repeated relevance creates local persistence.
```

---

## Summary

Local Inertia gives GyroOS a principled way to decide what remains locally available.

It supports Memory Runtime, Trajectory Cache, Fluid API, Dynamic Equivalence, and offline continuity.

It preserves the invariant core:

```text
Structure → Slice → Stability
```

and remains a runtime support mechanism.

---

## Next

```text
PoC runtime implementation planning
```
