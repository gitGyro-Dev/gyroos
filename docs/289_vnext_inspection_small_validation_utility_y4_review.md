# 289. vNext Inspection Small Validation Utility Y4 Review

## 1. Scope

Reviewed implementation:

```text
app/vnext/inspection_validation.py
app/vnext/inspection_comparison_register_comparison_ledger_service.py
app/vnext/inspection_comparison_ledger_comparison_archive_service.py
tests/vnext/test_inspection_validation.py
tests/test_groups/vnext_inspection.txt
```

Y4 extracts one repeated, contract-neutral operation: compact, key-sorted JSON serialization followed by UTF-8 byte-length measurement.

## 2. Utility Boundary

Added utility:

```text
canonical_json_utf8_size(value) -> int
```

The utility performs only:

```text
json.dumps with ensure_ascii=False
sort_keys=True
compact separators
UTF-8 encoding
byte-length return
```

Decision:

```text
Small pure validation utility
= ACCEPTED
```

## 3. Service Integration

Integrated consumers:

```text
ExperimentalComparisonRegisterComparisonLedgerService
ExperimentalComparisonLedgerComparisonArchiveService
```

The services continue to own:

```text
metadata field identity
configured byte limit
exception class
exception message
validation order
contract meaning
```

Decision:

```text
Contract-specific validation ownership
= PRESERVED
```

## 4. Compatibility Review

Unchanged:

```text
metadata serialization policy
metadata byte limits
exception identities
exception messages
request models
result models
endpoint behavior
```

Identifier validation was intentionally not generalized because existing contracts differ in character-count versus UTF-8 byte-count behavior and empty-value handling.

Decision:

```text
Behavior compatibility
= PRESERVED AT IMPLEMENTATION REVIEW LEVEL
```

## 5. Test Coverage

Added focused tests for:

```text
compact sorted JSON size
multibyte UTF-8 size
mapping order independence
sequence support
```

The new test file is included in the checked-in `vnext_inspection.txt` Priority F group.

Decision:

```text
Utility unit-test coverage
= ADDED

Workflow coverage
= UPDATED
```

## 6. Prohibited Generalization

Y4 does not introduce:

```text
generic identifier validation
generic duplicate validation
generic reference validation
generic settings models
generic manifest base models
generic inspection engine
shared contract error classes
automatic error construction
```

Decision:

```text
Universal validation framework
= NOT INTRODUCED
```

## 7. Runtime and Layer Isolation

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
inspection endpoint contracts
Gyro Logic → GyroOS → GyroAuth dependency direction
```

Decision:

```text
Runtime isolation
= VERIFIED AT IMPLEMENTATION REVIEW LEVEL

Layer isolation
= VERIFIED AT IMPLEMENTATION REVIEW LEVEL
```

## 8. Current Verification State

```text
Y4 design
= COMPLETE

Small validation utility
= IMPLEMENTED

Ledger service integration
= IMPLEMENTED

Archive service integration
= IMPLEMENTED

Focused tests
= IMPLEMENTED

Checked-in workflow coverage
= UPDATED

GitHub Actions verification
= PENDING

Y4
= COMPLETE AT IMPLEMENTATION / REVIEW LEVEL
```

## 9. Next Step

```text
Confirm the Priority F GitHub Actions run produced by Y4.
If successful, update Y4 to VERIFIED and proceed to Y Overall Review.
```
