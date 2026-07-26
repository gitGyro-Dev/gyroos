# 143. vNext Consumer Compatibility Minimal PoC

## 1. Purpose

This document records the isolated implementation of integration gate E:

```text
E1 contract descriptor and settings
E2 compatibility policy and service
E3 optional compatibility endpoint
```

## 2. Added Components

```text
app/vnext/consumer_compatibility.py
app/vnext/consumer_compatibility_service.py
```

Updated:

```text
app/vnext/experimental_api_routes.py
```

Tests:

```text
tests/vnext/test_consumer_compatibility_models.py
tests/vnext/test_consumer_compatibility_service.py
tests/vnext/test_consumer_compatibility_api.py
```

## 3. Compatibility Meaning

The implementation produces only:

```text
compatible_for_inspection
```

It does not establish authentication compatibility, semantic equivalence, migration approval, or canonical authority.

## 4. Initial Version Policy

```text
exact major compatibility required
minor mismatch = warning
patch mismatch = warning
unknown/invalid version = explicit validation failure
```

No automatic migration or fallback reinterpretation is performed.

## 5. Record Type Boundary

`record_type` remains an opaque label. The policy may compare it with an expected label, but does not reconstruct typed vNext models.

## 6. Optional Endpoint

```text
POST /vnext/experimental/compatibility/check
```

The endpoint is request-local and does not read or write the experimental repository.

## 7. Preserved Boundaries

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
consumer inspection boundary D
```

## 8. Current Decision

```text
E1 descriptor and settings
= IMPLEMENTED

E2 policy and service
= IMPLEMENTED

E3 optional endpoint
= IMPLEMENTED

Automatic migration
= NOT IMPLEMENTED

Typed reconstruction
= NOT IMPLEMENTED

Authentication mapping
= NOT IMPLEMENTED

Canonical persistence
= NOT IMPLEMENTED

GitHub Actions verification
= PENDING
```
