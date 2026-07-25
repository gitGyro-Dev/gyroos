# 112. vNext Trajectory Relation Taxonomy Review

---

## 1. Purpose

This document reviews whether the current Trajectory text fields should be replaced by enums or canonical registries:

```text
TrajectoryNode.record_type
TrajectoryNode.node_role
TrajectoryEdge.edge_type
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

This review does not add a new Core stage and does not connect Trajectory to Runtime or persistence.

---

## 2. Reviewed Sources

The review is based on the current isolated Trajectory design and implementation:

```text
docs/108_vnext_trajectory_layer_design.md
docs/109_vnext_trajectory_layer_minimal_poc.md
docs/110_vnext_trajectory_assembly_service.md
docs/111_vnext_trajectory_assembly_review.md
app/vnext/models.py
app/vnext/builders.py
app/vnext/trajectory_assembly.py
```

The current model intentionally uses caller-supplied text.

---

## 3. Review Question

The decision question is:

```text
Should record_type, node_role, and edge_type now become fixed enums?
```

The review must distinguish:

```text
implementation labels
≠
theoretical semantics
```

and:

```text
explicit caller assertion
≠
inferred graph meaning
```

---

## 4. record_type Review

### 4.1 Current Role

`record_type` identifies the kind of external record referenced by one TrajectoryNode.

Current examples may include:

```text
StabilityScene
StabilityObservation
DifferenceObject
BoundaryEvaluation
ReadabilityContext
IncorporationRecord
SceneReadabilityRelation
ContinuityReadabilityContext
ContinuityRelationRecord
SemanticRealizationBundle
ReadabilityRelationBundle
ContinuityRelationBundle
```

These values are implementation record labels, not Gyro Logic concepts or trajectory semantics.

### 4.2 Enum Assessment

A closed enum is premature because:

```text
new isolated record models may still be added
cross-repository records may later be referenced
GyroAuth-specific records must not be forced into GyroOS taxonomy
canonical repository registration does not yet exist
record resolution is intentionally not implemented
```

### 4.3 Decision

```text
record_type
= KEEP AS CALLER-SUPPLIED TEXT
```

Recommended discipline:

```text
use the exact model/class name when referencing a known vNext record
use a namespaced value for external records when needed
```

Example external form:

```text
gyroauth:AuthenticationDecision
```

This is documentation guidance only. No registry validation is introduced.

---

## 5. node_role Review

### 5.1 Current Role

`node_role` is an optional caller-supplied interpretation of a node within one explicit graph.

Possible meanings discussed so far include:

```text
root
terminal
branch point
merge point
gap boundary
revision point
superseded item
parallel item
```

However, root and terminal membership are already represented separately by:

```text
TrajectoryGraph.root_node_refs[]
TrajectoryGraph.terminal_node_refs[]
```

Therefore `node_role` must not duplicate or override graph membership fields.

### 5.2 Semantic Risk

Topology alone is insufficient to infer role:

```text
multiple outgoing edges
≠ semantic branch

multiple incoming edges
≠ semantic merge

missing direct edge
≠ semantic gap
```

A closed enum now would risk treating provisional interpretations as canonical semantics.

### 5.3 Decision

```text
node_role
= KEEP OPTIONAL CALLER-SUPPLIED TEXT
```

Initial descriptive vocabulary may be used, but remains non-canonical:

```text
OBSERVED
REFERENCE
REVISION_POINT
SUPERSEDED
PARALLEL
BRANCH_CANDIDATE
MERGE_CANDIDATE
GAP_BOUNDARY
```

The suffix `CANDIDATE` is preferred where graph topology has not been semantically reviewed.

The following must not be inferred automatically:

```text
ROOT
TERMINAL
BRANCH
MERGE
GAP
CURRENT
CANONICAL
AUTHORITATIVE
```

---

## 6. edge_type Review

### 6.1 Current Role

`edge_type` states the caller-declared meaning of one explicit edge.

Potential meanings span several independent dimensions:

```text
temporal
establishment-order
continuity-readable
causal
revision
supersession
reference
parallel
branch
merge
gap
identity-related
```

These dimensions are not mutually exclusive.

### 6.2 Enum Risk

A single closed enum would incorrectly collapse independent relation dimensions.

For example:

```text
TEMPORAL
CONTINUITY
SUPERSEDES
```

may all apply to one source-target pair without being equivalent.

Likewise:

```text
ContinuityRelationRecord
≠ TrajectoryEdge
```

and a `relation_ref` does not determine `edge_type` automatically.

### 6.3 Decision

```text
edge_type
= KEEP AS CALLER-SUPPLIED TEXT
```

A minimal non-canonical descriptive vocabulary is recorded for consistency:

```text
REFERENCES
FOLLOWS
PRECEDES
REVISES
SUPERSEDES
PARALLEL_TO
CONTINUITY_READABLE_TO
BRANCH_CANDIDATE_TO
MERGE_CANDIDATE_TO
GAP_BRIDGE_CANDIDATE_TO
```

These are labels only.

They do not prove:

```text
causality
continuity success
Identity preservation
chronological truth
canonical ordering
```

---

## 7. Why No Enum Is Added

The current architecture requires openness at this stage:

```text
record_type
= extensible external-record label

