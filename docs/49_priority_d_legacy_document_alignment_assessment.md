# 49. Priority D — Legacy Document Alignment Assessment

---

## 1. Purpose

This document begins **Priority D: Legacy Document Alignment** after the completion of:

```text
Priority A
= Gyro Logic v3.1 Core Runtime Mapping

Priority B
= Runtime Continuity and Operator Response refinement

Priority C
= Boundary-aware Runtime definition and review
```

The purpose of Priority D is to align earlier GyroOS design documents with the newer, reviewed Runtime model without rewriting the theory or discarding still-valid implementation ideas.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Priority D does not introduce a new Core element, Runtime Stage, or application responsibility.

---

## 2. Why Priority D Is Required

Priority C established a safer separation among:

```text
Boundary
Boundary State
Boundary evidence
Void as Boundary State
Void evidence / reference
Stability
Operator Response
Runtime Continuity
```

Several earlier GyroOS documents predate this separation.

They contain useful architecture, but may still imply one or more unsafe readings:

```text
Boundary as a fixed field or stage
Boundary State as a final verdict
Void as an actor
Void existence as an automatic response trigger
Stability as a controller or terminal result
Context existence as an automatic Re-Slice trigger
Re-Slice, Jump, Defer, and Stop as interchangeable handling modes
latest state overwriting prior trajectory evidence
```

Priority D corrects those readings while retaining valid runtime mechanisms.

---

## 3. Priority D Scope

Priority D covers the following existing documents:

```text
D-1  docs/18_void_defer_jump.md
D-2  docs/14_api_design.md
D-3  docs/15_context_runtime.md
D-4  docs/16_reslice_engine.md
D-5  docs/17_context_loop_controller.md
D-6  docs/21_memory_runtime.md
D-7  docs/22_trajectory_cache.md
D-8  docs/26_poc_runtime_object_graph.md
D-9  docs/27_claude_poc_implementation_prompt.md
D-10 Priority D Cross-document Review and Refinement
```

This order is intentional.

The highest-risk responsibility mixture is corrected first, followed by API, Context, Re-Slice, control, memory, trajectory, and finally PoC specifications.

---

## 4. Priority D Is Alignment, Not Replacement

Priority D must not treat every earlier statement as invalid.

The safe method is:

```text
retain valid mechanism
+
replace unsafe conceptual wording
+
clarify responsibility owner
+
add traceability to the newer canonical document
```

Priority D must not:

```text
rewrite Gyro Logic
change Structure → Slice → Stability
move Operator Orientation outside Slice
turn Boundary into a Runtime Stage
turn Stability into a controller
turn Boundary State into an application verdict
remove useful bounded implementation mechanisms without cause
expand GyroOS into GyroAuth or another application layer
```

---

## 5. Canonical Runtime Model for Alignment

All Priority D updates must remain consistent with the following reviewed relation:

```text
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  distinctions become readable
  slice-done {
    representation
    Difference / Deviation
    BoundaryEvidence when readable
    BoundaryStateRecord when classifiable
    Context references
    VoidEvidence / Void references when retained
  }
}
↓
Stability
↓
Loop Controller / Operator Response
↓
CONTINUE | ADJUST | RESLICE | JUMP | DEFER | STOP
↓
Runtime Continuity relation
```

Responsibility boundary:

```text
Slice
= opens the Runtime Path and makes relations readable

SliceDone
= preserves the readable established Slice result

Stability
= reads whether the opened Path is readable as an establishment that can continue

Loop Controller / Operator Response
= selects the next Runtime relation

Memory Runtime / Trajectory Cache
= preserve evidence, lineage, and changing readability
```

---

## 6. Canonical Boundary-aware Terms

Priority D should use the following implementation names consistently where concrete objects are required:

```text
BoundaryEvidence
BoundaryStateRecord
VoidEvidence
```

Collection naming:

```python
boundary_evidence: list[BoundaryEvidence]
boundary_state_records: list[BoundaryStateRecord]
void_evidence: list[VoidEvidence]
```

Reference naming:

```python
boundary_refs: list[str]
boundary_state_refs: list[str]
void_refs: list[str]
```

Naming rule:

```text
*_evidence
= embedded or directly retained evidence objects

*_records
= classified runtime records with identity and lineage

*_refs
= references to separately retained records
```

---

## 7. Canonical Void Separation

Every Priority D update must preserve at least the following distinctions:

```text
Void as Boundary State
≠ VoidEvidence
≠ Void reference
≠ retained pending relation
≠ DEFER
≠ RESLICE
≠ JUMP
≠ STOP
```

Void is not an actor.

```text
Void does not defer.
Void does not re-slice.
Void does not jump.
Void does not stop.
```

The response owner remains:

```text
Loop Controller / Operator Response
```

Void as Boundary State requires:

```text
the relevant Boundary relation is identifiable
+
the target relation cannot currently be read or connected sufficiently
```

If the Boundary distinction itself is unreadable, the runtime should retain:

```text
unclassified Boundary evidence
or
unreadable distinction evidence
```

rather than forcing a `VOID` classification.

---

## 8. Canonical Response Separation

Priority D must remove or qualify direct mappings such as:

```text
Context exists → automatic RESLICE
Void exists → automatic DEFER
Unknown → automatic RESLICE
low Stability → automatic STOP
Boundary crossed → automatic JUMP
```

