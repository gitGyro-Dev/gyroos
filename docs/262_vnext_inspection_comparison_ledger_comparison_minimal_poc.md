# 262. vNext Inspection Comparison Ledger Comparison Minimal PoC

## 1. Purpose

This record captures the minimal V implementation for comparing two explicit U comparison-ledger references without retrieval, persistence, semantic inference, risk classification, authentication aggregation, or Runtime integration.

## 2. Implemented Flow

```text
left comparison ledger reference
+
right comparison ledger reference
+
explicit comparison request
↓
request-local comparison ledger comparison report
```

## 3. Implemented Components

```text
app/vnext/inspection_comparison_ledger_comparison.py
app/vnext/inspection_comparison_ledger_comparison_service.py
app/vnext/experimental_api_routes.py
```

Tests:

```text
tests/vnext/test_inspection_comparison_ledger_comparison_models.py
tests/vnext/test_inspection_comparison_ledger_comparison_service.py
tests/vnext/test_inspection_comparison_ledger_comparison_api.py
```

## 4. Comparison Output

The implementation records only:

```text
ledger comparison ID
left comparison ledger ID
right comparison ledger ID
added register-comparison IDs
removed register-comparison IDs
retained register-comparison IDs
left declared ledger digest
right declared ledger digest
digest_changed
created_at
warnings
metadata
```

## 5. Ordering Policy

```text
added = right-side request order
removed = left-side request order
retained = left-side request order
```

## 6. Digest Boundary

```text
digest_changed
= comparison of declared ledger digest labels only
```

No source retrieval, canonicalization, digest recomputation, authenticity verification, chronology verification, or semantic interpretation occurs.

## 7. Endpoint

```text
POST /vnext/experimental/inspection-comparison-ledger-comparisons
```

The endpoint returns one request-local report only.

No retrieval, listing, update, deletion, repository, or export route is introduced.

## 8. Meaning Boundary

```text
comparison_ledger_comparison_created
≠ semantic trend established
≠ risk change classified
≠ authentication state changed
≠ Runtime continuation changed
≠ canonical history created
```

## 9. Unchanged Runtime Boundary

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
Runtime history
SQLite schema
experimental record CRUD
```

## 10. Verification State

```text
V1 models and settings
= IMPLEMENTED

V2 comparison service
= IMPLEMENTED

V3 optional endpoint
= IMPLEMENTED

Priority F workflow inclusion
= IMPLEMENTED

GitHub Actions verification
= PENDING
```
