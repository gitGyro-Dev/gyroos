# 188. vNext Inspection Review Bundle Comparison Set Comparison Design Gate

## 1. Purpose

Integration gate L defines a bounded request-local comparison report between two K inspection review bundle comparison set manifests.

```text
left comparison set reference
+
right comparison set reference
+
explicit comparison request
↓
inspection review bundle comparison set comparison report
```

The comparison reports reference-level additions, removals, retained J comparison references, and declared set digest changes.

It does not retrieve sets implicitly, reconstruct J comparison reports, infer semantic trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
set comparison ID
left comparison set descriptor
right comparison set descriptor
added bundle comparison IDs
removed bundle comparison IDs
retained bundle comparison IDs
left set digest
right set digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full K set manifests, J comparison reports, review bundles, H comparison reports, manifests, receipts, source records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonSetComparisonSettings
ExperimentalComparisonSetReference
ExperimentalComparisonSetComparisonRequest
ExperimentalComparisonSetComparisonReport
ExperimentalComparisonSetComparisonResult
```

Suggested result meaning:

```text
comparison_set_comparison_created
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
ExperimentalComparisonSetComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalComparisonSetComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right comparison set references
validate bounded bundle-comparison reference counts
compute added bundle comparison IDs
compute removed bundle comparison IDs
compute retained bundle comparison IDs
compare declared set digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve K set manifests implicitly
retrieve J comparison reports implicitly
retrieve review bundles or lower-level inspection records implicitly
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
added bundle comparison ID
removed bundle comparison ID
retained bundle comparison ID
digest_changed
```

These values must not be mapped automatically to semantic trend, security risk, authentication change, Runtime DifferenceObject, or BoundaryEvaluation.

```text
comparison set reference difference
≠ semantic trend
≠ risk change
≠ Runtime DifferenceObject
≠ authentication state change
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left set digest != right set digest
```

This does not establish what underlying comparison content changed, whether the change is valid, or whether semantic meaning changed.

No source retrieval or digest recomputation is approved in the initial L scope.

## 7. Error Boundary

Distinguish:

```text
same comparison set used on both sides
missing comparison set identity
duplicate bundle-comparison reference within a side
comparison count exceeded
invalid set comparison ID
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
```

Initial L comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial L scope.

## 9. Proposed Sequence

```text
L1. comparison descriptor and settings
↓
Review
↓
L2. comparison service
↓
Review
↓
L3. optional comparison endpoint
↓
Actions verification
↓
L Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, comparison sets, or Runtime state.

## 10. Final Design Decision

```text
L inspection review bundle comparison set comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL COMPARISON SET REFERENCE COMPARISON ONLY

Comparison set retrieval
= NOT APPROVED

J comparison retrieval
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
L1. comparison descriptor and settings
```
