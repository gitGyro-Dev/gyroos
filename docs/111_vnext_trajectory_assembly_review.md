# 111. vNext Trajectory Assembly Review

---

## 1. Purpose

This document records the review of the isolated Trajectory assembly pipeline:

```text
TrajectoryNodeSpec[]
+
TrajectoryEdgeSpec[]
→ TrajectoryAssemblyService
→ TrajectoryNode[]
+
TrajectoryEdge[]
+
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

The review evaluates implementation boundaries only. It does not promote Trajectory into the Core, Runtime contract, persistence model, or continuation decision path.

---

## 2. Review Scope

Reviewed components:

```text
TrajectoryNodeSpec
TrajectoryEdgeSpec
TrajectoryAssemblyRequest
TrajectoryAssemblyService
TrajectoryAssemblyResult
TrajectoryNodeBuilder
TrajectoryEdgeBuilder
TrajectoryGraphBuilder
TrajectoryNode
TrajectoryEdge
TrajectoryGraph
```

Reviewed tests:

```text
tests/vnext/test_trajectory_layer.py
tests/vnext/test_trajectory_assembly_service.py
```

Verified workflow runs:

```text
30158004382 = success
30158015270 = success
30158033108 = success
30158051683 = success
```

---

## 3. Request / Record Separation

```text
TrajectoryNodeSpec
≠ TrajectoryNode

TrajectoryEdgeSpec
≠ TrajectoryEdge

TrajectoryAssemblyRequest
≠ TrajectoryGraph
```

The request describes explicit construction inputs.

The service returns newly constructed in-memory records.

Decision:

```text
Request / record separation
= ACCEPTED
```

---

## 4. Builder Delegation

The service delegates construction to:

```text
TrajectoryNodeBuilder
TrajectoryEdgeBuilder
TrajectoryGraphBuilder
```

It does not duplicate graph validation rules or mutate constructed records after builder completion.

Decision:

```text
Builder delegation
= ACCEPTED
```

---

## 5. Request-local Endpoint Boundary

Every edge endpoint must reference a node assembled in the same request.

```text
source_node_ref
→ request-local TrajectoryNode

target_node_ref
→ request-local TrajectoryNode
```

The service does not search persistence, import external nodes, or infer substitutes.

Decision:

```text
Request-local endpoint boundary
= ACCEPTED
```

---

## 6. Reference-only Graph Boundary

`TrajectoryGraph` stores only:

```text
trajectory_node_refs[]
trajectory_edge_refs[]
root_node_refs[]
terminal_node_refs[]
```

It does not embed complete nodes or edges.

This preserves:

```text
Trajectory records
≠ Graph grouping record
```

Decision:

```text
Reference-only graph boundary
= ACCEPTED
```

---

## 7. Non-inference Boundary

The assembly does not infer:

```text
nodes from existing records
edges from timestamps
edges from list order
edges from ContinuityRelationRecord
root nodes
terminal nodes
current node
preferred path
authoritative edge
branch meaning
merge meaning
gap meaning
```

Decision:

```text
Graph inference boundary
= ACCEPTED
```

---

## 8. Continuity Separation

The following remains explicit:

```text
ContinuityRelationRecord
≠ TrajectoryEdge
```

A continuity relation may be referenced by `relation_ref`, but it is not converted automatically into an edge.

Decision:

```text
Continuity / Trajectory separation
= ACCEPTED
```

---

## 9. Identity Separation

The following remains explicit:

```text
Identity break
≠ Trajectory break
≠ continuity break
```

The assembly does not infer Identity continuity or Identity break from graph structure.

Decision:

```text
Identity separation
= ACCEPTED
```

---

## 10. Runtime and Persistence Isolation

The assembly remains isolated from:

```text
POST /loop/step
ProcessExecutor
StabilityEngine
OperatorResponse selection
Priority G/H canonical records
SQLite schema
repository reconstruction registry
public API models
```

Decision:

```text
Runtime isolation
= ACCEPTED

Persistence isolation
= ACCEPTED
```

---

## 11. Copy and Mutation Boundary

Nested specification metadata is copied into constructed records.

Caller mutation after assembly does not rewrite the assembled result.

Decision:

```text
Copy / mutation boundary
= ACCEPTED
```

---

## 12. Test and Workflow Review

The tests cover:

```text
explicit node / edge / graph assembly
empty graph
request-local endpoint enforcement
duplicate node ID rejection
duplicate edge ID rejection
non-inference of edges, roots, terminals, and authority
deep-copy behavior
```

The full bounded Runtime and vNext regression workflow completed successfully in all supplied runs.

Decision:

```text
Test coverage for isolated assembly boundary
= ACCEPTED

Workflow verification
= ACCEPTED
```

---

## 13. Findings

No critical blocker was identified.

One intentionally open design area remains:

```text
record_type
node_role
edge_type
```

These remain caller-supplied text.

This is acceptable for the current isolated PoC because no canonical taxonomy, Runtime contract, persistence schema, or public API depends on them.

Premature enumeration could incorrectly freeze theoretical distinctions before sufficient use cases exist.

---

## 14. Final Decision

```text
Trajectory Assembly Review
= COMPLETE

TrajectoryAssemblyService
= ACCEPTED AS ISOLATED ORCHESTRATION FACADE

TrajectoryAssemblyRequest / Result boundary
= ACCEPTED

TrajectoryNode / Edge / Graph construction pipeline
= ACCEPTED

Critical design blocker
= NONE IDENTIFIED

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED
```

---

## 15. Next Decision

Proceed to:

```text
Trajectory relation taxonomy review
```

That review should determine whether caller-supplied text remains sufficient for:

```text
record_type
node_role
edge_type
```

Do not introduce enums, canonical taxonomy, Runtime mapping, persistence mapping, or automatic relation inference unless the review identifies a concrete need.
