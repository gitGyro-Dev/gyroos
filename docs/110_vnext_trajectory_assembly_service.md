# 110. vNext Trajectory Assembly Service

---

## 1. Purpose

This document records the isolated orchestration step for the Trajectory Layer:

```text
explicit node and edge specifications
→ TrajectoryAssemblyRequest
→ TrajectoryAssemblyService
→ TrajectoryAssemblyResult
→ TrajectoryGraph
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

The service is an implementation facade. It is not a new Core stage, causal engine, path evaluator, authority selector, branch/merge engine, persistence transaction, or Runtime executor.

---

## 2. Added Components

Updated:

```text
app/vnext/models.py
```

Added input models:

```text
TrajectoryNodeSpec
TrajectoryEdgeSpec
TrajectoryAssemblyRequest
```

Added output model:

```text
TrajectoryAssemblyResult
```

Added service:

```text
app/vnext/trajectory_assembly.py
TrajectoryAssemblyService
```

Primary operation:

```text
assemble(request)
→ TrajectoryAssemblyResult
```

---

## 3. Assembly Sequence

The service coordinates existing builders in this implementation order:

```text
TrajectoryNodeBuilder[]
↓
TrajectoryEdgeBuilder[]
↓
TrajectoryGraphBuilder
```

This is orchestration order only.

It does not define:

```text
time order
causal order
theoretical establishment order
preferred path order
authority precedence
branch order
merge order
```

---

## 4. Request / Record Separation

The request contains specification models:

```text
TrajectoryNodeSpec
TrajectoryEdgeSpec
```

These are not constructed Trajectory records.

The service uses them to create:

```text
TrajectoryNode
TrajectoryEdge
TrajectoryGraph
```

This preserves:

```text
caller construction specification
≠
constructed in-memory record
```

---

## 5. Service Responsibility

The service performs only:

```text
construct zero or more explicit TrajectoryNode records
ensure node IDs are unique within the request
resolve edge endpoint refs within the same request
construct zero or more explicit TrajectoryEdge records
ensure edge IDs are unique within the request
construct one explicit reference-only TrajectoryGraph
return all records in memory
```

The service delegates record validation and copy behavior to the existing pure builders and models.

---

## 6. Request-local Reference Boundary

Each edge specification must reference nodes assembled in the same request:

```text
source_node_ref
→ one assembled TrajectoryNode

target_node_ref
→ one assembled TrajectoryNode
```

A missing endpoint is rejected.

The service does not search a repository, resolve a latest node, import an external node, or infer replacement endpoints.

---

## 7. Explicit Non-responsibilities

The service does not:

```text
resolve node record_ref values
validate record_type against a registry
infer nodes from existing records
infer edges from timestamps
infer edges from list order
infer edges from ContinuityRelationRecord
calculate path score
select a preferred path
select a current node
select an authoritative edge
infer branch semantics
infer merge semantics
infer gap semantics
repair gaps
perform path search
detect cycles
reject cycles
assert acyclicity
calculate reachability
map OperatorResponse
select OperatorResponse
persist records
register canonical record types
modify SemanticAssemblyService
modify IncorporatedReadabilityAssemblyService
modify ContinuityReadabilityAssemblyService
modify POST /loop/step
modify SQLite schema
```

The following separations remain explicit:

```text
ContinuityRelationRecord
≠ TrajectoryEdge
```

```text
Identity break
≠ Trajectory break
≠ continuity break
```

```text
TrajectoryGraph
≠ Runtime history list
```

---

## 8. Optional Records

A valid request may contain:

```text
zero node specs
zero edge specs
zero root refs
zero terminal refs
```

The resulting empty graph remains valid.

The service does not synthesize missing nodes, edges, roots, or terminals.

---

## 9. Test Coverage

Added:

```text
tests/vnext/test_trajectory_assembly_service.py
```

Coverage includes:

```text
explicit node / edge / graph assembly
empty graph
request-local endpoint enforcement
duplicate node ID rejection
duplicate edge ID rejection
no edge/root/terminal/authority inference
deep-copy boundary
```

The Priority F workflow now executes this test with all accepted Priority G/H and earlier vNext tests.

---

## 10. Isolation Boundary

The service remains isolated from:

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

## 11. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Trajectory Assembly added to Core
= NO

Edge inference introduced
= NO

Path authority inferred
= NO

Branch / merge semantics introduced
= NO

Runtime history treated as TrajectoryGraph
= NO

Current RC Runtime contract changed
= NO
```

---

## 12. Current Decision

```text
TrajectoryNodeSpec
= VERIFIED AS ISOLATED INPUT MODEL

TrajectoryEdgeSpec
= VERIFIED AS ISOLATED INPUT MODEL

TrajectoryAssemblyRequest
= VERIFIED AS ISOLATED INPUT MODEL

TrajectoryAssemblyService
= VERIFIED AS ISOLATED ORCHESTRATION FACADE

TrajectoryAssemblyResult
= VERIFIED AS ISOLATED IN-MEMORY RESULT

Current /loop/step behavior
= UNCHANGED

Current SQLite schema
= UNCHANGED

GitHub Actions verification
= VERIFIED
```

Verified workflow runs:

```text
30158004382 = success
30158015270 = success
30158033108 = success
30158051683 = success
```

---

## 13. Next Decision

Perform:

```text
Trajectory Assembly Review
```

If no critical blocker is identified, then review whether caller-supplied text remains sufficient for:

```text
record_type
node_role
edge_type
```

That later step is the separate:

```text
Trajectory relation taxonomy review
```

Do not connect Trajectory assembly to `/loop/step` or SQLite before those reviews are complete.
