# 157. vNext Inspection Batch Manifest Minimal PoC

## 1. Purpose

This document records the isolated implementation of integration gate G:

```text
G1 manifest descriptor, settings, and digest policy
G2 manifest assembly service
G3 optional manifest creation endpoint
```

## 2. Added Components

```text
app/vnext/inspection_batch_manifest.py
app/vnext/inspection_batch_manifest_service.py
```

Tests:

```text
tests/vnext/test_inspection_batch_manifest_models.py
tests/vnext/test_inspection_batch_manifest_service.py
tests/vnext/test_inspection_batch_manifest_api.py
```

Updated route module:

```text
app/vnext/experimental_api_routes.py
```

Workflow:

```text
.github/workflows/priority-f-poc.yml
```

## 3. G1 Contract

Added closed frozen models for receipt references, batch requests, manifests, and results.

The manifest digest uses:

```text
SHA-256
JSON_SORTED_KEYS_UTF8_COMPACT_V1
```

The ordered receipt reference list is the digest input.

## 4. G2 Service

The assembly service validates:

```text
non-empty receipt reference set
unique receipt IDs
bounded receipt count
bounded identifiers and labels
bounded warning/source reference counts
bounded manifest metadata bytes
```

It preserves explicit receipt ordering and returns an immutable request-local manifest.

## 5. G3 Endpoint

Added:

```text
POST /vnext/experimental/inspection-batch-manifests
```

The endpoint returns one request-local manifest only.

It does not retrieve or persist receipts, retrieve source records, store manifests, aggregate authentication outcomes, or mutate Runtime.

## 6. Current Decision

```text
G1 models, settings, and digest policy
= IMPLEMENTED

G2 assembly service
= IMPLEMENTED

G3 optional creation endpoint
= IMPLEMENTED

Receipt persistence
= NOT IMPLEMENTED

Manifest persistence
= NOT IMPLEMENTED

Authentication aggregation
= NOT IMPLEMENTED

Runtime integration
= NOT IMPLEMENTED

GitHub Actions verification
= PENDING
```
