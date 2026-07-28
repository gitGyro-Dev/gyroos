# 267. vNext Inspection Comparison Ledger Comparison Archive W2 Review

## 1. Scope

Reviewed:

```text
comparison archive assembly service
reference uniqueness validation
resource bounds
ordered digest assembly
request-local immutable output
```

## 2. Assembly Boundary

The service accepts one explicit archive request and returns one immutable request-local archive manifest.

It does not retrieve V comparison reports, U ledger manifests, lower-level inspection records, payloads, metadata payloads, or typed semantic records.

Decision:

```text
Reference-only archive assembly
= ACCEPTED
```

## 3. Identity and Uniqueness

The service validates:

```text
comparison_archive_id
ledger_comparison_id
left_comparison_ledger_id
right_comparison_ledger_id
```

Duplicate `ledger_comparison_id` values are rejected within one archive request.

Decision:

```text
Explicit archive identity and uniqueness
= ACCEPTED
```

## 4. Ordering and Digest

Input order is preserved exactly.

The archive digest is computed over the ordered V comparison-reference list using the W1-approved profile.

Decision:

```text
Deterministic ordered archive assembly
= ACCEPTED
```

## 5. Resource Boundary

The service enforces bounds for:

```text
reference count
identifier length
warning count
source reference count
metadata bytes
```

Decision:

```text
Bounded archive assembly
= ACCEPTED
```

## 6. Error Meaning Boundary

Duplicate references and resource-limit violations remain inspection archive validation errors only.

They do not become:

```text
AUTH_FAIL
REAUTH_REQUIRED
identity break
trajectory break
attack classification
OperatorResponse
Runtime DifferenceObject
BoundaryEvaluation
```

Decision:

```text
Archive error non-mapping
= ACCEPTED
```

## 7. Runtime and Persistence Isolation

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
inspection boundaries D-V
```

No repository, retrieval, export, Runtime integration, authentication aggregation, or canonical persistence is introduced.

## 8. Final Decision

```text
W2 comparison archive assembly service
= COMPLETE

V comparison retrieval
= NOT INTRODUCED

U ledger retrieval
= NOT INTRODUCED

Semantic trend analysis
= NOT INTRODUCED

Risk aggregation
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

Proceed next to:

```text
W3. optional comparison archive creation endpoint
```
