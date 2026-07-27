# 219. vNext Inspection Comparison Collection Comparison P3 Review

## 1. Scope

Reviewed:

```text
P3 optional comparison endpoint
```

## 2. Endpoint

```text
POST /vnext/experimental/inspection-comparison-collection-comparisons
```

The endpoint accepts one explicit P comparison request and returns one request-local comparison report.

Decision:

```text
P3 optional comparison endpoint
= COMPLETE AT DESIGN / IMPLEMENTATION LEVEL
```

## 3. Endpoint Isolation

The endpoint does not introduce:

```text
GET comparison retrieval
comparison listing
comparison update
comparison delete
repository storage
export
canonical persistence
```

Decision:

```text
Request-local endpoint isolation
= ACCEPTED
```

## 4. Error Boundary

P comparison validation errors are mapped to:

```text
HTTP 422
GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_INVALID
EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_CREATE
```

They are not mapped into Runtime, authentication, semantic trend, risk, attack, OperatorResponse, BoundaryEvaluation, or DifferenceObject outcomes.

Decision:

```text
Endpoint error non-mapping
= ACCEPTED
```

## 5. Route Preservation

Existing D-O experimental routes and experimental record CRUD remain present and unchanged in responsibility.

```text
Existing route preservation
= ACCEPTED
```

## 6. Test Boundary

Tests cover:

```text
request-local comparison creation
same-collection rejection
absence of Runtime/authentication/semantic outputs
absence of retrieval routes
```

The route absence check inspects the experimental router directly and does not depend on shared rate-limiter state.

## 7. Runtime and Persistence Boundary

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
consumer boundary D
compatibility boundary E
inspection receipt boundary F
inspection batch manifest boundary G
inspection manifest comparison boundary H
inspection comparison review bundle boundary I
inspection review bundle comparison boundary J
inspection review bundle comparison set boundary K
inspection review bundle comparison set comparison boundary L
inspection comparison-set comparison series boundary M
inspection comparison series comparison boundary N
inspection comparison-series comparison collection boundary O
```

## 8. Final Decision

```text
P3 optional comparison endpoint
= COMPLETE AT DESIGN / IMPLEMENTATION LEVEL

Comparison collection retrieval
= NOT INTRODUCED

N comparison retrieval
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

Public comparison retrieval
= NOT INTRODUCED

GitHub Actions verification
= PENDING

Critical design blocker
= NONE IDENTIFIED
```