The reviewed decision relation is:

```text
SliceDone evidence
+ StabilityResult
+ Difference / Deviation
+ Boundary readability
+ Boundary State records
+ Context
+ Void evidence
+ Trajectory history
+ recoverability
+ retainability
+ Re-Slice viability
+ Runtime limits
+ policy
↓
Loop Controller / Operator Response
```

A bounded implementation may use deterministic policy rules.

However, those rules must be labeled as implementation policy, not Gyro Logic definitions.

---

## 9. Canonical Confidence Separation

Priority D must not reuse one confidence value for several conceptual responsibilities.

Keep separate:

```text
boundary_readability
boundary_state_confidence
stability
response_confidence
context_confidence when applicable
```

No one value silently substitutes for another.

---

## 10. Canonical Memory and Trajectory Rule

Priority D must preserve both:

```text
historical traceability
+
current-scope selection
```

A later Slice may refine or reclassify a Boundary relation.

It must not silently erase the earlier record.

Recommended relations include:

```text
refined_from
reclassified_from
conflicts_with
coexists_with
supersedes_for_current_scope
reopened_from
invalidated_by_evidence
unreadable_under
```

`supersedes_for_current_scope` does not mean universal deletion or invalidation.

---

## 11. Document-specific Initial Assessment

### D-1: `docs/18_void_defer_jump.md`

Risk level:

```text
HIGHEST
```

Primary review points:

```text
Void state / evidence / reference separation
Void is not an actor
DEFER, RESLICE, JUMP, STOP responsibility separation
pending relation versus stopped relation
Boundary-relative Void condition
removal of automatic response implications
```

This document should be aligned first.

### D-2: `docs/14_api_design.md`

Primary review points:

```text
SliceDone / StabilityResult / OperatorResponse separation
Boundary-aware API fields
HTTP status versus Runtime result separation
canonical naming
support APIs remain subordinate to /loop/step
```

### D-3: `docs/15_context_runtime.md`

Primary review points:

```text
Context ≠ Boundary
Context ≠ automatic Re-Slice trigger
Context as retained or inferred surrounding Structure
Context confidence separation
Context lineage
```

### D-4: `docs/16_reslice_engine.md`

Primary review points:

```text
RESLICE as Operator Response
Re-Slice as runtime operation
retained source requirements
Boundary and Void evidence as possible inputs, not owners
lineage preservation
```

### D-5: `docs/17_context_loop_controller.md`

Primary review points:

```text
Loop Controller owns response selection
Context does not control the loop
Boundary-aware multi-evidence decision
CONTINUE / ADJUST / RESLICE / JUMP / DEFER / STOP consistency
```

### D-6: `docs/21_memory_runtime.md`

Primary review points:

```text
BoundaryEvidence / BoundaryStateRecord / VoidEvidence retention
historical record versus current-scope pointer
resolution decay without destroying lineage
response evidence references
```

### D-7: `docs/22_trajectory_cache.md`

Primary review points:

```text
Boundary readability trajectory
Boundary State reclassification history
multiple Boundary coexistence
Void-related trajectory evidence
continuity effect of Operator Response
```

### D-8: `docs/26_poc_runtime_object_graph.md`

Primary review points:

```text
Boundary-aware object graph
canonical object names
SliceDone expansion
Memory and Trajectory additions
remove direct Void response implication
bounded scope preservation
```

### D-9: `docs/27_claude_poc_implementation_prompt.md`

Primary review points:

```text
Boundary-aware implementation subset
NORMAL | UNKNOWN | VOID as PoC subset only
multi-input deterministic decision rules
four Boundary-aware scenarios
separate output fields
no automatic Void → DEFER rule
```

---

## 12. Update Method

Each Priority D document should be handled in the following order:

```text
1. Read the entire current document.
2. Identify still-valid mechanisms.
3. Identify unsafe or outdated conceptual wording.
4. Apply a focused alignment update.
5. Preserve the document's original responsibility and scope.
6. Add references to the newer canonical Priority A/B/C documents where useful.
7. Confirm no new Core stage or responsibility collapse was introduced.
```

Large simultaneous rewrites should be avoided.

One document should be stabilized before moving to the next.

---

## 13. Acceptance Criteria

Priority D is complete when:

```text
1. All nine legacy documents use the reviewed Core mapping.
2. Boundary and Boundary State remain Slice-derived evidence.
3. Void is not represented as an actor or automatic response owner.
4. Stability remains separate from Operator Response.
5. RESLICE, JUMP, DEFER, and STOP have distinct continuity meanings.
6. Memory and Trajectory preserve reclassification and lineage.
7. API contracts expose responsibility separation.
8. PoC rules are explicitly implementation policy.
9. Cross-document terminology is consistent.
10. A final Priority D review finds no responsibility collapse.
```

---

## 14. Priority D Decision

Priority D will proceed as a careful legacy alignment pass.

The first implementation step is:

```text
Priority D-1
= align docs/18_void_defer_jump.md
```

This is the highest-priority legacy correction because it contains the greatest risk of mixing:

```text
Void condition
Void evidence
Defer
Re-Slice
Jump
Stop
```

The alignment must preserve useful runtime handling while restoring the reviewed responsibility boundaries.