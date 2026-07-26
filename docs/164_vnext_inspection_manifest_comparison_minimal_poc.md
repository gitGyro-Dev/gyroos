# 164. vNext Inspection Manifest Comparison Minimal PoC

## 1. Purpose

This document records integration gate H:

```text
H1 comparison descriptor and settings
H2 comparison service
H3 optional comparison endpoint
```

The implementation compares two explicit inspection batch manifest references at receipt-membership level only.

## 2. Added Components

```text
app/vnext/inspection_manifest_comparison.py
app/vnext/inspection_manifest_comparison_service.py
```

Tests:

```text
tests/vnext/test_inspection_manifest_comparison_models.py
tests/vnext/test_inspection_manifest_comparison_service.py
tests/vnext/test_inspection_manifest_comparison_api.py
```

Endpoint:

```text
POST /vnext/experimental/inspection-manifest-comparisons
```

## 3. Initial Comparison Fields

```text
comparison ID
left manifest ID
right manifest ID
added receipt IDs
removed receipt IDs
retained receipt IDs
left manifest digest
right manifest digest
digest_changed
warnings
metadata
```

## 4. Ordering Policy

```text
added receipt IDs
= right-side order

removed receipt IDs
= left-side order

retained receipt IDs
= left-side order
```

## 5. Digest Policy

```text
digest_changed
= declared left digest != declared right digest
```

If either digest is absent:

```text
digest_changed = null
```

No digest recomputation or source-content verification is performed.

## 6. Meaning Boundary

```text
comparison_report_created
≠ semantic change established
≠ security impact classified
≠ authentication state changed
≠ Runtime continuation changed
≠ canonical history created
```

```text
manifest reference difference
≠ Runtime DifferenceObject
≠ semantic change
≠ security risk
```

## 7. Existing Runtime Isolation

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
SQLite schema
Runtime history
experimental record CRUD
consumer boundary D
compatibility boundary E
inspection receipt boundary F
inspection batch manifest boundary G
```

## 8. Current Decision

```text
H1 models and settings
= IMPLEMENTED

H2 comparison service
= IMPLEMENTED

H3 optional endpoint
= IMPLEMENTED

Manifest retrieval
= NOT IMPLEMENTED

Receipt retrieval
= NOT IMPLEMENTED

Semantic diffing
= NOT IMPLEMENTED

Authentication aggregation
= NOT IMPLEMENTED

Runtime integration
= NOT IMPLEMENTED

Canonical persistence
= NOT IMPLEMENTED

GitHub Actions verification
= PENDING
```
