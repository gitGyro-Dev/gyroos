# 283. vNext Inspection Documentation Index

## 1. Purpose

This is the stable navigation entry point for the vNext inspection integration and consolidation documents.

Existing documents are not renamed or moved.

Use the gate letter as the stable key and the short display name as the readable label.

## 2. Contract Gates

| Gate | Short name | Kind | Primary documents | Status |
|---|---|---|---|---|
| D | Consumer Boundary | boundary | Consumer boundary design, reviews, and completion record | COMPLETE |
| E | Compatibility Boundary | boundary | Compatibility boundary design, reviews, and completion record | COMPLETE |
| F | Receipt | record | Inspection receipt design, step reviews, PoC, overall review, completion review | COMPLETE |
| G | Batch | grouping manifest | Batch manifest design, step reviews, PoC, overall review, completion review | COMPLETE |
| H | Manifest Comparison | comparison report | Manifest comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| I | Review Bundle | grouping manifest | Comparison review-bundle design, step reviews, PoC, overall review, completion review | COMPLETE |
| J | Bundle Comparison | comparison report | Review-bundle comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| K | Comparison Set | grouping manifest | Review-bundle comparison-set design, step reviews, PoC, overall review, completion review | COMPLETE |
| L | Set Comparison | comparison report | Comparison-set comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| M | Comparison Series | grouping manifest | Comparison-series design, step reviews, PoC, overall review, completion review | COMPLETE |
| N | Series Comparison | comparison report | Series-comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| O | Comparison Collection | grouping manifest | Comparison-collection design, step reviews, PoC, overall review, completion review | COMPLETE |
| P | Collection Comparison | comparison report | Collection-comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| Q | Comparison Sequence | grouping manifest | Comparison-sequence design, step reviews, PoC, overall review, completion review | COMPLETE |
| R | Sequence Comparison | comparison report | Sequence-comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| S | Comparison Register | grouping manifest | Comparison-register design, step reviews, PoC, overall review, completion review | COMPLETE |
| T | Register Comparison | comparison report | Register-comparison design, step reviews, PoC, overall review, completion review | COMPLETE |
| U | Comparison Ledger | grouping manifest | Comparison-ledger design, step reviews, PoC, overall review, completion review | COMPLETE |
| V | Ledger Comparison | comparison report | `docs/263_vnext_inspection_comparison_ledger_comparison_review.md`; `docs/264_vnext_inspection_comparison_ledger_comparison_completion_review.md` | COMPLETE |
| W | Comparison Archive | grouping manifest | `docs/265_vnext_inspection_comparison_ledger_comparison_archive_design_gate.md`; `docs/266_vnext_inspection_comparison_ledger_comparison_archive_w1_review.md`; `docs/267_vnext_inspection_comparison_ledger_comparison_archive_w2_review.md`; `docs/268_vnext_inspection_comparison_ledger_comparison_archive_w3_review.md`; `docs/269_vnext_inspection_comparison_ledger_comparison_archive_minimal_poc.md`; `docs/270_vnext_inspection_comparison_ledger_comparison_archive_review.md`; `docs/271_vnext_inspection_comparison_ledger_comparison_archive_completion_review.md` | COMPLETE |

## 3. Consolidation Gates

| Gate | Short name | Kind | Primary documents | Status |
|---|---|---|---|---|
| X | Architecture Review | consolidation review | `docs/272_vnext_inspection_contract_consolidation_architecture_review_design_gate.md`; `docs/273_vnext_inspection_contract_inventory_hierarchy_map.md`; `docs/274_vnext_inspection_naming_readability_review.md`; `docs/275_vnext_inspection_shared_abstraction_review.md`; `docs/276_vnext_inspection_router_workflow_growth_review.md`; `docs/277_vnext_inspection_api_contract_index.md`; `docs/278_vnext_inspection_documentation_index_review.md`; `docs/279_vnext_inspection_architecture_decision_record.md`; `docs/280_vnext_inspection_contract_consolidation_architecture_review.md`; `docs/281_vnext_inspection_contract_consolidation_architecture_completion_review.md` | COMPLETE |
| Y | Consolidation Implementation | bounded implementation | `docs/282_vnext_inspection_consolidation_implementation_planning_design_gate.md`; this index; subsequent Y step reviews and completion records | IN PROGRESS |

## 4. Reference Hierarchy

```text
F Receipt
↓
G Batch
↓
H Manifest Comparison
↓
I Review Bundle
↓
J Bundle Comparison
↓
K Comparison Set
↓
L Set Comparison
↓
M Comparison Series
↓
N Series Comparison
↓
O Comparison Collection
↓
P Collection Comparison
↓
Q Comparison Sequence
↓
R Sequence Comparison
↓
S Comparison Register
↓
T Register Comparison
↓
U Comparison Ledger
↓
V Ledger Comparison
↓
W Comparison Archive
```

The arrows describe explicit reference direction only.

They do not establish chronology, semantic trend, risk, authentication state, Runtime continuation, or canonical history.

## 5. API Index

The normative Inspection API index is:

```text
docs/277_vnext_inspection_api_contract_index.md
```

Only the approved request-local POST endpoints listed there are part of the inspection contract family.

## 6. Architecture Decisions

The normative consolidation decisions are:

```text
docs/279_vnext_inspection_architecture_decision_record.md
```

Key decision:

```text
Additional inspection hierarchy after W
= NOT APPROVED

Consolidation before extension
= REQUIRED
```

## 7. Navigation Rule

Use this order when reviewing one gate:

```text
Design Gate
↓
Step Reviews
↓
Minimal PoC / Implementation Record
↓
Overall Review
↓
Completion Review
```

For repository-wide inspection review, use:

```text
this index
↓
X1 hierarchy map
↓
X5 API index
↓
X7 architecture decision
```

## 8. Boundary Reminder

All inspection contracts remain:

```text
request-local
read-only
non-canonical
explicit references only
no implicit retrieval
no semantic inference
no risk aggregation
no authentication aggregation
no Runtime mutation
no canonical persistence
```

The following remain unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
```

## 9. Y1 Decision

```text
Stable inspection documentation index
= CREATED

Existing document rename or move
= NOT REQUIRED

Gate-letter navigation
= ACTIVE

Y1 implementation
= COMPLETE PENDING REVIEW
```
