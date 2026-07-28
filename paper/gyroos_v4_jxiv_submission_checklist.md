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
= CREATED AS A FUTURE TRANSLATION VERSION
```

## 2. Submission Order

The established Gyro Project submission workflow is:

```text
1. Submit the English manuscript as the original version.
2. Complete jxiv screening and wait for public release.
3. Fix the English jxiv bibliographic information and DOI.
4. Prepare the Japanese manuscript as a faithful translation of the public English version.
5. Submit the Japanese manuscript as a translation version under the jxiv translation workflow.
```

The English and Japanese manuscripts must not be submitted simultaneously.

The Japanese version must not introduce new data, interpretation, claims, sections, limitations, or references that are absent from the public English original. Corrections that materially change the paper must first be handled through an English revision and then reflected faithfully in the Japanese translation.

## 3. Fixed Implementation Snapshot

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

The Zenodo object is a versioned software archive, not a prior publication of the jxiv manuscript itself.

## 4. Primary Figures

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

## 5. Figure Captions

English:

> Figure 1. GyroOS system architecture and bounded information flow. Gyro Logic defines the invariant Structure–Slice–Stability order. GyroOS Runtime owns bounded execution and canonical Runtime records. vNext projection and Inspection contracts remain read-only and non-canonical, while GyroAuth is positioned outside the GyroOS implementation boundary as an explicit consumer.

Japanese:

> 図1. GyroOSのシステム構成とbounded information flow。Gyro LogicはStructure–Slice–Stabilityの不変順序を定義し、GyroOS Runtimeはbounded executionとcanonicalなRuntime記録を所有する。vNext projectionおよびInspection contractはread-onlyかつnon-canonicalに保たれ、GyroAuthは明示的consumerとしてGyroOS実装境界の外側に位置付けられる。

## 6. Required Metadata Review

Confirm before English submission:

```text
final English title
English abstract
author name and affiliation
corresponding email
ORCID, if used
English keywords
software Release URL
Zenodo DOI
license statement
AI-assistance statement
conflict-of-interest statement
funding statement, if applicable
```

Confirm before Japanese translation submission:

```text
public English jxiv title
public English jxiv DOI and bibliographic information
statement that the manuscript is a Japanese translation
English original bibliographic citation
Japanese title and abstract
same author list as the English original
same author order as the English original
same affiliation scope as the English original
translation-process disclosure
AI or machine-translation disclosure, if used
required jxiv translation cover sheet
permission evidence requested by jxiv, if applicable
```

## 7. Suggested Keywords

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

## 8. Claim Guardrails

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

## 9. English–Japanese Translation Consistency Review

The Japanese manuscript must preserve the public English original's:

```text
research question
central claim
scope
section order
figures and tables
references
limitations
F–W interpretation
GyroAuth boundary
canonical / non-canonical distinction
Release and Zenodo references
AI-assistance disclosure
conflict-of-interest disclosure
funding disclosure
```

Do not translate terminology in a way that changes layer ownership or theoretical definitions.

The following are prohibited in the Japanese translation unless first incorporated through an English revision:

```text
new claims
new examples used as evidence
new evaluation results
new interpretation
new limitations
new references that change the scholarly position
new diagrams or hierarchy levels
```

## 10. Japanese Translation Front Matter

After the English version is publicly released, the Japanese PDF must state clearly at its beginning:

```text
This manuscript is a Japanese translation of the English original.
English original title
all authors
jxiv DOI
public release year
```

Japanese wording template:

> 本稿は、Jxivで公開された英語原版「[English title]」（[authors], [year], DOI: [jxiv DOI]）の日本語翻訳版である。翻訳版の内容は英語原版に忠実であり、原版にないデータ、解釈、主張を追加していない。

Translation-process disclosure template:

> 本翻訳版の作成には生成AIを翻訳補助および言語調整に使用した。著者が英語原版との対応を全編確認し、翻訳の正確性および最終内容について全責任を負う。

The final wording must reflect the actual tools and actual translation process used.

## 11. Verification Evidence

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

## 12. Reference Review

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

The Japanese translation should use the same reference list as the public English original unless an English revision establishes a different list first.

## 13. Final Assembly

Recommended sequence:

```text
1. Confirm Zenodo DOI and software citation.
2. Complete scientific review of the English draft.
3. Add Related Work and bibliography to the English draft.
4. Add exact author metadata to the English draft.
5. Convert the English manuscript to one submission PDF.
6. Verify figure rendering and embedded fonts.
7. Perform layer-consistency and final language review.
8. Submit the English manuscript.
9. Complete jxiv screening and wait for public release.
10. Record the public English jxiv DOI and bibliographic information.
11. Freeze the public English manuscript as the translation source.
12. Align the Japanese manuscript faithfully to that source.
13. Add translation front matter and translation-process disclosure.
14. Prepare the required jxiv translation cover sheet and supporting evidence.
15. Convert the Japanese translation to one submission PDF.
16. Submit the Japanese manuscript as a translation version.
```

## 14. Current Status

```text
GitHub v4.0.0 Release
= COMPLETE

Zenodo integration
= COMPLETE

English full draft
= COMPLETE AT FIRST-DRAFT LEVEL

English scientific review
= COMPLETE AT INITIAL REVIEW LEVEL

References and bibliography
= DESIGNED / NOT YET INSERTED

English author metadata
= PENDING FINAL INSERTION

English PDF assembly
= PENDING

English jxiv submission
= NEXT PUBLICATION TARGET

Japanese full draft
= CREATED AS PRELIMINARY TRANSLATION WORKING COPY

Japanese translation source
= PENDING PUBLIC ENGLISH JXIV VERSION

Japanese translation front matter
= PENDING ENGLISH DOI

Japanese jxiv translation submission
= AFTER PUBLIC ENGLISH RELEASE
```
