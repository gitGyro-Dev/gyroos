# 258. vNext Inspection Comparison Ledger Comparison Design Gate

## 1. Purpose

Integration gate V defines a bounded request-local comparison report between two U inspection comparison-register comparison ledger manifests.

```text
left comparison ledger reference
+
right comparison ledger reference
+
explicit comparison request
↓
inspection comparison ledger comparison report
```

The comparison reports reference-level additions, removals, retained T comparison references, and declared ledger digest changes.

It does not retrieve ledgers implicitly, reconstruct T comparison reports, infer semantic trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
ledger comparison ID
left comparison ledger descriptor
right comparison ledger descriptor
added register-comparison IDs
removed register-comparison IDs
retained register-comparison IDs
left ledger digest
right ledger digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full U ledger manifests, T comparison reports, S register manifests, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonLedgerComparisonSettings
ExperimentalComparisonLedgerReference
ExperimentalComparisonLedgerComparisonRequest
ExperimentalComparisonLedgerComparisonReport
ExperimentalComparisonLedgerComparisonResult
```

Suggested result meaning:

```text
comparison_ledger_comparison_created
```

This means only that a bounded request-local reference comparison was assembled.

It does not mean:

```text
semantic trend was established
risk change was classified
authentication state changed
Runtime continuation changed
canonical history was created
```

## 4. Comparison Boundary

Proposed service:

```text
ExperimentalComparisonLedgerComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalComparisonLedgerComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right comparison ledger references
validate bounded register-comparison reference counts
compute added register-comparison IDs
compute removed register-comparison IDs
compute retained register-comparison IDs
compare declared ledger digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve U ledger manifests implicitly
retrieve T comparison reports implicitly
retrieve S register manifests or lower-level inspection records implicitly
verify declared digests against source content
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Difference Meaning Boundary

The initial report distinguishes only reference membership and declared digest equality.

```text
added register-comparison ID
removed register-comparison ID
retained register-comparison ID
digest_changed
```

These values must not be mapped automatically to semantic trend, security risk, authentication change, Runtime DifferenceObject, or BoundaryEvaluation.

```text
comparison ledger reference difference
≠ semantic trend
≠ risk change
≠ Runtime DifferenceObject
≠ authentication state change
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left ledger digest != right ledger digest
```

This does not establish what underlying comparison content changed, whether the change is valid, whether ledger order is chronologically meaningful, or whether semantic meaning changed.

No source retrieval or digest recomputation is approved in the initial V scope.

## 7. Error Boundary

Distinguish:

```text
same comparison ledger used on both sides
missing comparison ledger identity
duplicate register-comparison reference within a side
reference count exceeded
invalid ledger comparison ID
resource limit exceeded
invalid digest label
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
inspection comparison-register comparison ledger boundary U
```

Initial V comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial V scope.

## 9. Proposed Sequence

```text
V1. comparison descriptor and settings
↓
Review
↓
V2. comparison service
↓
Review
↓
V3. optional comparison endpoint
↓
Actions verification
↓
V Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, series comparisons, comparison collections, collection comparisons, comparison sequences, sequence comparisons, comparison registers, register comparisons, comparison ledgers, or Runtime state.

## 10. Final Design Decision

```text
V inspection comparison ledger comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL COMPARISON LEDGER REFERENCE COMPARISON ONLY

Comparison ledger retrieval
= NOT APPROVED

T comparison retrieval
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
V1. comparison descriptor and settings
```
