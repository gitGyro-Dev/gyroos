# GyroOS v4.0.0 Formal GitHub Release Steps

## 1. Preconditions

Confirm the following before creating the Release:

```text
release scope is fixed
completion review is complete
English Release Notes exist
Japanese Release Notes exist
README English and Japanese include the architecture figures
latest main-branch workflow run is successful
release tag does not already exist
```

Primary files:

```text
release_candidates/gyroos/v4.0/release_scope.md
release_candidates/gyroos/v4.0/completion_review.md
release_candidates/gyroos/v4.0/release_notes.md
release_candidates/gyroos/v4.0/release_notes_jp.md
release_candidates/gyroos/v4.0/architecture_figure.md
```

## 2. Release Identity

```text
Tag: v4.0.0
Target: main
Release title: GyroOS v4.0.0 — Bounded Runtime and Experimental Inspection Architecture
```

## 3. GitHub UI Procedure

1. Open the repository Releases page.
2. Select **Draft a new release**.
3. Select **Choose a tag**.
4. Enter `v4.0.0`.
5. Create the tag from the current `main` branch.
6. Set the release title to:

```text
GyroOS v4.0.0 — Bounded Runtime and Experimental Inspection Architecture
```

7. Copy the full contents of:

```text
release_candidates/gyroos/v4.0/release_notes.md
```

into the Release description.

8. Do not mark the Release as a pre-release unless the intended public positioning changes.
9. Do not mark it as the latest release until the final tag and target commit are confirmed.
10. Publish the Release.

## 4. Recommended Figure Reference

The Release Notes may include the English architecture figure using:

```markdown
![GyroOS System Architecture and Flow](https://raw.githubusercontent.com/gitGyro-Dev/gyroos/v4.0.0/figures/gyroos_system_architecture_flow_en.svg)
```

Japanese announcements may reference:

```markdown
![GyroOS システム構成図・フロー図](https://raw.githubusercontent.com/gitGyro-Dev/gyroos/v4.0.0/figures/gyroos_system_architecture_flow_jp.svg)
```

Use tag-pinned URLs after the Release exists.

## 5. Post-Release Verification

After publishing, confirm:

```text
tag resolves to the intended main-branch commit
Release page displays the complete English notes
README images resolve at the tagged revision
architecture SVG files display correctly
source archive downloads are available
Release is listed as latest when intended
```

## 6. Post-Release Repository Update

Record the final Release URL and tag in:

```text
README.md
README_jp.md
release_candidates/gyroos/v4.0/completion_review.md
Gyro Hub publication and artifact records
```

Do not insert a guessed Release URL before publication.

## 7. jxiv Transition

After the Release is published:

```text
freeze the implementation citation as GyroOS v4.0.0
record the tag and release date
use the tagged architecture SVG as the manuscript figure source
begin the English manuscript
prepare the Japanese manuscript from the reviewed English structure
add the final GitHub Release reference to both manuscripts
```

## 8. Current Status

```text
Release scope
= FIXED

Completion review
= COMPLETE

English Release Notes
= READY

Japanese Release Notes
= READY

Formal GitHub Release
= REQUIRES GITHUB RELEASE UI OR RELEASE-CAPABLE TOOLING

jxiv manuscript preparation
= READY TO BEGIN AFTER RELEASE PUBLICATION
```
