# 292. GyroOS System Architecture and Flow Overview

## 1. Purpose

This document defines the repository-level overview for the system architecture and flow diagrams added after completion of Inspection consolidation Gate Y.

Primary diagrams:

```text
figures/gyroos_system_architecture_flow_en.md
figures/gyroos_system_architecture_flow_jp.md
```

The diagrams provide one-page navigation across:

```text
Gyro Logic Core
GyroOS Runtime
vNext Read-Only Projection
Inspection API
Inspection Contract Hierarchy F-W
GyroAuth Consumer Boundary
```

## 2. Architecture Direction

The primary dependency and realization direction remains:

```text
Gyro Logic
↓
GyroOS
↓
GyroAuth / external consumers
```

This does not mean that GyroOS depends on GyroAuth.

GyroAuth is represented as a consumer outside the GyroOS implementation boundary.

## 3. Runtime Flow

The bounded Runtime flow is represented as:

```text
/loop/step
↓
ProcessExecutor
↓
Runtime records and history
↓
OperatorResponse
↓
next bounded execution decision
```

The diagram does not replace the detailed Runtime contract documentation.

## 4. Projection Boundary

The vNext projection layer is shown as a read-only observation path from Runtime-owned outputs.

It must not:

```text
change Runtime state
select OperatorResponse
rewrite canonical history
create authentication state
create risk state
become canonical persistence
```

## 5. Inspection Boundary

The Inspection API is shown after the read-only projection layer.

All inspection contracts remain:

```text
request-local
read-only
non-canonical
explicit references only
POST-only under the approved experimental API boundary
```

The diagram intentionally separates:

```text
route organization
contract hierarchy
Runtime ownership
consumer usage
```

## 6. F-W Hierarchy

The F-W chain represents explicit reference direction:

```text
F Receipt
→ G Batch Manifest
→ H Manifest Comparison
→ I Comparison Review Bundle
→ J Review-Bundle Comparison
→ K Review-Bundle Comparison Set
→ L Set Comparison
→ M Comparison Series
→ N Series Comparison
→ O Comparison Collection
→ P Collection Comparison
→ Q Comparison Sequence
→ R Sequence Comparison
→ S Comparison Register
→ T Register Comparison
→ U Comparison Ledger
→ V Ledger Comparison
→ W Comparison Archive
```

The arrows do not establish:

```text
chronology
semantic trend
risk aggregation
authentication aggregation
Runtime continuation
canonical history
implicit retrieval
```

## 7. Consumer Boundary

The GyroAuth consumer boundary is shown outside GyroOS.

The boundary communicates that:

```text
GyroOS may provide explicit inspection outputs
GyroAuth may consume those outputs
GyroOS does not import or depend on GyroAuth semantics
inspection results do not become authentication decisions inside GyroOS
```

## 8. Diagram Status

```text
English system architecture diagram
= CREATED

Japanese system architecture diagram
= CREATED

Gate Y completion context
= REPRESENTED

Runtime and layer isolation
= PRESERVED
```

## 9. Non-Goals

These diagrams do not define:

```text
new Runtime APIs
new inspection endpoints
new F-W contracts
new persistence behavior
new semantic inference
new risk calculation
new authentication calculation
new GyroAuth implementation details
```

## 10. Recommended Use

Use the diagrams as:

```text
repository architecture entry point
review and onboarding material
README-linked system overview
basis for future SVG or publication-quality figures
```
