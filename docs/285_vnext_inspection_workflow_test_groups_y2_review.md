# 285. vNext Inspection Workflow Test Groups Y2 Review

## 1. Scope

Reviewed implementation:

```text
tests/test_groups/runtime_hardening.txt
tests/test_groups/vnext_core.txt
tests/test_groups/vnext_inspection.txt
.github/workflows/priority-f-poc.yml
```

Y2 replaces one long inline pytest argument list with checked-in explicit test-group files.

## 2. Test Group Structure

The workflow now reads three explicit groups:

```text
runtime_hardening.txt
vnext_core.txt
vnext_inspection.txt
```

Each file contains one test path per line.

Decision:

```text
Checked-in explicit test groups
= ACCEPTED
```

## 3. Coverage Boundary

The test paths were moved from the existing workflow command into the three group files.

No wildcard test discovery replaces the explicit list.

The workflow still executes the selected files through one pytest invocation.

Decision:

```text
Explicit auditable coverage
= PRESERVED
```

## 4. Workflow Boundary

The workflow uses:

```bash
mapfile -t test_files < <(
  cat \
    tests/test_groups/runtime_hardening.txt \
    tests/test_groups/vnext_core.txt \
    tests/test_groups/vnext_inspection.txt
)
python -m pytest "${test_files[@]}" -q
```

The test-group directory is included in push and pull-request path filters.

Decision:

```text
Priority F workflow readability
= IMPROVED

Test-group change triggering
= ENABLED
```

## 5. Non-Goals

Y2 does not introduce:

```text
automatic filesystem discovery
dynamic contract inference
parallel test partitioning
changed-test-only execution
contract-specific workflow generation
new test semantics
```

Decision:

```text
Workflow behavior expansion
= NOT INTRODUCED
```

## 6. Runtime and Contract Isolation

Unchanged:

```text
Structure → Slice → Stability
/loop/step
ProcessExecutor
OperatorResponse selection
current SQLite schema
Runtime history
experimental record CRUD
inspection request-local contracts
inspection API endpoints
```

Decision:

```text
Runtime isolation
= VERIFIED

Contract isolation
= VERIFIED
```

## 7. Current Verification State

```text
Y2 checked-in test-group files
= IMPLEMENTED

Priority F workflow migration
= IMPLEMENTED

Local behavior equivalence
= REVIEWED AT CONFIGURATION LEVEL

GitHub Actions verification
= PENDING

Y2
= COMPLETE AT IMPLEMENTATION / REVIEW LEVEL
```

Y2 becomes VERIFIED only after a successful Priority F workflow run confirms the grouped invocation.

## 8. Next Step

```text
Confirm the Priority F GitHub Actions run.
If successful, update Y2 to VERIFIED and proceed to Y3 Dedicated Inspection Router.
```
