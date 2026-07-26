# 150. vNext Inspection Receipt Minimal PoC

## 1. Purpose

This document records the isolated implementation of integration gate F:

```text
F1 receipt descriptor, settings, and digest policy
F2 receipt assembly service
F3 optional receipt creation endpoint
```

## 2. Added Components

```text
app/vnext/inspection_receipt.py
app/vnext/inspection_receipt_service.py
```

Tests:

```text
tests/vnext/test_inspection_receipt_models.py
tests/vnext/test_inspection_receipt_service.py
tests/vnext/test_inspection_receipt_api.py
```

Endpoint:

```text
POST /vnext/experimental/inspection-receipts
```

## 3. Digest Policy

```text
algorithm = SHA-256
canonicalization = JSON_SORTED_KEYS_UTF8_COMPACT_V1
```

Payload and source metadata are used only to compute deterministic digests.

## 4. Receipt Meaning

```text
receipt_created
= request-local receipt assembled
```

It does not mean:

```text
record accepted as truth
semantic equivalence
compatible_for_inspection
authentication accepted
Runtime continuation approved
canonical persistence
```

## 5. Incompatible Attempt Policy

The initial policy permits request-local audit receipts for incompatible inspection attempts.

The supplied compatibility result is preserved without reinterpretation.

## 6. Runtime and Persistence Isolation

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
```

No receipt repository or public receipt retrieval is introduced.

## 7. Current Decision

```text
F1 models, settings, and digest policy
= IMPLEMENTED

F2 receipt assembly service
= IMPLEMENTED

F3 optional receipt endpoint
= IMPLEMENTED

Typed reconstruction
= NOT IMPLEMENTED

Authentication mapping
= NOT IMPLEMENTED

Runtime integration
= NOT IMPLEMENTED

Canonical persistence
= NOT IMPLEMENTED

Public receipt retrieval
= NOT IMPLEMENTED

GitHub Actions verification
= PENDING
```
