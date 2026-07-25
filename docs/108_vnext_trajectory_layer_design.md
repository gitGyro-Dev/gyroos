# 108. vNext Trajectory Layer Design

---

## 1. Purpose

This document defines the next isolated design boundary for a vNext Trajectory Layer.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Trajectory is not a fourth Core stage.

---

## 2. Placement

Trajectory is designed as a cross-record relation layer above the isolated semantic, readability, and continuity records:

```text
Semantic records
Readability records
Continuity readability records
──────────────
Trajectory reference layer
──────────────
```

The layer may reference records from those groups, but it does not own, rewrite, merge, or canonicalize them.

---

## 3. Trajectory Is Not ContinuityRelationRecord

```text
ContinuityRelationRecord
= one explicit statement about readability of a possible relation

Trajectory
= an explicit graph-shaped grouping of nodes and edges across records
```

Therefore:

```text
ContinuityRelationRecord
≠ Trajectory edge
```

A later explicit mapping may reference a ContinuityRelationRecord as evidence for an edge. That mapping must never be inferred merely because the relation exists.

---

## 4. Proposed Minimal Models

### 4.1 TrajectoryNode

```text
trajectory_node_id
process_id
record_ref
record_type
slice_ref
node_role
provisional
created_at
metadata
```

A node is a reference wrapper only.

It does not duplicate the referenced record.

### 4.2 TrajectoryEdge

```text
trajectory_edge_id
process_id
source_node_ref
target_node_ref
edge_type
relation_ref
readable
provisional
authoritative
evidence_refs[]
created_at
metadata
```

`relation_ref` is optional and caller-supplied.

An edge does not automatically mean causal, temporal, identity-preserving, or continuous.

### 4.3 TrajectoryGraph

```text
trajectory_graph_id
process_id
trajectory_node_refs[]
trajectory_edge_refs[]
root_node_refs[]
terminal_node_refs[]
provisional
created_at
metadata
```

The graph stores references only.

---

## 5. Initial Allowed Shape

The first PoC may allow:

```text
zero or more nodes
zero or more edges
zero or more roots
zero or more terminals
```

It should validate only:

```text
common process scope
edge source/target refs point to bundled nodes
root/terminal refs point to bundled nodes
unique node IDs
unique edge IDs
```

It should not require a connected graph.

It should not require acyclicity.

---

## 6. Branch, Merge, Gap, Revision

Trajectory must be able to represent these shapes later:

```text
branch
merge
gap
revision
supersession
parallel relation
```

However, the first implementation should not infer any of them from graph topology.

For example:

```text
one node with two outgoing edges
```

must not automatically become a semantic `branch` unless an explicit edge/node role states that interpretation.

---

## 7. Time and Establishment Order

Trajectory list order is not time order.

```text
node list order
edge list order
created_at
```

must not automatically define:

```text
establishment order
causal order
continuity order
importance
precedence
canonical history
```

Time references may be added explicitly later, but remain separate from graph membership.

---

## 8. Identity Boundary

Trajectory does not prove Identity continuity.

```text
same process_id
same record type
same source/target chain
connected graph
```

are insufficient to assert Identity.

Likewise:

```text
Identity break
≠ Trajectory break
≠ continuity break
```

These remain separate judgments.

---

## 9. Runtime Boundary

The first Trajectory Layer must remain isolated from:

```text
POST /loop/step
ProcessExecutor
StabilityEngine
OperatorResponse selection
SQLite schema
canonical repository registry
Trajectory publication
GyroAuth decisions
```

No automatic graph generation from Runtime history is allowed in the first PoC.

---

## 10. Explicit Non-responsibilities

The Trajectory Layer does not initially:

```text
calculate scores
select a preferred path
select a canonical path
infer branch or merge semantics
repair gaps
collapse revisions
resolve conflicts
prove causality
prove continuity
prove Identity
choose OperatorResponse
execute rollback
persist records
```

---

## 11. Recommended Implementation Order

```text
1. TrajectoryNode
2. TrajectoryEdge
3. TrajectoryGraph
4. pure builders
5. reference-integrity tests
6. TrajectoryAssemblyService
7. review
8. only then consider Runtime or persistence integration
```

---

## 12. Current Decision

```text
Trajectory Layer design
= COMPLETE

Trajectory implementation
= NOT STARTED

ContinuityRelationRecord treated as TrajectoryEdge
= NO

Runtime integration
= NO

SQLite integration
= NO

Critical design blocker
= NONE IDENTIFIED
```
