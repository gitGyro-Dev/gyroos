# 154. vNext Inspection Batch Manifest G1 Review

## 1. Scope

Reviewed:

```text
ExperimentalInspectionBatchSettings
ExperimentalInspectionBatchDigestPolicy
ExperimentalInspectionReceiptReference
ExperimentalInspectionBatchRequest
ExperimentalInspectionBatchManifest
ExperimentalInspectionBatchResult
```

## 2. Manifest Meaning

```text
batch_manifest_created
≠ receipt compatibility aggregation
≠ semantic equivalence
≠ authentication success
≠ Runtime continuation approval
≠ canonical persistence
```

Decision:

```text
Request-local reference grouping meaning
= ACCEPTED
```

## 3. Digest Policy

The initial manifest digest policy is:

```text
algorithm
= SHA-256

canonicalization
= JSON_SORTED_KEYS_UTF8_COMPACT_V1
```

The digest input is the ordered list of receipt reference representations.

Decision:

```text
Deterministic ordered-reference digest
= ACCEPTED
```

## 4. Receipt Reference Boundary

A reference carries identifiers, contract labels, compatibility flag, and optional payload/metadata digests only.

It does not embed a complete receipt, source payload, or source metadata.

Decision:

```text
Reference-only source boundary
= ACCEPTED
```

## 5. Model Boundary

Models are closed and frozen. Runtime and authentication output fields are absent.

Decision:

```text
Closed immutable manifest contract
= ACCEPTED
```

## 6. Final Decision

```text
G1 manifest descriptor, settings, and digest policy
= COMPLETE

Receipt persistence
= NOT INTRODUCED

Receipt retrieval
= NOT INTRODUCED

Authentication aggregation
= NOT INTRODUCED

Runtime integration
= NOT INTRODUCED

Canonical persistence
= NOT INTRODUCED

Critical design blocker
= NONE IDENTIFIED
```

Proceed to G2 manifest assembly service.
