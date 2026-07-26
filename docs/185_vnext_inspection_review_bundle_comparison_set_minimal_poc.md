# 185. vNext Inspection Review Bundle Comparison Set Minimal PoC

## 1. Purpose

Record the minimal implementation of integration gate K.

```text
J comparison references
+
explicit comparison-set request
↓
request-local comparison set manifest
```

## 2. Implemented Components

```text
app/vnext/inspection_review_bundle_comparison_set.py
app/vnext/inspection_review_bundle_comparison_set_service.py
POST /vnext/experimental/inspection-review-bundle-comparison-sets
```

Tests:

```text
tests/vnext/test_inspection_review_bundle_comparison_set_models.py
tests/vnext/test_inspection_review_bundle_comparison_set_service.py
tests/vnext/test_inspection_review_bundle_comparison_set_api.py
```

## 3. Set Contract

The request-local set manifest carries:

```text
comparison_set_id
ordered J comparison references
comparison_count
comparison_references_digest
digest algorithm
canonicalization profile
created_at
warnings
source_refs
metadata
```

It does not embed full J comparison reports or lower-layer records.

## 4. Digest Policy

```text
algorithm = SHA-256
canonicalization = JSON_SORTED_KEYS_UTF8_COMPACT_V1
input = ordered comparison-reference list
```

The digest is deterministic and order-sensitive.

## 5. Validation

The service validates:

```text
non-empty references
unique bundle_comparison_id
bounded comparison count
bounded identifiers
bounded warning/source reference counts
bounded canonical JSON metadata
supported digest policy
```

## 6. Endpoint

```text
POST /vnext/experimental/inspection-review-bundle-comparison-sets
```

The endpoint creates one request-local result only.

No retrieval, list, update, delete, repository, or export route exists.

## 7. Explicit Non-Goals

```text
J comparison retrieval
review bundle retrieval
semantic trend analysis
risk aggregation
authentication aggregation
OperatorResponse selection
Runtime integration
canonical persistence
```

## 8. Invariants

Unchanged:

```text
Structure → Slice → Stability
Gyro Logic → GyroOS → GyroAuth
/loop/step
ProcessExecutor
current SQLite schema
Runtime history
boundaries D-J
```

## 9. Verification State

```text
K1 models and digest policy
= IMPLEMENTED

K2 assembly service
= IMPLEMENTED

K3 optional endpoint
= IMPLEMENTED

Priority F workflow inclusion
= IMPLEMENTED

GitHub Actions verification
= PENDING
```
