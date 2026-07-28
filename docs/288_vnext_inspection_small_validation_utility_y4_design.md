# 288. vNext Inspection Small Validation Utility Y4 Design

## 1. Scope

Y4 introduces one small pure validation utility for repeated canonical JSON UTF-8 byte measurement.

Approved target:

```text
canonical JSON serialization
UTF-8 encoding
encoded byte-length measurement
```

Initial consumers:

```text
ExperimentalComparisonRegisterComparisonLedgerService
ExperimentalComparisonLedgerComparisonArchiveService
```

## 2. Rationale

Both services currently repeat the same low-level operation:

```python
json.dumps(
    metadata,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

The serialization rule is mechanical and contract-neutral. The services must continue to own:

```text
field identity
configured limit
error class
error message
validation order
contract meaning
```

## 3. Approved Utility

Create:

```text
app/vnext/inspection_validation.py
```

Approved function:

```text
canonical_json_utf8_size(value) -> int
```

The function may only:

```text
serialize with ensure_ascii=False
sort keys
use compact separators
encode as UTF-8
return byte length
```

## 4. Prohibited Generalization

Y4 does not approve:

```text
generic identifier validator
generic reference validator
generic duplicate detector
generic settings model
generic manifest base model
generic inspection engine
shared contract error type
automatic field-name inference
automatic error-message construction
```

Identifier validation is not shared in Y4 because existing contracts differ on character length versus UTF-8 byte length and on empty-value handling.

## 5. Compatibility Requirements

The change must preserve:

```text
existing metadata limits
existing exception classes
existing exception messages
existing validation order
existing request and result models
existing endpoint behavior
```

## 6. Test Requirements

Add focused tests covering:

```text
stable compact canonical serialization size
UTF-8 multibyte size
mapping key-order independence
sequence support
```

Existing service and API tests remain the behavior-equivalence authority.

## 7. Boundary Decision

```text
Small canonical JSON byte-size utility
= APPROVED

Broader validation framework
= NOT APPROVED

Runtime or persistence changes
= NOT APPROVED
```
