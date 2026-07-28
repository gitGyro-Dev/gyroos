# 292. GyroOS System Architecture and Flow Overview

## 1. Purpose

This document defines the repository-level overview for the system architecture and flow diagrams added after completion of Inspection consolidation Gate Y.

Primary source diagrams:

```text
figures/gyroos_system_architecture_flow_en.md
figures/gyroos_system_architecture_flow_jp.md
```

Publication-ready vector diagrams:

```text
figures/gyroos_system_architecture_flow_en.svg
figures/gyroos_system_architecture_flow_jp.svg
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

## 8. SVG Layout and Rendering Policy

The SVG figures use:

```text
1920 × 1080 viewBox
wide horizontal layout
white background
vector text and shapes
low-saturation grayscale palette
solid arrows for execution or reference direction
dashed arrows for read-only, non-canonical, or external-boundary relations
```

The format is intended to remain readable in:

```text
GitHub README rendering
GitHub Release notes
PDF export
Jxiv manuscript figures
presentation slides
printed grayscale copies
```

No external fonts, embedded raster images, scripts, or remote resources are required.

## 9. Recommended README Use

English README:

```markdown
![GyroOS System Architecture and Flow](figures/gyroos_system_architecture_flow_en.svg)
```

Japanese README:

```markdown
![GyroOS システム構成図・フロー図](figures/gyroos_system_architecture_flow_jp.svg)
```

For a smaller README display, use HTML with an explicit width while keeping the SVG file as the source:

```html
<img src="figures/gyroos_system_architecture_flow_en.svg" alt="GyroOS System Architecture and Flow" width="100%">
```

## 10. Recommended Publication Captions

English:

```text
Figure X. GyroOS system architecture and bounded information flow. Gyro Logic defines the invariant Structure–Slice–Stability order. GyroOS Runtime owns bounded execution and canonical Runtime records. vNext projection and Inspection contracts remain read-only and non-canonical, while GyroAuth is positioned outside the GyroOS implementation boundary as an explicit consumer.
```

Japanese:

```text
図X. GyroOSのシステム構成とbounded information flow。Gyro LogicはStructure–Slice–Stabilityの不変順序を定義し、GyroOS Runtimeはbounded executionとcanonicalなRuntime記録を所有する。vNext projectionおよびInspection contractはread-onlyかつnon-canonicalに保たれ、GyroAuthは明示的consumerとしてGyroOS実装境界の外側に位置付けられる。
```

## 11. Jxiv and Release Preparation Notes

For Jxiv submission:

```text
use the SVG as the master figure
export PDF from the SVG when the manuscript toolchain requires PDF
preserve the full white background
keep the boundary-rule footer visible
avoid cropping the F-W hierarchy or consumer boundary
verify Japanese font substitution in the final PDF
```

For GitHub Release materials:

```text
link the SVG directly from release notes
use the English figure as the default public overview
link the Japanese figure immediately below it
retain the Mermaid source files as editable architecture sources
```

The SVG is an architecture overview figure, not an API specification. Detailed contract documents remain normative.

## 12. Diagram Status

```text
English Mermaid source diagram
= CREATED

Japanese Mermaid source diagram
= CREATED

English publication-ready SVG
= CREATED

Japanese publication-ready SVG
= CREATED

README and release suitability
= DOCUMENTED

Jxiv figure preparation basis
= CREATED

Gate Y completion context
= REPRESENTED

Runtime and layer isolation
= PRESERVED
```

## 13. Non-Goals

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

## 14. Recommended Use

Use the SVG diagrams as:

```text
repository architecture entry point
review and onboarding material
README system overview
GitHub Release overview figure
Jxiv manuscript architecture figure
basis for PDF or PNG derivatives
```

Use the Mermaid diagrams as the editable source-level representation when future architecture changes require revision.