# 247. vNext Inspection Comparison Register Comparison T3 Review

## 1. Scope

Reviewed:

```text
T3 optional comparison endpoint
```

## 2. Endpoint

```text
POST /vnext/experimental/inspection-comparison-register-comparisons
```

The endpoint creates and returns one request-local comparison report only.

Decision:

```text
T3 optional comparison endpoint
= COMPLETE AT IMPLEMENTATION LEVEL
```

## 3. Endpoint Isolation

The endpoint does not add:

```text
GET collection
GET item
PUT item
PATCH item
DELETE item
repository storage
export
implicit source retrieval
```

Decision:

```text
Request-local endpoint isolation
= ACCEPTED
```

## 4. Error Boundary

Comparison validation errors are translated to:

```text
HTTP 422
GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_INVALID
EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_CREATE
```

They do not become Runtime, authentication, semantic trend, risk, attack, OperatorResponse, DifferenceObject, or BoundaryEvaluation outcomes.

Decision:

```text
Comparison error non-mapping
= ACCEPTED
```

## 5. Existing Route Preservation

Unchanged:

```text
experimental record CRUD
D-S experimental routes
/loop/step
Runtime endpoints
```

## 6. Final Decision

```text
T3 optional comparison endpoint
= ACCEPTED PENDING WORKFLOW VERIFICATION

Comparison register retrieval
= NOT INTRODUCED

R comparison retrieval
= NOT INTRODUCED

Semantic trend analysis
= NOT INTRODUCED

Risk aggregation
= NOT INTRODUCED

Authentication aggregation
= NOT INTRODUCED

Runtime integration
= NOT INTRODUCED

Canonical persistence
= NOT INTRODUCED

Critical design blocker
= NONE IDENTIFIED
```
