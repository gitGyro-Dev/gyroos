# 109. vNext Trajectory Layer Minimal PoC

---

## 1. Purpose

This document records the isolated implementation of:

```text
TrajectoryNode
↓
TrajectoryEdge
↓
TrajectoryGraph
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The Trajectory Layer is an implementation-level reference graph over explicit existing records. It is not a new Core stage, causal engine, continuity evaluator, Identity engine, current-state selector, or persistence graph.

---

## 2. Added Models

Updated:

```text
app/vnext/models.py
```

Added:

```text
TrajectoryNode
TrajectoryEdge
TrajectoryGraph
```

---

## 3. TrajectoryNode

Fields:

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

The node stores an explicit reference to an existing record.

It does not:

```text
resolve the record
copy the record
validate the record type against a registry
infer a canonical node role
select a current node
```

---

## 4. TrajectoryEdge

Fields:

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

The edge records one explicit relation between two TrajectoryNode references.

`relation_ref` is optional. A ContinuityRelationRecord may be referenced explicitly, but:

```text
ContinuityRelationRecord
≠ TrajectoryEdge
```

No automatic conversion is performed.

---

## 5. TrajectoryGraph

Fields:

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

The graph stores references only. It does not embed complete nodes or edges.

`root_node_refs` and `terminal_node_refs` are explicit caller-supplied references. They are not inferred from graph topology.

---

## 6. Added Builders

Updated:

```text
app/vnext/builders.py
```

Added:

```text
TrajectoryNodeBuilder
TrajectoryEdgeBuilder
TrajectoryGraphBuilder
```

### TrajectoryNodeBuilder

Performs only:

```text
copy explicit record reference and labels
copy metadata
create node ID when absent
```

### TrajectoryEdgeBuilder

Performs only:

```text
verify source/target process_id match
reject self-reference
verify optional expected endpoint refs
copy explicit relation values
copy metadata
create edge ID when absent
```

### TrajectoryGraphBuilder

Performs only:

```text
verify node process_id matches graph process_id
reject duplicate node IDs
verify edge process_id matches graph process_id
reject duplicate edge IDs
verify edge endpoints are bundled nodes
verify root refs are bundled nodes
verify terminal refs are bundled nodes
copy node and edge IDs
copy metadata
create graph ID when absent
```

---

## 7. Explicit Non-responsibilities

The models and builders do not:

```text
resolve referenced records
infer edges from timestamps
infer edges from list order
infer edges from ContinuityRelationRecord
infer Identity continuity
infer Identity break
calculate continuity score
calculate path score
select a preferred path
select an authoritative edge
select a current node
create branch semantics
create merge semantics
create gap semantics
repair gaps
resolve conflicts
perform path search
detect cycles
reject cycles
assert acyclicity
calculate reachability
map OperatorResponse
select OperatorResponse
persist records
modify /loop/step
modify SQLite schema
```

The following separations remain explicit:

```text
Identity break
≠ Trajectory break
≠ continuity break
```

and:

```text
Trajectory graph
≠ Runtime history list
```

---

## 8. Test Coverage

Added:

```text
tests/vnext/test_trajectory_layer.py
```

Coverage includes:

```text
reference-only graph grouping
explicit record reference preservation
edge process mismatch rejection
self-reference rejection
expected endpoint validation
external endpoint rejection
duplicate node ID rejection
duplicate edge ID rejection
root/terminal reference validation
no authority or path inference
deep-copy boundary
```

The Priority F workflow now executes this test with all accepted Priority G/H and earlier vNext tests.

---

## 9. Isolation Boundary

The Trajectory Layer remains isolated from:

```text
SemanticAssemblyService
IncorporatedReadabilityAssemblyService
ContinuityReadabilityAssemblyService
POST /loop/step
current ProcessExecutor
current StabilityEngine
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API models
OperatorResponse selection
```

The accepted release-candidate Runtime behavior remains unchanged.

---

## 10. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Trajectory added to Core
= NO

ContinuityRelationRecord converted automatically to edge
= NO

Identity continuity inferred
= NO

Path authority inferred
= NO

Runtime history treated as Trajectory graph
= NO

Current RC Runtime contract changed
= NO
```

---

## 11. Current Decision

```text
TrajectoryNode
= IMPLEMENTED AS ISOLATED REFERENCE MODEL

TrajectoryEdge
= IMPLEMENTED AS ISOLATED RELATION MODEL

TrajectoryGraph
= IMPLEMENTED AS ISOLATED REFERENCE GRAPH MODEL

TrajectoryNodeBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

TrajectoryEdgeBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

TrajectoryGraphBuilder
= IMPLEMENTED AS ISOLATED PURE BUILDER

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= PENDING
```

---

## 12. Next Decision

After workflow verification, review whether the next minimal step should be:

```text
A. Trajectory Assembly Service
```

that coordinates explicit node, edge, and graph builders without inference or persistence;

or:

```text
B. Trajectory relation taxonomy review
```

that constrains `record_type`, `node_role`, and `edge_type` only after confirming that caller-supplied text is no longer sufficient.

Do not connect the Trajectory Layer to `/loop/step` or SQLite before that review.
