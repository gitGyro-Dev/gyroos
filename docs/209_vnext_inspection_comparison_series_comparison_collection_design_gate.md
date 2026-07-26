# 209. vNext Inspection Comparison Series Comparison Collection Design Gate

## 1. Purpose

Integration gate O defines a bounded request-local manifest for grouping multiple N inspection comparison-series comparison reports by explicit reference.

```text
comparison-series comparison references
+
explicit comparison-collection request
↓
inspection comparison-series comparison collection manifest
```

The manifest records that several request-local N comparison reports were grouped for one explicit inspection operation.

It does not retrieve reports implicitly, infer semantic trends, classify or aggregate risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison collection should carry explicit references only:

```text
comparison collection ID
series-comparison references
left/right comparison series IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The collection must not embed full N comparison reports, M series manifests, L comparison reports, K comparison set manifests, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonSeriesComparisonCollectionSettings
ExperimentalComparisonSeriesComparisonReference
ExperimentalComparisonSeriesComparisonCollectionRequest
ExperimentalComparisonSeriesComparisonCollectionManifest
ExperimentalComparisonSeriesComparisonCollectionResult
```

Suggested result meaning:

```text
comparison_collection_created
```

This means only that a bounded request-local reference collection was assembled.

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
ExperimentalComparisonSeriesComparisonCollectionService
```

Initial operation:

```text
create_collection(request)
→ ExperimentalComparisonSeriesComparisonCollectionResult
```

Responsibilities:

```text
validate explicit collection identity
validate series-comparison reference uniqueness
validate bounded reference count
copy explicit series and series-comparison references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local collection manifest
```

Non-responsibilities:

```text
retrieve N comparison reports implicitly
retrieve M series manifests implicitly
retrieve L comparison reports or lower-level inspection records implicitly
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

An N comparison reference may carry only bounded labels such as:

```text
series_comparison_id
left_comparison_series_id
right_comparison_series_id
added_count
removed_count
retained_count
digest_changed
```

The collection must not override or reinterpret any comparison result.

```text
comparison grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial collection may optionally record a deterministic digest over the ordered N comparison-reference list.

No digest algorithm or canonicalization profile is approved until O1 review.

The collection digest must not be presented as proof of semantic validity, security meaning, authenticity, or completeness.

## 7. Error Boundary

Distinguish:

```text
duplicate series-comparison reference
missing series-comparison identity
reference count exceeded
invalid collection ID
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
```

Initial O comparison collections remain request-local and non-canonical.

Collection repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial O scope.

## 9. Proposed Sequence

```text
O1. comparison collection descriptor, settings, and digest policy
↓
Review
↓
O2. comparison collection assembly service
↓
Review
↓
O3. optional comparison collection creation endpoint
↓
Actions verification
↓
O Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, series manifests, series comparisons, or Runtime state.

## 10. Final Design Decision

```text
O inspection comparison-series comparison collection design gate
= COMPLETE

Initial collection meaning
= REQUEST-LOCAL N COMPARISON REFERENCE GROUPING ONLY

N comparison retrieval
= NOT APPROVED

M series retrieval
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
O1. comparison collection descriptor, settings, and digest policy
```
