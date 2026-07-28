# 274. vNext Inspection Naming and Readability Review

## 1. Scope

This document is the X2 deliverable for integration gate X.

It reviews the naming and readability of the inspection contracts implemented from gates D through W.

This review does not rename code, change endpoints, modify tests, add aliases, introduce migration behavior, or approve a new hierarchy level.

## 2. Current State

The current names are explicit and technically consistent, but they become difficult to read from gate L onward because each layer repeats the full name of the previous layer.

Examples:

```text
inspection_review_bundle_comparison_set_comparison
inspection_comparison_set_comparison_series
inspection_comparison_series_comparison_collection
inspection_comparison_collection_comparison_sequence
inspection_comparison_sequence_comparison_register
inspection_comparison_register_comparison_ledger
inspection_comparison_ledger_comparison_archive
```

The same growth appears in:

```text
module names
service names
class names
endpoint paths
test file names
error codes
workflow test lists
```

## 3. Main Readability Problems

### 3.1 Repeated full ancestry

Names describe both the current contract and much of its ancestry.

This preserves precision, but makes adjacent contracts hard to distinguish quickly.

### 3.2 Comparison ambiguity

The word `comparison` appears several times in many names.

A reader must inspect the full contract definition to determine whether the contract:

```text
compares manifests
compares bundles
compares sets
collects comparison reports
compares those collections
```

### 3.3 Long operational identifiers

Long names increase the risk of:

```text
incorrect imports
incorrect endpoint paths
incorrect error-code expectations
omitted workflow tests
copy-and-paste defects
```

The previously corrected comparison-set API error-code expectation is an example of this risk.

### 3.4 Adjacent-layer confusion

From M through W, adjacent contracts usually alternate between:

```text
comparison report
bounded grouping manifest
```

The contract meaning is valid, but the naming alone does not make that alternation easy to scan.

## 4. Simple Naming Rule

For architecture documents and indexes, use one short display name per gate:

| Gate | Short display name | Contract kind |
|---|---|---|
| F | Receipt | record |
| G | Batch | grouping manifest |
| H | Manifest Comparison | comparison report |
| I | Review Bundle | grouping manifest |
| J | Bundle Comparison | comparison report |
| K | Comparison Set | grouping manifest |
| L | Set Comparison | comparison report |
| M | Comparison Series | grouping manifest |
| N | Series Comparison | comparison report |
| O | Comparison Collection | grouping manifest |
| P | Collection Comparison | comparison report |
| Q | Comparison Sequence | grouping manifest |
| R | Sequence Comparison | comparison report |
| S | Comparison Register | grouping manifest |
| T | Register Comparison | comparison report |
| U | Comparison Ledger | grouping manifest |
| V | Ledger Comparison | comparison report |
| W | Comparison Archive | grouping manifest |

These short display names are documentation labels only.

They do not replace public contract names, Python symbols, module names, endpoint paths, or error codes.

## 5. Repository Naming Decision

Current implementation names remain unchanged during gate X.

Reason:

```text
existing tests depend on the names
existing endpoints are already implemented
existing review documents use the names
renaming would require compatibility analysis
aliases would add another naming layer
partial renaming would increase inconsistency
```

Decision:

```text
Immediate rename
= NOT APPROVED

Compatibility aliases
= NOT APPROVED

Documentation short names
= APPROVED

Gate letters as stable navigation keys
= APPROVED
```

## 6. Rules for Future Work

Future inspection work should follow these rules.

### Rule 1

Use the gate identifier and short display name in architecture documents.

Example:

```text
V — Ledger Comparison
W — Comparison Archive
```

### Rule 2

Do not create another contract merely by appending a new grouping word to the existing full name.

### Rule 3

A new contract name must describe a distinct bounded requirement, not only its position in the hierarchy.

### Rule 4

Do not introduce abbreviations into public Python classes or endpoint paths unless a separate compatibility and migration decision approves them.

### Rule 5

Keep contract kind explicit in indexes:

```text
record
grouping manifest
comparison report
```

This is more important for readability than repeating the full ancestry.

## 7. Simplification Direction

The preferred simplification is documentation and navigation first:

```text
gate letter
+
short display name
+
contract kind
+
explicit input reference type
```

Example:

```text
W — Comparison Archive
Kind: grouping manifest
Input: explicit V ledger-comparison references
Output: request-local archive manifest
```

This avoids implementation churn while making the hierarchy readable.

## 8. Final Decision

```text
X2 naming and readability review
= COMPLETE

Current contract names
= TECHNICALLY CONSISTENT

Current contract names from L onward
= HIGH READABILITY COST

Immediate implementation rename
= NOT APPROVED

Documentation short-name scheme
= APPROVED

Gate-letter navigation
= APPROVED

New hierarchy extension based on name continuation
= NOT APPROVED

Runtime and persistence boundaries
= UNCHANGED
```

## 9. Next Step

```text
X3: Review repeated validation, digest, model, service, API-error, and test patterns for limited shared abstractions.
```

X3 must prefer small reusable helpers over a universal generic inspection framework.