node_role
= optional graph-local interpretation

edge_type
= explicit relation assertion
```

Converting these to enums now would create at least four risks:

```text
1. freeze provisional theoretical distinctions
2. confuse graph topology with semantic meaning
3. force cross-layer records into a GyroOS-owned registry
4. create false validation authority before record resolution exists
```

Therefore no model or builder change is required by this review.

---

## 8. Normalization Guidance

Although fields remain text, callers should follow these conventions:

```text
uppercase snake case for semantic labels
exact class/model name for known record_type values
namespace external record types when ambiguity exists
avoid synonyms inside one graph or one project artifact
```

Examples:

```text
record_type = "ContinuityRelationRecord"
node_role = "BRANCH_CANDIDATE"
edge_type = "CONTINUITY_READABLE_TO"
```

This guidance does not create automatic normalization or validation.

---

## 9. Conditions for Future Taxonomy Promotion

A canonical taxonomy may be reconsidered only when all applicable conditions are met:

```text
multiple real Trajectory artifacts exist
repeated labels are observed across artifacts
synonym conflicts materially affect interoperability
record resolution or registry validation is introduced
cross-repository ownership rules are defined
branch / merge / gap semantics are theoretically stabilized
migration impact can be measured
```

Future promotion should likely use separate dimensions rather than one broad enum.

Potential later structure:

```text
record_namespace
record_type

node_structural_role
node_semantic_role

edge_order_relation
edge_continuity_relation
edge_revision_relation
edge_identity_relation
```

This structure is not implemented now.

---

## 10. Explicit Non-decisions

This review does not define:

```text
canonical path
current node
preferred node
preferred edge
authoritative edge
branch detection
merge detection
gap detection
causal inference
temporal inference
continuity scoring
Identity continuity
OperatorResponse mapping
```

It also does not modify:

```text
TrajectoryNode
TrajectoryEdge
TrajectoryGraph
TrajectoryAssemblyService
POST /loop/step
SQLite schema
```

---

## 11. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

Trajectory added to Core
= NO

Topology treated as semantics
= NO

ContinuityRelationRecord converted automatically to edge
= NO

Identity continuity inferred
= NO

Runtime history treated as TrajectoryGraph
= NO

Current RC Runtime contract changed
= NO
```

---

## 12. Review Decision

```text
Trajectory relation taxonomy review
= COMPLETE

record_type enum
= NOT ADOPTED

node_role enum
= NOT ADOPTED

edge_type enum
= NOT ADOPTED

Caller-supplied text
= RETAINED

Normalization guidance
= DOCUMENTED

Future promotion criteria
= DOCUMENTED

Implementation changes required
= NONE

Critical design blocker
= NONE IDENTIFIED
```

---

## 13. Next Decision

The isolated Trajectory construction layer is now structurally complete.

Before Runtime or persistence integration, the next review should determine whether to proceed with:

```text
A. Cross-layer Semantic / Readability / Continuity / Trajectory composition review
```

or:

```text
B. vNext isolated architecture completion review
```

Do not connect Trajectory to `/loop/step` or SQLite solely because this taxonomy review is complete.
