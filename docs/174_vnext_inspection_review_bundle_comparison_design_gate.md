# 174. vNext Inspection Review Bundle Comparison Design Gate

## 1. Purpose

Integration gate J defines a bounded request-local comparison report between two inspection comparison review bundles.

```text
left review bundle reference
+
right review bundle reference
+
explicit comparison request
↓
inspection review bundle comparison report
```

The comparison reports reference-level additions, removals, retained comparison references, and declared digest changes.

It does not retrieve bundles implicitly, reconstruct comparison reports, infer semantic trends, classify risk, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
bundle comparison ID
left review bundle descriptor
right review bundle descriptor
added comparison IDs
removed comparison IDs
retained comparison IDs
left bundle digest
right bundle digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full review bundles, comparison reports, manifests, receipts, source records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalReviewBundleComparisonSettings
ExperimentalReviewBundleReference
ExperimentalReviewBundleComparisonRequest
ExperimentalReviewBundleComparisonReport
ExperimentalReviewBundleComparisonResult
```

Suggested result meaning:

```text
review_bundle_comparison_created
```

This means only that a bounded request-local reference comparison was assembled.

It does not mean:

```text
semantic trend was established
risk change was classified
authentication state changed
Runtime continuation changed
canonical review history was created
```

## 4. Comparison Boundary

Proposed service:

```text
ExperimentalReviewBundleComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalReviewBundleComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right review bundle references
validate bounded comparison-reference counts
compute added comparison IDs
compute removed comparison IDs
compute retained comparison IDs
compare declared bundle digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve review bundles implicitly
retrieve comparison reports implicitly
retrieve manifests or receipts implicitly
verify declared digests against source content
recompute comparison results
infer semantic trends
classify risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Difference Meaning Boundary

The initial report distinguishes only reference membership and declared digest equality.

```text
added comparison ID
removed comparison ID
retained comparison ID
digest_changed
```

These values must not be mapped automatically to semantic trend, security risk, authentication change, Runtime DifferenceObject, or BoundaryEvaluation.

```text
review bundle reference difference
≠ semantic trend
≠ risk change
≠ Runtime DifferenceObject
≠ authentication state change
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left bundle digest != right bundle digest
```

This does not establish what underlying comparison content changed, whether the change is valid, or whether semantic meaning changed.

No source retrieval or digest recomputation is approved in the initial J scope.

## 7. Error Boundary

Distinguish:

```text
same review bundle used on both sides
missing review bundle identity
duplicate comparison reference within a side
comparison count exceeded
invalid bundle comparison ID
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
```

Initial J comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial J scope.

## 9. Proposed Sequence

```text
J1. comparison descriptor and settings
↓
Review
↓
J2. comparison service
↓
Review
↓
J3. optional comparison endpoint
↓
Actions verification
↓
J Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, or Runtime state.

## 10. Final Design Decision

```text
J inspection review bundle comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL REVIEW BUNDLE REFERENCE COMPARISON ONLY

Review bundle retrieval
= NOT APPROVED

Comparison report retrieval
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
J1. comparison descriptor and settings
```
