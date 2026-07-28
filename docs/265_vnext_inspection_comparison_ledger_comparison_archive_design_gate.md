# 265. vNext Inspection Comparison Ledger Comparison Archive Design Gate

## 1. Purpose

Integration gate W defines a bounded request-local manifest for grouping multiple V inspection comparison-ledger comparison reports by explicit reference.

```text
comparison-ledger comparison references
+
explicit comparison-archive request
↓
inspection comparison-ledger comparison archive manifest
```

The manifest records that several request-local V comparison reports were grouped for one explicit inspection operation.

It does not retrieve reports implicitly, infer semantic trends, classify or aggregate risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison archive should carry explicit references only:

```text
comparison archive ID
ledger-comparison references
left/right comparison ledger IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The archive must not embed full V comparison reports, U ledger manifests, T comparison reports, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonLedgerComparisonArchiveSettings
ExperimentalComparisonLedgerComparisonArchiveDigestPolicy
ExperimentalComparisonLedgerComparisonReference
ExperimentalComparisonLedgerComparisonArchiveRequest
ExperimentalComparisonLedgerComparisonArchiveManifest
ExperimentalComparisonLedgerComparisonArchiveResult
```

Suggested result meaning:

```text
comparison_archive_created
```

This means only that a bounded request-local reference archive was assembled.

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
ExperimentalComparisonLedgerComparisonArchiveService
```

Initial operation:

```text
create_archive(request)
→ ExperimentalComparisonLedgerComparisonArchiveResult
```

Responsibilities:

```text
validate explicit archive identity
validate ledger-comparison reference uniqueness
validate bounded reference count
copy explicit ledger and ledger-comparison references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local archive manifest
```

Non-responsibilities:

```text
retrieve V comparison reports implicitly
retrieve U ledger manifests implicitly
retrieve T comparison reports or lower-level inspection records implicitly
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

A V comparison reference may carry only bounded labels such as:

```text
ledger_comparison_id
left_comparison_ledger_id
right_comparison_ledger_id
added_count
removed_count
retained_count
digest_changed
```

The archive must not override or reinterpret any comparison result.

```text
comparison archive grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial archive may record a deterministic digest over the ordered V comparison-reference list.

The proposed initial profile is:

```text
algorithm = SHA-256
canonicalization = JSON_SORTED_KEYS_UTF8_COMPACT_V1
input = ordered V comparison-reference list
```

Final approval of this profile is deferred to W1 review.

The archive digest must not be presented as proof of semantic validity, security meaning, authenticity, completeness, chronology, or causal order.

## 7. Error Boundary

Distinguish:

```text
duplicate ledger-comparison reference
missing ledger-comparison identity
reference count exceeded
invalid archive ID
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
inspection comparison-register comparison ledger boundary U
inspection comparison ledger comparison boundary V
```

Initial W comparison archives remain request-local and non-canonical.

Archive repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial W scope.

## 9. Proposed Sequence

```text
W1. comparison archive descriptor, settings, and digest policy
↓
Review
↓
W2. comparison archive assembly service
↓
Review
↓
W3. optional comparison archive creation endpoint
↓
Actions verification
↓
W Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, series comparisons, comparison collections, collection comparisons, comparison sequences, sequence comparisons, comparison registers, register comparisons, comparison ledgers, ledger comparisons, or Runtime state.

## 10. Final Design Decision

```text
W inspection comparison-ledger comparison archive design gate
= COMPLETE

Initial archive meaning
= REQUEST-LOCAL V COMPARISON REFERENCE GROUPING ONLY

V comparison retrieval
= NOT APPROVED

U ledger retrieval
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
W1. comparison archive descriptor, settings, and digest policy
```