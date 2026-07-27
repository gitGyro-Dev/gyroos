# 241. vNext Inspection Comparison Sequence Comparison Register Minimal PoC

## 1. Implemented Components

```text
app/vnext/inspection_comparison_sequence_comparison_register.py
app/vnext/inspection_comparison_sequence_comparison_register_service.py
app/vnext/experimental_api_routes.py
```

## 2. Test Components

```text
tests/vnext/test_inspection_comparison_sequence_comparison_register_models.py
tests/vnext/test_inspection_comparison_sequence_comparison_register_service.py
tests/vnext/test_inspection_comparison_sequence_comparison_register_api.py
```

## 3. Endpoint

```text
POST /vnext/experimental/inspection-comparison-sequence-comparison-registers
```

## 4. PoC Meaning

The PoC assembles an immutable request-local register from explicitly supplied R sequence-comparison references.

```text
comparison_register_created
≠ semantic trend established
≠ risk level established
≠ authentication state aggregated
≠ Runtime continuation approved
≠ canonical history created
```

## 5. Approved Digest Policy

```text
SHA-256
JSON_SORTED_KEYS_UTF8_COMPACT_V1
ordered R comparison-reference list
```

## 6. Excluded Scope

```text
R comparison retrieval
Q sequence retrieval
semantic trend analysis
risk aggregation
authentication aggregation
Runtime integration
canonical persistence
public register retrieval
```

## 7. Verification State

```text
Design = COMPLETE
Implementation = COMPLETE
Tests added = COMPLETE
Workflow inclusion = COMPLETE
GitHub Actions verification = PENDING
```
