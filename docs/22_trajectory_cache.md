# 22. Trajectory Cache

---

## Overview

This document defines the Trajectory Cache model for GyroOS.

Trajectory Cache is a runtime cache for preserving, retrieving, and comparing process trajectories.

It supports:

```text
Re-Slice
Context Loop
Dynamic Equivalence
Local Inertia
Memory Runtime
Gyro-OOM damping
```

Trajectory Cache does not redefine Gyro Logic.

The invariant theoretical core remains:

```text
Structure → Slice → Stability
```

---

## Core Definition

```text
Trajectory Cache = runtime cache of Gyro Process continuity.
```

It stores references and summaries of Gyro Process history so that GyroOS can reason over continuity without retaining all raw data at full resolution.

Trajectory Cache is not just history storage.

It is a runtime lookup and continuity support layer.

---

## Position in GyroOS

GyroOS runtime flow:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

Trajectory Cache supports this flow by maintaining continuity across processes.

It may provide evidence for:

```text
next Operator Orientation
Dynamic Equivalence
Re-Slice candidate selection
Context relevance
Local inertia
memory compression decisions
```

Trajectory Cache does not decide the next process.

The Loop Controller / Operator Response decides.

---

## What Trajectory Cache Stores

Recommended stored elements:

```text
process_refs
slice_refs
context_refs
void_refs
stability_summary
deviation_summary
operator_response_summary
orientation_summary
dynamic_equivalence_evidence
local_inertia_score
resolution_level
storage_tier
```

---

## Data Model

```python
class TrajectoryCacheEntry:
    trajectory_id: str

    process_refs: list[str]
    slice_refs: list[str]
    context_refs: list[str]
    void_refs: list[str]
    response_refs: list[str]

    stability_summary: dict
    deviation_summary: dict
    orientation_summary: dict

    dynamic_equivalence_evidence: dict
    local_inertia_score: float

    resolution_level: str
    storage_tier: str
    metadata: dict
```

---

## Trajectory Index

Trajectory Cache should support lookup by multiple keys.

Recommended indexes:

```text
trajectory_id
process_id
context_id
void_id
orientation_signature
stability_range
deviation_pattern
dynamic_equivalence_group
```

Example:

```python
class TrajectoryIndex:
    by_trajectory_id: dict[str, str]
    by_context_id: dict[str, list[str]]
    by_void_id: dict[str, list[str]]
    by_orientation_signature: dict[str, list[str]]
    by_equivalence_group: dict[str, list[str]]
```

---

## Resolution Levels

Trajectory Cache follows Memory Runtime resolution levels:

```text
full
summary
vector
pointer
```

### full

Detailed references to all process and slice records.

### summary

Compressed stability / deviation / response summaries.

### vector

Low-dimensional trajectory direction representation.

### pointer

External or archived reference.

---

## Cache Lifecycle

Recommended lifecycle:

```text
create
extend
stabilize
summarize
compress
retrieve
branch
archive
```

### create

A new trajectory begins.

### extend

A new process is appended.

### stabilize

Trajectory is marked as stability-relevant.

### summarize

Trajectory is reduced to summarized form.

### compress

Trajectory is reduced to vector or pointer representation.

### retrieve

Trajectory is materialized for Re-Slice or Dynamic Equivalence.

### branch

Trajectory splits due to Jump or major Orientation change.

### archive

Trajectory moves to cold or external storage.

---

## Relation to Dynamic Equivalence

Dynamic Equivalence requires trajectory evidence.

Trajectory Cache provides:

```text
trajectory continuity
stability preservation evidence
deviation range evidence
context consistency evidence
jump / stop boundary evidence
```

Without sufficient trajectory cache evidence, Dynamic Equivalence should return:

```text
undecidable
```

---

## Relation to Re-Slice

Re-Slice may use Trajectory Cache to locate relevant Context or prior SliceDone.

```text
Operator Response
→ RESLICE_CONTEXT
→ Trajectory Cache lookup
→ ContextRecord retrieval
→ Re-Slice Engine
```

Trajectory Cache does not decide to Re-Slice.

It only provides lookup and evidence.

---

## Relation to Context Loop

Context Loop may extend a trajectory through Context.

```text
Trajectory_n
→ Context_n
→ Re-Slice(Context_n)
→ Trajectory_{n+1}
```

Trajectory Cache must track:

```text
context_chain
reslice_depth
cycle_detected
branch points
```

---

## Relation to Local Inertia

Local Inertia may be calculated from Trajectory Cache.

Example factors:

```text
access frequency
recent use
stability relevance
context relevance
void unresolvedness
dynamic equivalence importance
```

Example:

```python
local_inertia_score = (
    access_weight
    + stability_weight
    + context_weight
    + unresolved_void_weight
    + equivalence_weight
)
```

High local inertia may keep trajectory data in hot or warm storage.

---

## Relation to Jump

Jump may create a trajectory branch.

Trajectory Cache must preserve the branch point.

```text
Trajectory_A
→ JUMP
→ Trajectory_B
```

Jump should not erase the previous trajectory.

It may mark Dynamic Equivalence across the branch as:

```text
not_equivalent
undecidable
equivalent_under_new_context
```

depending on policy and evidence.

---

## Cache Pressure

Trajectory Cache may grow rapidly.

Pressure signals:

```text
trajectory_count_high
hot_cache_overflow
context_chain_growth
reslice_branch_explosion
void_reference_accumulation
equivalence_group_expansion
```

Trajectory Cache does not kill processes.

It reports pressure to Memory Runtime and Loop Controller / Operator Response.

---

## API Implications

Possible future endpoints:

```text
GET  /trajectory/{trajectory_id}
GET  /trajectory/{trajectory_id}/summary
GET  /trajectory/search
POST /trajectory/retrieve
POST /trajectory/compress
```

These are support endpoints.

The main runtime endpoint remains:

```text
POST /loop/step
```

---

## Design Constraints

Trajectory Cache MUST NOT:

```text
redefine Structure → Slice → Stability
control the Loop directly
replace Loop Controller
replace Memory Runtime
delete Δ history silently
delete Void references silently
treat trajectory similarity as Dynamic Equivalence by itself
make authentication decisions
```

Trajectory Cache MUST:

```text
preserve continuity evidence
support Dynamic Equivalence
support Re-Slice retrieval
support Context Loop tracking
support Jump branch preservation
support resolution decay
report cache pressure
```

---

## Key Insight

Trajectory Cache is not a log.

It is a continuity substrate.

In short:

```text
History records what happened.
Trajectory Cache preserves what can still be connected.
```

---

## Summary

Trajectory Cache allows GyroOS to preserve runtime continuity under limited memory.

It supports Re-Slice, Context Loop, Dynamic Equivalence, Local Inertia, and Memory Runtime without changing the invariant core:

```text
Structure → Slice → Stability
```

---

## Next

```text
docs/23_gyro_oom_damper.md
```
