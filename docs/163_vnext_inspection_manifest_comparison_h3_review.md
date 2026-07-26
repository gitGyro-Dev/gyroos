# 163. vNext Inspection Manifest Comparison H3 Review

## 1. Scope

Reviewed:

```text
POST /vnext/experimental/inspection-manifest-comparisons
ExperimentalManifestComparisonRequest
ExperimentalManifestComparisonResult
```

## 2. Endpoint Boundary

The endpoint accepts one explicit request and returns one request-local comparison report.

It does not retrieve or persist manifests, receipts, source records, or comparison reports.

Decision:

```text
Request-local endpoint boundary
= ACCEPTED
```

## 3. Error Mapping Boundary

Comparison validation errors are mapped to:

```text
HTTP 422
GYRO_VNEXT_EXPERIMENTAL_MANIFEST_COMPARISON_INVALID
```

They are not mapped to Runtime, authentication, identity, trajectory, attack, or OperatorResponse outcomes.

Decision:

```text
Comparison error mapping boundary
= ACCEPTED
```

## 4. Route Isolation

No retrieval, listing, updating, or deletion routes are introduced for comparison reports.

Existing routes remain registered:

```text
/loop/step
/vnext/experimental/records
/vnext/experimental/compatibility/check
/vnext/experimental/inspection-receipts
/vnext/experimental/inspection-batch-manifests
```

Decision:

```text
Existing route isolation
= ACCEPTED
```

## 5. Runtime and Persistence Isolation

The endpoint does not modify:

```text
Runtime state
OperatorResponse
SQLite schema
Runtime history
experimental record repository
inspection receipt boundary F
inspection batch manifest boundary G
```

Decision:

```text
Runtime isolation
= ACCEPTED

Persistence isolation
= ACCEPTED
```

## 6. Final Decision

```text
H3 optional comparison endpoint
= COMPLETE AT DESIGN / IMPLEMENTATION LEVEL

Manifest retrieval
= NOT INTRODUCED

Receipt retrieval
= NOT INTRODUCED

Semantic diffing
= NOT INTRODUCED

Authentication aggregation
= NOT INTRODUCED

Runtime integration
= NOT INTRODUCED

Canonical persistence
= NOT INTRODUCED

Public comparison retrieval
= NOT INTRODUCED

Critical design blocker
= NONE IDENTIFIED

GitHub Actions verification
= PENDING
```
