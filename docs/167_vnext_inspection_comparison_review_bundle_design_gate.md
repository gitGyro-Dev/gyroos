# 167. vNext Inspection Comparison Review Bundle Design Gate

## 1. Purpose

Integration gate I defines a bounded request-local bundle for grouping multiple inspection manifest comparison reports by explicit reference.

```text
comparison report references
+
explicit review-bundle request
↓
inspection comparison review bundle
```

The bundle records that several request-local comparison reports were grouped for one explicit review operation.

It does not retrieve reports implicitly, infer semantic trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial bundle should carry explicit references only:

```text
review bundle ID
comparison report references
left/right manifest IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The bundle must not embed full comparison reports, manifests, receipts, source records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalComparisonReviewBundleSettings
ExperimentalComparisonReportReference
ExperimentalComparisonReviewBundleRequest
ExperimentalComparisonReviewBundle
ExperimentalComparisonReviewBundleResult
```

Suggested result meaning:

```text
review_bundle_created
```

This means only that a bounded request-local reference bundle was assembled.

It does not mean:

```text
semantic trend established
risk level established
authentication state aggregated
Runtime continuation approved
canonical review history created
```

## 4. Assembly Boundary

Proposed service:

```text
ExperimentalComparisonReviewBundleService
```

Initial operation:

```text
create_bundle(request)
→ ExperimentalComparisonReviewBundleResult
```

Responsibilities:

```text
validate explicit bundle identity
validate comparison reference uniqueness
validate bounded comparison count
copy explicit comparison and manifest references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local bundle
```

Non-responsibilities:

```text
retrieve comparison reports implicitly
retrieve manifests implicitly
retrieve receipts implicitly
recompute comparison results
infer semantic trends
classify security risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

A comparison reference may carry only bounded labels such as:

```text
comparison_id
left_manifest_id
right_manifest_id
added_count
removed_count
retained_count
digest_changed
```

The bundle must not override or reinterpret any comparison result.

```text
comparison grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial bundle may optionally record a deterministic digest over the ordered comparison-reference list.

No digest algorithm or canonicalization profile is approved until I1 review.

The bundle digest must not be presented as proof of semantic validity, security meaning, authenticity, or completeness.

## 7. Error Boundary

Distinguish:

```text
duplicate comparison reference
missing comparison identity
comparison count exceeded
invalid bundle ID
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
```

Initial review bundles remain request-local and non-canonical.

Bundle repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial I scope.

## 9. Proposed Sequence

```text
I1. review bundle descriptor, settings, and digest policy
↓
Review
↓
I2. review bundle assembly service
↓
Review
↓
I3. optional review bundle creation endpoint
↓
Actions verification
↓
I Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, or Runtime state.

## 10. Final Design Decision

```text
I inspection comparison review bundle design gate
= COMPLETE

Initial bundle meaning
= REQUEST-LOCAL COMPARISON REFERENCE GROUPING ONLY

Comparison retrieval
= NOT APPROVED

Manifest retrieval
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
I1. review bundle descriptor, settings, and digest policy
```
