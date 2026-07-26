# 181. vNext Inspection Review Bundle Comparison Set Design Gate

## 1. Purpose

Integration gate K defines a bounded request-local manifest for grouping multiple inspection review bundle comparison reports by explicit reference.

```text
review bundle comparison references
+
explicit comparison-set request
↓
inspection review bundle comparison set manifest
```

The manifest records that several request-local J comparison reports were grouped for one explicit inspection operation.

It does not retrieve reports implicitly, infer trends, classify risk, aggregate authentication outcomes, or integrate with Runtime.

## 2. Initial Scope

The initial comparison set should carry explicit references only:

```text
comparison set ID
review bundle comparison references
left/right review bundle IDs
added/removed/retained counts
digest_changed labels
created_at
warnings
source refs
metadata
```

The set must not embed full J comparison reports, review bundles, H comparison reports, manifests, receipts, source records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalReviewBundleComparisonSetSettings
ExperimentalReviewBundleComparisonReference
ExperimentalReviewBundleComparisonSetRequest
ExperimentalReviewBundleComparisonSetManifest
ExperimentalReviewBundleComparisonSetResult
```

Suggested result meaning:

```text
comparison_set_created
```

This means only that a bounded request-local reference set was assembled.

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
ExperimentalReviewBundleComparisonSetService
```

Initial operation:

```text
create_set(request)
→ ExperimentalReviewBundleComparisonSetResult
```

Responsibilities:

```text
validate explicit set identity
validate comparison reference uniqueness
validate bounded comparison count
copy explicit comparison and bundle references
carry declared counts and digest_changed labels
preserve deterministic request order
return immutable request-local set manifest
```

Non-responsibilities:

```text
retrieve J comparison reports implicitly
retrieve review bundles implicitly
retrieve H comparison reports, manifests, or receipts implicitly
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Reference Meaning Boundary

A J comparison reference may carry only bounded labels such as:

```text
bundle_comparison_id
left_review_bundle_id
right_review_bundle_id
added_count
removed_count
retained_count
digest_changed
```

The set must not override or reinterpret any comparison result.

```text
comparison grouping
≠ semantic trend analysis
≠ risk aggregation
```

## 6. Optional Digest Boundary

The initial set may optionally record a deterministic digest over the ordered J comparison-reference list.

No digest algorithm or canonicalization profile is approved until K1 review.

The set digest must not be presented as proof of semantic validity, security meaning, authenticity, or completeness.

## 7. Error Boundary

Distinguish:

```text
duplicate comparison reference
missing comparison identity
comparison count exceeded
invalid set ID
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
```

Initial comparison sets remain request-local and non-canonical.

Set repository storage, public retrieval, export, semantic trend analysis, risk aggregation, and Runtime integration are not approved in the initial K scope.

## 9. Proposed Sequence

```text
K1. comparison set descriptor, settings, and digest policy
↓
Review
↓
K2. comparison set assembly service
↓
Review
↓
K3. optional comparison set creation endpoint
↓
Actions verification
↓
K Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, comparison reports, review bundles, J comparison reports, or Runtime state.

## 10. Final Design Decision

```text
K inspection review bundle comparison set design gate
= COMPLETE

Initial set meaning
= REQUEST-LOCAL J COMPARISON REFERENCE GROUPING ONLY

J comparison retrieval
= NOT APPROVED

Review bundle retrieval
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
K1. comparison set descriptor, settings, and digest policy
```