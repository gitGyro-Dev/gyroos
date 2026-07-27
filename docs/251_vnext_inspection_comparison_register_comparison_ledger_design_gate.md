# 251. vNext Inspection Comparison Register Comparison Ledger Design Gate

## 1. Purpose

Integration gate U defines a bounded request-local manifest for grouping multiple T inspection comparison-register comparison reports by explicit reference.

```text
comparison-register comparison references
+
explicit comparison-ledger request
↓
inspection comparison-register comparison ledger manifest
```

The manifest records that several request-local T comparison reports were grouped for one explicit inspection operation.

It does not retrieve reports implicitly, infer semantic trends, classify or aggregate risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison ledger should carry explicit references only:

```text
comparison ledger ID
register-comparison references
left/right comparison register IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The ledger must not embed full T comparison reports, S register manifests, R comparison reports, Q sequence manifests, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonRegisterComparisonLedgerSettings
ExperimentalComparisonRegisterComparisonReference
ExperimentalComparisonRegisterComparisonLedgerRequest
ExperimentalComparisonRegisterComparisonLedgerManifest
ExperimentalComparisonRegisterComparisonLedgerResult
```

Suggested result meaning:

```text
comparison_ledger_created
```

This means only that a bounded request-local reference ledger was assembled.

It does not mean:

```text
semantic trend established
risk level established
authentication state aggregated
Runtime continuation approved
canonical history created
```

## 4. Assembly Boundary

Proposed service:

```text
ExperimentalComparisonRegisterComparisonLedgerService
```

Initial operation:

```text
create_ledger(request)
→ ExperimentalComparisonRegisterComparisonLedgerResult
```

Responsibilities:

```text
validate explicit ledger identity
validate register-comparison reference uniqueness
validate bounded reference count
copy explicit register and register-comparison references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local ledger manifest
```

Non-responsibilities:

```text
retrieve T comparison reports implicitly
retrieve S register manifests implicitly
retrieve R comparison reports or lower-level inspection records implicitly
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

A T comparison reference may carry only bounded labels such as:

```text
register_comparison_id
left_comparison_register_id
right_comparison_register_id
added_count
removed_count
retained_count
digest_changed
```

The ledger must not override or reinterpret any comparison result.

```text
comparison ledger grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial ledger may optionally record a deterministic digest over the ordered T comparison-reference list.

No digest algorithm or canonicalization profile is approved until U1 review.

The ledger digest must not be presented as proof of semantic validity, security meaning, authenticity, completeness, chronology, or causal order.

## 7. Error Boundary

Distinguish:

```text
duplicate register-comparison reference
missing register-comparison identity
reference count exceeded
invalid ledger ID
unsupported digest policy
resource limit exceeded
```

These errors must not become:

```text
AUTH_FAIL
REAUTH_REQUIRED
identity break
trajectory break
attack classification
OperatorResponse
```

## 8. Runtime and Persistence Boundary

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
inspection receipt boundary F
inspection batch manifest boundary G
inspection manifest comparison boundary H
inspection comparison review bundle boundary I
inspection review bundle comparison boundary J
inspection review bundle comparison set boundary K
inspection review bundle comparison set comparison boundary L
inspection comparison-set comparison series boundary M
inspection comparison series comparison boundary N
inspection comparison-series comparison collection boundary O
inspection comparison collection comparison boundary P
inspection comparison-collection comparison sequence boundary Q
inspection comparison sequence comparison boundary R
inspection comparison-sequence comparison register boundary S
inspection comparison register comparison boundary T
```

Initial U comparison ledgers remain request-local and non-canonical.

Ledger repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial U scope.

## 9. Proposed Sequence

```text
U1. comparison ledger descriptor, settings, and digest policy
↓
Review
↓
U2. comparison ledger assembly service
↓
Review
↓
U3. optional comparison ledger creation endpoint
↓
Actions verification
↓
U Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, series comparisons, comparison collections, collection comparisons, comparison sequences, sequence comparisons, comparison registers, register comparisons, or Runtime state.

## 10. Final Design Decision

```text
U inspection comparison-register comparison ledger design gate
= COMPLETE

Initial ledger meaning
= REQUEST-LOCAL T COMPARISON REFERENCE GROUPING ONLY

T comparison retrieval
= NOT APPROVED

S register retrieval
= NOT APPROVED

Semantic trend analysis
= NOT APPROVED

Risk aggregation
= NOT APPROVED

Authentication aggregation
= NOT APPROVED

Runtime integration
= NOT APPROVED

Canonical persistence
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```

Proceed next to:

```text
U1. comparison ledger descriptor, settings, and digest policy
```