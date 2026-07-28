# 279. vNext Inspection Architecture Decision Record

## 1. Scope

This document is the X7 deliverable for integration gate X.

It decides whether the inspection hierarchy should extend beyond gate W or whether consolidation should take priority.

This decision does not modify implementation, endpoints, tests, Runtime behavior, persistence, or public contracts.

## 2. Inputs

The decision is based on:

```text
X1 Contract Inventory / Hierarchy Map
X2 Naming and Readability Review
X3 Shared-Abstraction Review
X4 Router and Workflow Growth Review
X5 Inspection API Contract Index
X6 Documentation Index Review
```

## 3. Findings

The current inspection family already has a deep explicit-reference chain from F through W.

From H onward, the architecture repeatedly alternates between:

```text
comparison report
→ grouping manifest
→ comparison report
→ grouping manifest
```

The contracts remain bounded and isolated, but the cost is visible in:

```text
long module and class names
long endpoint paths
long error codes
large router imports
large workflow command lists
high documentation navigation cost
repeated validation and digest code
```

## 4. New Hierarchy Necessity Test

A new hierarchy level is approved only when all of the following are true:

```text
1. A concrete bounded consumer exists.
2. The new contract has a distinct meaning.
3. Existing F-W contracts cannot represent the requirement.
4. The benefit exceeds naming and maintenance cost.
5. Runtime, persistence, semantic, risk, and authentication boundaries remain unchanged.
```

Current evidence does not satisfy these conditions.

## 5. Decision

```text
Additional archive/comparison hierarchy after W
= NOT APPROVED

Mechanical continuation of naming hierarchy
= NOT APPROVED

Inspection contract consolidation
= APPROVED

Documentation and navigation consolidation
= APPROVED

Small pure utility extraction
= APPROVED AS A FUTURE CANDIDATE

Dedicated inspection router
= APPROVED AS A FUTURE CANDIDATE

Checked-in explicit workflow test groups
= APPROVED AS A FUTURE CANDIDATE
```

## 6. Implementation Boundary

Gate X does not authorize immediate refactoring.

Any implementation change must be handled by a separate bounded gate with:

```text
explicit scope
compatibility review
contract-specific tests
workflow verification
rollback-safe sequencing
no public contract change unless separately approved
```

The first implementation candidate should remain small.

Preferred order:

```text
1. Add a stable inspection documentation index.
2. Add explicit workflow test-group files without reducing coverage.
3. Split inspection routes into one dedicated router.
4. Evaluate one small pure validation utility.
```

Each step requires its own review before proceeding to the next.

## 7. Preserved Boundaries

Unchanged:

```text
Structure → Slice → Stability
Gyro Logic → GyroOS → GyroAuth
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
```

Still prohibited:

```text
implicit retrieval
semantic inference
risk aggregation
authentication aggregation
attack classification
Runtime mutation
canonical persistence
GET collection or item routes for inspection contracts
PUT
PATCH
DELETE
public export
GyroAuth coupling
```

## 8. Next Gate Decision

The next gate must not introduce another inspection hierarchy layer.

Recommended next gate:

```text
Y — Inspection Consolidation Implementation Planning
```

Its purpose should be limited to selecting and sequencing the smallest approved consolidation changes.

Gate Y must begin with documentation and workflow structure before code-level genericization.

## 9. Final Decision

```text
X7 architecture decision record
= COMPLETE

Need for hierarchy extension after W
= NOT ESTABLISHED

Further inspection hierarchy extension
= REJECTED

Consolidation before extension
= REQUIRED

Runtime and persistence boundaries
= UNCHANGED

Recommended next gate
= Y Inspection Consolidation Implementation Planning
```
