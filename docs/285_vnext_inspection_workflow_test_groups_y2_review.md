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
= VERIFIED
```

## 3. Coverage Boundary

The test paths were moved from the existing workflow command into the three group files.

No wildcard test discovery replaces the explicit list.

The workflow still executes the selected files through one pytest invocation.

Decision:

```text
Explicit auditable coverage
= VERIFIED
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
= VERIFIED

Test-group change triggering
= VERIFIED
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

## 7. GitHub Actions Verification

Verified run:

```text
run_id: 30328656282
job: test-and-run-poc
status: completed
conclusion: success
```

Verified successful steps:

```text
Run bounded Runtime and production hardening tests
Generate PoC result artifacts
Verify PoC result artifact count
Upload PoC result artifacts
```

Decision:

```text
GitHub Actions verification
= VERIFIED
```

## 8. Final Decision

```text
Y2 checked-in test-group files
= VERIFIED

Priority F workflow migration
= VERIFIED

Explicit auditable coverage
= VERIFIED

GitHub Actions verification
= VERIFIED

Y2
= COMPLETE
```

## 9. Next Step

```text
Proceed to Y3 Dedicated Inspection Router.
```
