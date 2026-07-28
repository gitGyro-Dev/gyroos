# 275. vNext Inspection Shared-Abstraction Review

## 1. Scope

This document is the X3 deliverable for integration gate X.

It reviews repeated validation, digest, model, service, API-error, and test patterns across the inspection contracts from F through W.

This review does not change implementation, rename contracts, alter endpoints, modify Runtime behavior, add persistence, or approve a universal generic inspection framework.

## 2. Review Principle

Use the smallest reusable unit that removes mechanical duplication without weakening contract-specific types, limits, ordering rules, errors, or meaning boundaries.

```text
small helper
> reusable mixin
> generic base model
> universal framework
```

The preferred direction is the left side of this scale.

## 3. Repeated Patterns Found

The following patterns repeat across several grouping-manifest and comparison services.

```text
identifier length validation
reference-count validation
duplicate-reference detection
warning count validation
source-reference count validation
metadata JSON byte validation
ordered canonical JSON encoding
SHA-256 digest calculation
request-local immutable result creation
experimental API error translation
model/service/API test structure
```

The repetition is real, but not every repeated block has the same contract meaning.

## 4. Safe Shared Helpers

The following small pure helpers are suitable candidates for future implementation.

### 4.1 Canonical JSON byte encoding

```text
input: JSON-compatible value
output: UTF-8 bytes
policy: sorted keys, compact separators, ensure_ascii=False
```

This helper may support metadata-size checks and ordered digest input generation.

It must not decide which fields belong in a digest.

Decision:

```text
shared canonical JSON encoder
= APPROVED AS A CANDIDATE
```

### 4.2 Metadata byte validation

```text
validate_json_byte_limit(value, maximum, field_name, error_factory)
```

The helper may compute encoded byte size and raise a caller-supplied contract-specific error.

Decision:

```text
shared metadata byte validator
= APPROVED AS A CANDIDATE
```

### 4.3 Bounded string-list validation

```text
validate_bounded_strings(values, maximum_count, maximum_length, field_name, error_factory)
```

This may support warnings and source references.

The caller must retain the contract-specific field names, limits, and error class.

Decision:

```text
shared bounded string validator
= APPROVED AS A CANDIDATE
```

### 4.4 Unique explicit-reference validation

```text
validate_unique_reference_keys(references, key, error_factory)
```

The helper may detect duplicate explicit reference identifiers.

It must not infer identity from payload contents or compare semantic equality.

Decision:

```text
shared duplicate-key validator
= APPROVED AS A CANDIDATE
```

### 4.5 Reference-count validation

```text
validate_reference_count(references, maximum, error_factory)
```

The helper may enforce a configured upper bound.

Non-empty requirements should remain in the contract model or contract-specific service when their meaning differs.

Decision:

```text
shared reference-count validator
= APPROVED AS A CANDIDATE
```

## 5. Contract-Specific Logic That Must Remain Local

The following must remain inside each contract or its dedicated policy object.

```text
reference model type
reference identifier fields
left/right identifier meaning
ordered versus unordered semantics
digest input field selection
digest policy identity
result label
manifest/report type
settings field names and limits
contract-specific error classes
endpoint error code
endpoint phase
creation method name
meaning boundary
```

Decision:

```text
contract-specific assembly and semantics
= MUST REMAIN LOCAL
```

## 6. Generic Base Models

A shared Pydantic base model for all inspection manifests is not approved.

Reason:

```text
fields differ across contracts
reference types differ
result structures differ
digest fields differ
created_at ownership differs
metadata field names differ
inheritance would hide contract boundaries
future changes could couple unrelated contracts
```

The existing repeated declaration:

```python
model_config = ConfigDict(extra="forbid", frozen=True)
```

is small and explicit. Removing this duplication does not justify a common inheritance hierarchy.

Decision:

```text
universal inspection base model
= NOT APPROVED
```

## 7. Generic Service Framework

A universal grouping/comparison service is not approved.

A generic engine would require callbacks or configuration for:

```text
identifier extraction
reference validation
result construction
digest construction
error mapping
contract labels
limits
```

That configuration would become another hidden contract language and make local behavior harder to audit.

Decision:

```text
universal manifest/comparison service
= NOT APPROVED
```

## 8. Digest Abstraction

Only canonical encoding and raw SHA-256 calculation may be shared.

Each contract must continue to declare:

```text
algorithm
canonicalization identifier
ordered input structure
included fields
policy validation
output digest field
```

Decision:

```text
shared digest primitives
= APPROVED AS CANDIDATES

shared universal digest policy
= NOT APPROVED
```

## 9. API Error Translation

The existing `experimental_error(...)` response builder is an appropriate shared boundary.

The following must remain explicit at each endpoint:

```text
HTTP status
error code
message
category
phase
contract-specific exception type
```

A registry that automatically derives endpoint errors from class names is not approved because it could hide incorrect mappings.

Decision:

```text
shared response builder
= ALREADY ACCEPTABLE

automatic error registry or inference
= NOT APPROVED
```

## 10. Test Abstraction

Small test helpers or fixtures may be introduced later for:

```text
asserting closed frozen models
asserting absence of Runtime/authentication/semantic fields
resetting shared rate-limit state
building repeated metadata payloads
checking no GET/PUT/PATCH/DELETE route exists
```

Parameterized tests may be used only when each contract remains visible in the test case identifiers and failures identify the exact contract.

A single generic test suite replacing contract-specific model, service, and API tests is not approved.

Decision:

```text
small test helpers and explicit parametrization
= APPROVED AS CANDIDATES

replacement of contract-specific tests
= NOT APPROVED
```

## 11. Preferred Minimal Module

If implementation is later approved, use one small internal utility module such as:

```text
app/vnext/inspection_contract_utils.py
```

Initial scope should be limited to pure functions for:

```text
canonical JSON bytes
metadata byte limits
bounded string lists
reference count
unique reference keys
```

The module must not contain:

```text
Pydantic contract models
contract settings
manifest/report construction
semantic classification
Runtime integration
persistence
repository access
endpoint routing
error-code inference
```

## 12. Implementation Order

No implementation change is authorized by this document alone.

If implementation is approved later, proceed incrementally:

```text
1. add utility module and direct unit tests
2. migrate one low-risk contract
3. run its full model/service/API tests
4. compare behavior and error identity
5. review before migrating another contract
```

Do not migrate all contracts in one change.

## 13. Final Decision

```text
X3 shared-abstraction review
= COMPLETE

Small pure validation helpers
= APPROVED AS CANDIDATES

Canonical JSON encoding helper
= APPROVED AS A CANDIDATE

Raw digest primitive sharing
= APPROVED AS A CANDIDATE

Contract-specific types and assembly
= MUST REMAIN LOCAL

Universal inspection base model
= NOT APPROVED

Universal manifest/comparison service
= NOT APPROVED

Automatic endpoint error inference
= NOT APPROVED

Replacement of contract-specific tests
= NOT APPROVED

Immediate refactoring
= NOT YET APPROVED

Runtime and persistence boundaries
= UNCHANGED
```

## 14. Next Step

```text
X4: Review experimental router growth and Priority F workflow growth.
```

X4 should prefer explicit, auditable organization over dynamic route or test discovery.