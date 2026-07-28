# 278. vNext Inspection Documentation Index Review

## 1. Scope

This document is the X6 deliverable for integration gate X.

It reviews whether the inspection documentation from gates D through W can be located and followed consistently.

This review does not change Runtime behavior, persistence, endpoints, models, services, tests, or existing document contents.

## 2. Current State

The repository contains a complete sequence of inspection design, implementation review, overall review, and completion records through gate W.

The documentation is detailed, but navigation depends heavily on numeric filenames and prior knowledge of the gate sequence.

Decision:

```text
Documentation coverage
= SUBSTANTIALLY COMPLETE

Documentation navigation
= HIGH FRICTION
```

## 3. Main Navigation Problems

### 3.1 Numeric ordering is useful but insufficient

The numeric prefix preserves chronology, but it does not immediately show:

```text
which gate a file belongs to
whether the file is design, step review, PoC, overall review, or completion review
which document closes the gate
which document should be read next
```

### 3.2 Long filenames reduce scanability

From the later inspection gates onward, filenames contain repeated ancestry such as:

```text
comparison_set_comparison_series
comparison_series_comparison_collection
comparison_collection_comparison_sequence
comparison_sequence_comparison_register
comparison_register_comparison_ledger
comparison_ledger_comparison_archive
```

The names remain precise, but repository browsing becomes difficult.

### 3.3 Document families are not exposed through one stable entry point

A reader currently needs to reconstruct the sequence from filenames, commits, or prior review documents.

The following should be visible from one index:

```text
gate
short display name
contract kind
design gate
step reviews
minimal PoC / implementation record
overall review
completion review
status
```

## 4. Simple Documentation Index Rule

Use one dedicated inspection documentation index with one row per gate.

Recommended row shape:

```text
Gate | Short name | Kind | Design | Reviews | PoC | Overall | Completion | Status
```

Use the short names approved by X2.

Examples:

```text
F | Receipt | record
G | Batch | grouping manifest
H | Manifest Comparison | comparison report
W | Comparison Archive | grouping manifest
```

The index should link to existing files only. It must not rename, duplicate, or replace them.

## 5. Required Index Scope

The future index should cover at least:

```text
D Consumer Boundary
E Compatibility Boundary
F Receipt
G Batch
H Manifest Comparison
I Review Bundle
J Bundle Comparison
K Comparison Set
L Set Comparison
M Comparison Series
N Series Comparison
O Comparison Collection
P Collection Comparison
Q Comparison Sequence
R Sequence Comparison
S Comparison Register
T Register Comparison
U Comparison Ledger
V Ledger Comparison
W Comparison Archive
X Consolidation / Architecture Review
```

For gate X, the index should expose:

```text
272 design gate
273 X1 inventory / hierarchy map
274 X2 naming review
275 X3 shared-abstraction review
276 X4 router/workflow review
277 X5 API contract index
278 X6 documentation index review
future X7 architecture decision record
future overall review
future completion review
```

## 6. File Retention Decision

Existing files remain unchanged.

Decision:

```text
Rename existing docs
= NOT APPROVED

Move existing docs
= NOT APPROVED

Duplicate existing docs under short names
= NOT APPROVED

Add one stable index file
= APPROVED AS NEXT DOCUMENTATION ACTION
```

## 7. Completion-Record Consistency

Completion reviews exist through gate W, including the verified W completion record.

The preferred end-of-gate sequence remains:

```text
Design Gate
↓
Step Reviews
↓
Minimal PoC / Implementation Record
↓
Overall Review
↓
GitHub Actions Verification
↓
Completion Review
```

Where an older gate used a slightly different naming pattern, the index should record the actual existing file rather than forcing a rename.

## 8. Navigation Boundary

The documentation index is a navigation aid only.

It must not imply:

```text
semantic progression
causal order
Runtime continuation
authentication state
risk level
attack classification
canonical history
```

Gate order represents repository integration order and explicit contract-reference direction only.

## 9. Final Decision

```text
X6 documentation index review
= COMPLETE

D-W documentation coverage
= ACCEPTED

Current navigation model
= HIGH FRICTION

Single stable inspection documentation index
= APPROVED

Existing document rename or relocation
= NOT APPROVED

Runtime and persistence boundaries
= UNCHANGED
```

## 10. Next Step

```text
X7: Create the architecture decision record for consolidation versus further hierarchy extension.
```

X7 must decide whether another inspection hierarchy level is justified and must record which consolidation candidates may proceed after gate X.