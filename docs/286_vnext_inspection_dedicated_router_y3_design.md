# 286. vNext Inspection Dedicated Router Y3 Design

## 1. Scope

Y3 extracts the existing Inspection POST routes from `experimental_api_routes.py` into one dedicated router module.

## 2. Target Structure

```text
experimental_api_routes.py
  ├─ experimental record CRUD
  ├─ compatibility check
  └─ include inspection router

inspection_api_routes.py
  └─ Inspection POST endpoints F-W
```

## 3. Invariants

The following must remain unchanged:

```text
/vnext/experimental prefix
all F-W endpoint paths
request and response models
HTTP status codes
error codes and phases
bearer dependency
service behavior
request-local and non-canonical contract meaning
```

## 4. Non-Goals

Y3 does not authorize:

```text
endpoint rename
new route
GET inspection route
repository storage
public retrieval
dynamic route registration
contract-specific subrouters
Runtime mutation
canonical persistence
```

## 5. Implementation Decision

Use one `inspection_router` with no prefix and include it in the existing experimental router.

The parent router continues to own:

```text
prefix=/vnext/experimental
bearer dependency
vNext Experimental tag
```

This avoids duplicated prefixes and dependencies.

## 6. Verification

Required verification:

```text
all existing Inspection API tests pass
experimental API route tests pass
no duplicate paths
no missing F-W POST endpoint
Priority F workflow succeeds
```

## 7. Decision

```text
Dedicated Inspection router
= APPROVED

One router for F-W
= REQUIRED

Contract-per-router structure
= NOT APPROVED

Y3 implementation
= AUTHORIZED
```
