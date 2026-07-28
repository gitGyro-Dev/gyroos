# GyroOS v4 jxiv Submission Checklist

## 1. Manuscript Files

```text
paper/gyroos_v4_jxiv_full_draft_en.md
paper/gyroos_v4_jxiv_full_draft_jp.md
```

Status:

```text
English full draft
= CREATED

Japanese full draft
= CREATED
```

## 2. Fixed Implementation Snapshot

```text
GitHub repository
= https://github.com/gitGyro-Dev/gyroos

GitHub Release
= v4.0.0

Zenodo record
= https://zenodo.org/records/21641158

Zenodo record identifier
= 21641158
```

Before submission, confirm the final Zenodo DOI text shown on the record page and replace the record URL with DOI notation where appropriate.

## 3. Primary Figures

English master:

```text
figures/gyroos_system_architecture_flow_en.svg
```

Japanese master:

```text
figures/gyroos_system_architecture_flow_jp.svg
```

For manuscript submission:

```text
SVG remains the repository master.
Create PDF or high-resolution PNG derivatives only if required by jxiv.
Use white background.
Preserve vector text where PDF is accepted.
Confirm Japanese glyph embedding in generated PDF.
Do not rasterize at low resolution.
```

## 4. Figure Captions

English:

> Figure 1. GyroOS system architecture and bounded information flow. Gyro Logic defines the invariant Structure–Slice–Stability order. GyroOS Runtime owns bounded execution and canonical Runtime records. vNext projection and Inspection contracts remain read-only and non-canonical, while GyroAuth is positioned outside the GyroOS implementation boundary as an explicit consumer.

Japanese:

> 図1. GyroOSのシステム構成とbounded information flow。Gyro LogicはStructure–Slice–Stabilityの不変順序を定義し、GyroOS Runtimeはbounded executionとcanonicalなRuntime記録を所有する。vNext projectionおよびInspection contractはread-onlyかつnon-canonicalに保たれ、GyroAuthは明示的consumerとしてGyroOS実装境界の外側に位置付けられる。

## 5. Required Metadata Review

Confirm before submission:

```text
final English title
final Japanese title
author name and affiliation
corresponding email
ORCID, if used
keywords
software Release URL
Zenodo DOI
license statement
AI-assistance statement
conflict-of-interest statement, if required
funding statement, if required
```

## 6. Suggested Keywords

English:

```text
Gyro Logic
GyroOS
bounded runtime
Structure–Slice–Stability
trajectory continuity
read-only projection
inspection contracts
runtime architecture
```

Japanese:

```text
Gyro Logic
GyroOS
bounded runtime
Structure–Slice–Stability
Trajectory continuity
read-only projection
Inspection contract
Runtime architecture
```

## 7. Claim Guardrails

The final manuscript must not:

```text
rewrite Structure → Slice → Stability
present Operator Response as part of the invariant Core
claim that F–W is chronological
infer semantics, risk, or authentication from Inspection outputs
present GyroAuth as internal to GyroOS
present projection as canonical history
claim distributed consensus
claim multi-node continuity
claim public-production readiness
claim complete mathematical proof
claim exhaustive information preservation
```

## 8. English–Japanese Consistency Review

Verify that both manuscripts preserve the same:

```text
research question
central claim
scope
limitations
F–W interpretation
GyroAuth boundary
canonical / non-canonical distinction
Release and Zenodo references
AI-assistance disclosure
```

Do not translate terminology in a way that changes layer ownership or theoretical definitions.

## 9. Verification Evidence

Repository evidence to review before final manuscript assembly:

```text
tests/test_groups/runtime_hardening.txt
tests/test_groups/vnext_core.txt
tests/test_groups/vnext_inspection.txt
docs/287_vnext_inspection_dedicated_router_y3_review.md
docs/289_vnext_inspection_small_validation_utility_y4_review.md
docs/290_vnext_inspection_consolidation_implementation_overall_review.md
docs/291_vnext_inspection_consolidation_implementation_completion_review.md
release_candidates/gyroos/v4.0/completion_review.md
```

If exact test counts or workflow run identifiers are included in the manuscript, re-check them against the final Release-linked commit and GitHub Actions records.

## 10. Reference Review

The current full drafts are architecture and implementation manuscripts. Before submission, add and verify references for:

```text
Gyro Logic publications
previous GyroOS publication or archive, if cited
bounded execution / event sourcing / immutable history literature where relevant
projection or read-model architecture where relevant
software citation and reproducibility guidance where relevant
SQLite documentation only when implementation detail requires it
```

External literature must be used to position the work, not to replace Gyro-specific definitions.

## 11. Final Assembly

Recommended final sequence:

```text
1. Confirm Zenodo DOI and software citation.
2. Review English draft for claim precision.
3. Align Japanese draft with accepted English structure.
4. Add references and bibliography.
5. Add exact author metadata.
6. Convert Markdown to submission PDF.
7. Verify figure rendering and Japanese glyphs.
8. Perform layer-consistency review.
9. Perform final language review.
10. Submit English manuscript.
11. Submit Japanese translation according to jxiv workflow.
```

## 12. Current Status

```text
GitHub v4.0.0 Release
= COMPLETE

Zenodo integration
= COMPLETE

English full draft
= COMPLETE AT FIRST-DRAFT LEVEL

Japanese full draft
= COMPLETE AT FIRST-DRAFT LEVEL

Primary figures
= READY

References and bibliography
= PENDING

Author metadata
= PENDING FINAL INSERTION

PDF assembly
= PENDING

Final scientific and language review
= PENDING
```
