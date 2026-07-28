# GyroOS v4.0 Release Candidate Architecture Figure

## Purpose

This file designates the publication-ready GyroOS system architecture figure as a primary artifact for the next GyroOS v4.0 release candidate and related publication work.

## Primary Figures

English master:

```text
figures/gyroos_system_architecture_flow_en.svg
```

Japanese master:

```text
figures/gyroos_system_architecture_flow_jp.svg
```

## Figure Scope

The figure presents, on one horizontal page:

```text
Gyro Logic Core
→ GyroOS Runtime
→ vNext Read-Only Projection
→ Inspection API
→ Inspection Contract Hierarchy F-W
→ GyroAuth Consumer Boundary
```

It also preserves the following boundaries:

```text
Structure → Slice → Stability remains invariant
GyroOS owns bounded Runtime execution and canonical Runtime records
vNext projection remains read-only and non-canonical
Inspection contracts remain request-local and POST-only
F-W arrows represent explicit reference direction only
GyroOS does not depend on GyroAuth
Inspection outputs do not become authentication decisions inside GyroOS
```

## Intended Release Use

Use the English SVG as the primary figure for:

```text
GitHub Release notes
English README
release announcement material
English paper or preprint drafts
```

Use the Japanese SVG as the primary figure for:

```text
Japanese README
Japanese release notes
Japanese paper or preprint drafts
Japanese explanatory material
```

## Publication Derivatives

The SVG files are the masters.

Create PDF or PNG derivatives only when required by the target platform.

Recommended properties:

```text
white background
no external image dependency
no external font file dependency
vector text and shapes
1920 × 1080 viewBox
print-readable line and label contrast
```

## Proposed Captions

English:

> Figure X. GyroOS system architecture and bounded information flow. Gyro Logic defines the invariant Structure–Slice–Stability order. GyroOS Runtime owns bounded execution and canonical Runtime records. vNext projection and Inspection contracts remain read-only and non-canonical, while GyroAuth is positioned outside the GyroOS implementation boundary as an explicit consumer.

Japanese:

> 図X. GyroOSのシステム構成とbounded information flow。Gyro LogicはStructure–Slice–Stabilityの不変順序を定義し、GyroOS Runtimeはbounded executionとcanonicalなRuntime記録を所有する。vNext projectionおよびInspection contractはread-onlyかつnon-canonicalに保たれ、GyroAuthは明示的consumerとしてGyroOS実装境界の外側に位置付けられる。

## Related Documentation

```text
README.md
README_jp.md
docs/292_gyroos_system_architecture_flow_overview.md
docs/291_vnext_inspection_consolidation_implementation_completion_review.md
figures/gyroos_system_architecture_flow_en.md
figures/gyroos_system_architecture_flow_jp.md
```

## Release Candidate Status

```text
English README placement
= COMPLETE

Japanese README placement
= COMPLETE

English SVG master
= AVAILABLE

Japanese SVG master
= AVAILABLE

Release Candidate primary figure reference
= ESTABLISHED

GitHub Release attachment or inline reference
= READY

jxiv manuscript figure integration
= READY FOR MANUSCRIPT-SPECIFIC NUMBERING AND CAPTION REVIEW
```
