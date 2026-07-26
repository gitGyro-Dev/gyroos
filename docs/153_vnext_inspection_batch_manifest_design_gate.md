# 153. vNext Inspection Batch Manifest Design Gate

## 1. Purpose

Integration gate G defines a bounded manifest for grouping multiple request-local inspection receipts by reference.

```text
inspection receipt references
+
explicit batch request
↓
inspection batch manifest
```

The manifest records that a set of inspection receipts was grouped for one explicit review operation.

It does not persist receipts, reconstruct source records, create semantic authority, or integrate with Runtime.

## 2. Initial Scope

The initial manifest should carry explicit references only:

```text
batch manifest ID
receipt references
source record references
contract labels
created_at
warnings
source refs
metadata
```

The manifest must not embed full receipts, source payloads, source metadata, or typed vNext semantic records.

## 3. Proposed Models

```text
ExperimentalInspectionBatchSettings
ExperimentalInspectionReceiptReference
ExperimentalInspectionBatchRequest
ExperimentalInspectionBatchManifest
ExperimentalInspectionBatchResult
```

Suggested result meaning:

```text
batch_manifest_created
```

This means only that a bounded request-local manifest was assembled.

It does not mean:

```text
all receipts are compatible
all source records are semantically equivalent
batch authentication succeeded
Runtime continuation is approved
canonical persistence completed
```

## 4. Assembly Boundary

Proposed service:

```text
ExperimentalInspectionBatchService
```

Initial operation:

```text
create_manifest(request)
→ ExperimentalInspectionBatchResult
```

Responsibilities:

```text
validate explicit manifest identity
validate receipt reference uniqueness
validate bounded receipt count
copy explicit receipt/source references
carry contract labels and warnings
return immutable request-local manifest
```

Non-responsibilities:

```text
retrieve receipts implicitly
retrieve source records implicitly
validate receipt digests against source payloads
reconstruct typed records
migrate versions
infer semantic equivalence
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
```

## 5. Receipt Reference Boundary

A receipt reference should carry only bounded identifiers and labels such as:

```text
receipt_id
source_record_id
source_process_id
source_record_type
source_contract_version
consumer_contract_version
compatible_for_inspection
payload_digest
metadata_digest
```

The manifest must not override the compatibility result recorded by any receipt reference.

```text
batch grouping
≠ compatibility aggregation
```

## 6. Digest Boundary

The initial manifest may optionally record a deterministic digest over the ordered list of receipt references.

No digest algorithm or canonicalization profile is approved until G1 review.

The manifest digest must not be presented as proof that source records are valid, equivalent, authentic, or complete.

## 7. Error Boundary

Distinguish:

```text
duplicate receipt reference
missing receipt identity
receipt count exceeded
invalid manifest ID
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
```

Initial manifests remain request-local and non-canonical.

Manifest repository storage, public retrieval, export, and Runtime integration are not approved in the initial G scope.

## 9. Proposed Sequence

```text
G1. manifest descriptor, settings, and digest policy
↓
Review
↓
G2. manifest assembly service
↓
Review
↓
G3. optional manifest creation endpoint
↓
Actions verification
↓
G Review
```

The optional endpoint, if approved, should remain under:

```text
/vnext/experimental
```

and must not modify existing records, receipts, or Runtime state.

## 10. Final Design Decision

```text
G inspection batch manifest design gate
= COMPLETE

Initial manifest meaning
= REQUEST-LOCAL REFERENCE GROUPING ONLY

Receipt persistence
= NOT APPROVED

Receipt retrieval
= NOT APPROVED

Typed reconstruction
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
G1. manifest descriptor, settings, and digest policy
```
