# 171. vNext Inspection Comparison Review Bundle Minimal PoC

## 1. Purpose

This PoC implements integration gate I for bounded request-local grouping of explicit inspection manifest comparison references.

## 2. Implemented Components

```text
app/vnext/inspection_comparison_review_bundle.py
app/vnext/inspection_comparison_review_bundle_service.py
app/vnext/experimental_api_routes.py
```

Tests:

```text
tests/vnext/test_inspection_comparison_review_bundle_models.py
tests/vnext/test_inspection_comparison_review_bundle_service.py
tests/vnext/test_inspection_comparison_review_bundle_api.py
```

## 3. Endpoint

```text
POST /vnext/experimental/inspection-comparison-review-bundles
```

The endpoint returns one request-local bundle and does not persist it.

## 4. Digest Policy

```text
algorithm = SHA-256
canonicalization = JSON_SORTED_KEYS_UTF8_COMPACT_V1
input = ordered comparison-reference list
```

## 5. Boundary Preservation

Not introduced:

```text
comparison report retrieval
manifest retrieval
receipt retrieval
semantic trend analysis
risk aggregation
authentication aggregation
OperatorResponse selection
Runtime mutation
canonical persistence
public review bundle retrieval
```

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
current SQLite schema
Runtime history
experimental record CRUD
```

## 6. Workflow

The Priority F workflow includes all I1-I3 tests while preserving existing regression tests and PoC artifact generation.

## 7. Current State

```text
I1 models and digest policy
= IMPLEMENTED

I2 assembly service
= IMPLEMENTED

I3 optional endpoint
= IMPLEMENTED

GitHub Actions verification
= PENDING
```
