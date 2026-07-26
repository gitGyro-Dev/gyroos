# 160. vNext Inspection Manifest Comparison Design Gate

## 1. Purpose

Integration gate H defines a bounded request-local comparison report between two inspection batch manifests.

```text
left manifest reference
+
right manifest reference
+
explicit comparison request
↓
inspection manifest comparison report
```

The comparison reports reference-level additions, removals, retained receipt references, and declared digest changes.

It does not retrieve manifests implicitly, reconstruct receipts, compare source payload semantics, or integrate with Runtime.

## 2. Initial Scope

The initial comparison should carry explicit references only:

```text
comparison ID
left manifest descriptor
right manifest descriptor
added receipt IDs
removed receipt IDs
retained receipt IDs
left manifest digest
right manifest digest
digest_changed
created_at
warnings
metadata
```

The report must not embed full manifests, receipts, source records, payloads, metadata payloads, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalManifestComparisonSettings
ExperimentalManifestReference
ExperimentalManifestComparisonRequest
ExperimentalManifestComparisonReport
ExperimentalManifestComparisonResult
```

Suggested result meaning:

```text
comparison_report_created
```

This means only that a bounded request-local reference comparison was assembled.

It does not mean:

```text
semantic change was established
security impact was classified
authentication state changed
Runtime continuation changed
canonical history was created
```

## 4. Comparison Boundary

Proposed service:

```text
ExperimentalManifestComparisonService
```

Initial operation:

```text
compare(request)
→ ExperimentalManifestComparisonResult
```

Responsibilities:

```text
validate explicit comparison identity
validate distinct left/right manifest references
validate bounded receipt reference counts
compute added receipt IDs
compute removed receipt IDs
compute retained receipt IDs
compare declared manifest digests
preserve deterministic ordering
return immutable request-local report
```

Non-responsibilities:

```text
retrieve manifests implicitly
retrieve receipts implicitly
retrieve source records implicitly
verify declared digests against source content
reconstruct typed records
infer semantic change
classify risk or attacks
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Difference Meaning Boundary

The initial report distinguishes only set membership and declared digest equality.

```text
added receipt ID
removed receipt ID
retained receipt ID
digest_changed
```

These are not automatically Gyro Logic `DifferenceObject` values and must not be mapped to Runtime Difference, BoundaryEvaluation, security deviation, or authentication risk.

```text
manifest reference difference
≠ Runtime DifferenceObject
≠ semantic change
≠ security risk
```

## 6. Digest Boundary

The comparison may state:

```text
digest_changed = left manifest digest != right manifest digest
```

This does not prove which source content changed, whether the change is valid, or whether semantic meaning changed.

No payload retrieval or digest recomputation is approved in the initial H scope.

## 7. Error Boundary

Distinguish:

```text
same manifest used on both sides
missing manifest identity
duplicate receipt reference within a side
receipt count exceeded
invalid comparison ID
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
```

Initial comparison reports remain request-local and non-canonical.

Comparison repository storage, public retrieval, export, semantic diffing, and Runtime integration are not approved in the initial H scope.

## 9. Proposed Sequence

```text
H1. comparison descriptor and settings
↓
Review
↓
H2. comparison service
↓
Review
↓
H3. optional comparison endpoint
↓
Actions verification
↓
H Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, manifests, or Runtime state.

## 10. Final Design Decision

```text
H inspection manifest comparison design gate
= COMPLETE

Initial comparison meaning
= REQUEST-LOCAL REFERENCE COMPARISON ONLY

Manifest retrieval
= NOT APPROVED

Receipt retrieval
= NOT APPROVED

Semantic diffing
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
H1. comparison descriptor and settings
```