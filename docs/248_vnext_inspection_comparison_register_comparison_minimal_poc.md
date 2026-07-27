# 248. vNext Inspection Comparison Register Comparison Minimal PoC

## 1. Purpose

This PoC records the minimal T implementation for request-local comparison of two S comparison register references.

## 2. Input

```text
register comparison ID
left comparison register reference
right comparison register reference
warnings
metadata
```

Each register reference carries only:

```text
comparison register ID
ordered sequence-comparison IDs
optional declared register digest
```

## 3. Output

```text
comparison_register_comparison_created = true
comparison register comparison report
```

The report includes:

```text
added sequence-comparison IDs
removed sequence-comparison IDs
retained sequence-comparison IDs
left/right declared register digests
digest_changed
created_at
warnings
metadata
```

## 4. Ordering

```text
added = right-side order
removed = left-side order
retained = left-side order
```

## 5. Boundaries

```text
comparison_register_comparison_created
≠ semantic trend established
≠ risk change classified
≠ authentication state changed
≠ Runtime continuation changed
≠ canonical history created
```

No register retrieval, R comparison retrieval, semantic analysis, risk aggregation, authentication aggregation, Runtime integration, or canonical persistence is introduced.

## 6. Endpoint

```text
POST /vnext/experimental/inspection-comparison-register-comparisons
```

The endpoint is creation-only and request-local.

## 7. Verification State

```text
T1 models and settings
= IMPLEMENTED

T2 comparison service
= IMPLEMENTED

T3 optional endpoint
= IMPLEMENTED

Priority F workflow inclusion
= IMPLEMENTED

GitHub Actions verification
= PENDING
```
