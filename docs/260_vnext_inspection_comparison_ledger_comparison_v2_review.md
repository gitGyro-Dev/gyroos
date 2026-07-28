# 260. vNext Inspection Comparison Ledger Comparison V2 Review

## 1. Scope

Reviewed:

```text
ExperimentalComparisonLedgerComparisonService
comparison identity validation
per-side reference validation
added / removed / retained membership comparison
declared ledger digest comparison
resource limits
```

## 2. Comparison Boundary

The service compares only explicit ledger references supplied in the request.

It does not retrieve U ledger manifests, T comparison reports, S register manifests, or lower-level inspection records.

Decision:

```text
Explicit request-local comparison boundary
= ACCEPTED
```

## 3. Membership Difference Boundary

Ordering is deterministic:

```text
added = right-side order
removed = left-side order
retained = left-side order
```

Decision:

```text
Deterministic reference membership comparison
= ACCEPTED
```

## 4. Digest Boundary

```text
digest_changed
= left declared ledger digest != right declared ledger digest
```

If either digest is absent:

```text
digest_changed = null
```

No digest recomputation or source-content verification occurs.

Decision:

```text
Declared digest comparison boundary
= ACCEPTED
```

## 5. Validation Boundary

The service rejects:

```text
same comparison ledger on both sides
duplicate register-comparison reference within a side
reference count exceeded
invalid identifier
warning count exceeded
metadata byte limit exceeded
```

These validation results do not become Runtime, authentication, semantic trend, risk, attack, OperatorResponse, DifferenceObject, or BoundaryEvaluation outcomes.

Decision:

```text
Validation non-mapping boundary
= ACCEPTED
```

## 6. Runtime and Persistence Isolation

The service does not modify:

```text
/loop/step
ProcessExecutor
OperatorResponse
Runtime history
SQLite schema
experimental record CRUD
canonical persistence
```

Decision:

```text
Runtime and persistence isolation
= ACCEPTED
```

## 7. Final Decision

```text
V2 comparison service
= COMPLETE

Comparison ledger retrieval
= NOT INTRODUCED

T comparison retrieval
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
V3. optional comparison endpoint
```
