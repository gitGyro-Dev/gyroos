# 255. vNext Inspection Comparison Register Comparison Ledger Minimal PoC

## 1. Purpose

This minimal PoC implements integration gate U as a bounded request-local ledger for explicit T comparison references.

## 2. Implemented Files

```text
app/vnext/inspection_comparison_register_comparison_ledger.py
app/vnext/inspection_comparison_register_comparison_ledger_service.py
tests/vnext/test_inspection_comparison_register_comparison_ledger_models.py
tests/vnext/test_inspection_comparison_register_comparison_ledger_service.py
tests/vnext/test_inspection_comparison_register_comparison_ledger_api.py
```

## 3. Implemented Endpoint

```text
POST /vnext/experimental/inspection-comparison-register-comparison-ledgers
```

The endpoint returns one request-local manifest only.

## 4. Implemented Boundaries

```text
explicit ledger identity
explicit T comparison references
unique register_comparison_id values
bounded reference count
bounded identifier bytes
bounded warnings and source refs
bounded metadata bytes
request-order preservation
SHA-256 ordered-reference digest
```

## 5. Meaning Boundary

```text
comparison_ledger_created
≠ semantic trend established
≠ risk level established
≠ authentication state aggregated
≠ Runtime continuation approved
≠ canonical history created
```

## 6. Non-Implemented Capabilities

```text
T comparison retrieval
S register retrieval
semantic trend analysis
risk aggregation
authentication aggregation
Runtime integration
canonical persistence
public ledger retrieval
ledger export
```

## 7. Workflow

The Priority F workflow includes all U1-U3 model, service, and API tests while preserving the existing regression suite and PoC artifact steps.
