# GyroOS Review Workflow

This repository follows the Gyro Hub Multi-AI Critical Review Gate for major design notes, release candidates, and public manuscripts.

Reference: `gitGyro-Dev/gyro-hub/research_cycle.md`.

## Scope

Apply this workflow to materials whose correctness or framing can materially affect a public release, paper, or stable design milestone, including:

- major design / architecture notes
- release candidates
- public manuscript drafts
- implementation claims that appear in papers or release documentation

Routine code cleanup, minor documentation edits, and non-material wording changes do not require the full gate unless they alter a published claim or architectural invariant.

## Review roles

- ChatGPT owns disposition, revision, and source-file updates.
- Claude / Claude Code may perform independent critique and may write review artifacts under `reviews/`, but must not edit the reviewed source or paper/submission material on the project owner's behalf.
- Gemini may provide a second independent review pass after independently reading or re-importing the repository context.
- The project owner remains the final human checkpoint.

## Required classification before revision

Each material criticism should be classified before the reviewed source is changed.

Disposition:

- `valid`
- `partially valid`
- `misunderstanding`
- `needs verification`
- `future work`

Severity / publication impact:

- `blocking`
- `recommended`
- `optional`

Repeated or substantially overlapping criticisms should be linked to prior records rather than counted as new independent evidence.

## Verification rule

Factual, mathematical, bibliographic, implementation-dependent, and prior-work claims classified as `needs verification` must be checked against the actual source, implementation, tests, or authoritative reference before acceptance.

For GyroOS specifically, implementation reviews must preserve the architectural invariants already established in this repository, including the separation between bounded Runtime execution, canonical Runtime ownership, read-only projection, non-canonical Inspection, and downstream consumer interpretation.

## Convergence rule

A review loop may stop when:

1. no unresolved `blocking` item remains;
2. the current version is internally coherent;
3. blocking verification items have been checked;
4. material reviewer disagreements are recorded rather than hidden;
5. remaining `recommended`, `optional`, and `future work` items are either addressed or explicitly deferred; and
6. a new round is only restating already-resolved issues without identifying a new blocking defect.

The goal is not to eliminate all possible criticism. A version may advance while remaining provisional if it is coherent about what it currently claims.

## Suggested repository layout

```text
reviews/
  review_workflow.md
  <target>_<reviewer>_<round>_<yyyymmdd>.md
  <target>_<reviewer>_<round>_disposition_<yyyymmdd>.md
```

Review artifacts should identify:

- reviewed target and commit / version when known
- reviewer and review round
- criticism
- disposition
- severity
- verification status when applicable
- resulting action or deferral rationale

## Public manuscript gate

Before a major GyroOS manuscript is submitted publicly, use independent review passes that cover at minimum:

- internal consistency
- skeptical / adversarial reading
- implementation-to-paper consistency
- mathematical claims when present
- literature / prior-work claims when present

Submission should not be blocked by optional refinements once the convergence criteria above are met.
