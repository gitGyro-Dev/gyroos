# 202. vNext Inspection Comparison Series Comparison Design Gate

## 1. Purpose

Integration gate N defines a bounded request-local comparison report between two M inspection comparison-set comparison series manifests.

```text
left comparison series reference
+
right comparison series reference
+
explicit comparison request
↓
inspection comparison series comparison report
```

The comparison reports reference-level additions, removals, retained L comparison references, and declared series digest changes.

It does not retrieve series implicitly, reconstruct L comparison reports, infer semantic trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
series comparison ID
left comparison series descriptor
right comparison series descriptor
added set-comparison IDs
removed set-comparison IDs
retained set-comparison IDs
left series digest
right series digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full M series manifests, L comparison reports, K comparison set manifests, J comparison reports, review bundles, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonSeriesComparisonSettings
ExperimentalComparisonSeriesReference
ExperimentalComparisonSeriesComparisonRequest
ExperimentalComparisonSeriesComparisonReport
ExperimentalComparisonSeriesComparisonResult
```

Suggested result meaning:

```text
comparison_series_comparison_created
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
ExperimentalComparisonSeriesComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalComparisonSeriesComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right comparison series references
validate bounded set-comparison reference counts
compute added set-comparison IDs
compute removed set-comparison IDs
compute retained set-comparison IDs
compare declared series digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve M series manifests implicitly
retrieve L comparison reports implicitly
retrieve K comparison set manifests or lower-level inspection records implicitly
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
added set-comparison ID
removed set-comparison ID
retained set-comparison ID
digest_changed
```

These values must not be mapped automatically to semantic trend, security risk, authentication change, Runtime DifferenceObject, or BoundaryEvaluation.

```text
comparison series reference difference
≠ semantic trend
≠ risk change
≠ Runtime DifferenceObject
≠ authentication state change
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left series digest != right series digest
```

This does not establish what underlying comparison content changed, whether the change is valid, or whether semantic meaning changed.

No source retrieval or digest recomputation is approved in the initial N scope.

## 7. Error Boundary

Distinguish:

```text
same comparison series used on both sides
missing comparison series identity
duplicate set-comparison reference within a side
reference count exceeded
invalid series comparison ID
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
```

Initial N comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial N scope.

## 9. Proposed Sequence

```text
N1. comparison descriptor and settings
↓
Review
↓
N2. comparison service
↓
Review
↓
N3. optional comparison endpoint
↓
Actions verification
↓
N Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, or Runtime state.

## 10. Final Design Decision

```text
N inspection comparison series comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL COMPARISON SERIES REFERENCE COMPARISON ONLY

Comparison series retrieval
= NOT APPROVED

L comparison retrieval
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
N1. comparison descriptor and settings
```
