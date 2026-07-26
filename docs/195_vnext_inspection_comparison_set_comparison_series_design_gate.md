# 195. vNext Inspection Comparison Set Comparison Series Design Gate

## 1. Purpose

Integration gate M defines a bounded request-local manifest for grouping multiple L comparison-set comparison reports by explicit reference.

```text
comparison-set comparison references
+
explicit comparison-series request
↓
inspection comparison-set comparison series manifest
```

The manifest records that several request-local L comparison reports were grouped for one explicit inspection operation.

It does not retrieve reports implicitly, infer semantic trends, classify or aggregate risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison series should carry explicit references only:

```text
comparison series ID
set-comparison references
left/right comparison set IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The series must not embed full L comparison reports, K comparison set manifests, J comparison reports, review bundles, lower-level inspection records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonSetComparisonSeriesSettings
ExperimentalComparisonSetComparisonReference
ExperimentalComparisonSetComparisonSeriesRequest
ExperimentalComparisonSetComparisonSeriesManifest
ExperimentalComparisonSetComparisonSeriesResult
```

Suggested result meaning:

```text
comparison_series_created
```

This means only that a bounded request-local reference series was assembled.

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
ExperimentalComparisonSetComparisonSeriesService
```

Initial operation:

```text
create_series(request)
→ ExperimentalComparisonSetComparisonSeriesResult
```

Responsibilities:

```text
validate explicit series identity
validate set-comparison reference uniqueness
validate bounded reference count
copy explicit comparison-set and set-comparison references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local series manifest
```

Non-responsibilities:

```text
retrieve L comparison reports implicitly
retrieve K comparison set manifests implicitly
retrieve J comparison reports or lower-level inspection records implicitly
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

An L comparison reference may carry only bounded labels such as:

```text
set_comparison_id
left_comparison_set_id
right_comparison_set_id
added_count
removed_count
retained_count
digest_changed
```

The series must not override or reinterpret any comparison result.

```text
comparison grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial series may optionally record a deterministic digest over the ordered L comparison-reference list.

No digest algorithm or canonicalization profile is approved until M1 review.

The series digest must not be presented as proof of semantic validity, security meaning, authenticity, or completeness.

## 7. Error Boundary

Distinguish:

```text
duplicate set-comparison reference
missing set-comparison identity
reference count exceeded
invalid series ID
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
```

Initial comparison series remain request-local and non-canonical.

Series repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial M scope.

## 9. Proposed Sequence

```text
M1. comparison series descriptor, settings, and digest policy
↓
Review
↓
M2. comparison series assembly service
↓
Review
↓
M3. optional comparison series creation endpoint
↓
Actions verification
↓
M Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, set comparisons, or Runtime state.

## 10. Final Design Decision

```text
M inspection comparison-set comparison series design gate
= COMPLETE

Initial series meaning
= REQUEST-LOCAL L COMPARISON REFERENCE GROUPING ONLY

L comparison retrieval
= NOT APPROVED

K comparison set retrieval
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
M1. comparison series descriptor, settings, and digest policy
```
