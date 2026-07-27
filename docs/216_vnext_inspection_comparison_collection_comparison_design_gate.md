# 216. vNext Inspection Comparison Collection Comparison Design Gate

## 1. Purpose

Integration gate P defines a bounded request-local comparison report between two O inspection comparison-series comparison collection manifests.

```text
left comparison collection reference
+
right comparison collection reference
+
explicit comparison request
↓
inspection comparison collection comparison report
```

The comparison reports reference-level additions, removals, retained N comparison references, and declared collection digest changes.

It does not retrieve collections implicitly, reconstruct N comparison reports, infer semantic trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
collection comparison ID
left comparison collection descriptor
right comparison collection descriptor
added series-comparison IDs
removed series-comparison IDs
retained series-comparison IDs
left collection digest
right collection digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full O collection manifests, N comparison reports, M series manifests, L comparison reports, comparison sets, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonCollectionComparisonSettings
ExperimentalComparisonCollectionReference
ExperimentalComparisonCollectionComparisonRequest
ExperimentalComparisonCollectionComparisonReport
ExperimentalComparisonCollectionComparisonResult
```

Suggested result meaning:

```text
comparison_collection_comparison_created
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
ExperimentalComparisonCollectionComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalComparisonCollectionComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right comparison collection references
validate bounded series-comparison reference counts
compute added series-comparison IDs
compute removed series-comparison IDs
compute retained series-comparison IDs
compare declared collection digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve O collection manifests implicitly
retrieve N comparison reports implicitly
retrieve M series manifests or lower-level inspection records implicitly
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
added series-comparison ID
removed series-comparison ID
retained series-comparison ID
digest_changed
```

These values must not be mapped automatically to semantic trend, security risk, authentication change, Runtime DifferenceObject, or BoundaryEvaluation.

```text
comparison collection reference difference
≠ semantic trend
≠ risk change
≠ Runtime DifferenceObject
≠ authentication state change
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left collection digest != right collection digest
```

This does not establish what underlying comparison content changed, whether the change is valid, or whether semantic meaning changed.

No source retrieval or digest recomputation is approved in the initial P scope.

## 7. Error Boundary

Distinguish:

```text
same comparison collection used on both sides
missing comparison collection identity
duplicate series-comparison reference within a side
reference count exceeded
invalid collection comparison ID
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
```

Initial P comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial P scope.

## 9. Proposed Sequence

```text
P1. comparison descriptor and settings
↓
Review
↓
P2. comparison service
↓
Review
↓
P3. optional comparison endpoint
↓
Actions verification
↓
P Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, series comparisons, comparison collections, or Runtime state.

## 10. Final Design Decision

```text
P inspection comparison collection comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL COMPARISON COLLECTION REFERENCE COMPARISON ONLY

Comparison collection retrieval
= NOT APPROVED

N comparison retrieval
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
P1. comparison descriptor and settings
```
