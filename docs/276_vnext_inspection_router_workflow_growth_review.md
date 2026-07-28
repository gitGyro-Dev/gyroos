# 276. vNext Inspection Router and Workflow Growth Review

## 1. Scope

This document is the X4 deliverable for integration gate X.

It reviews growth in:

```text
app/vnext/experimental_api_routes.py
.github/workflows/priority-f-poc.yml
```

This review does not change routes, workflow commands, test discovery, Runtime behavior, persistence, or public API contracts.

## 2. Router State

`experimental_api_routes.py` currently contains:

```text
shared experimental-record CRUD
consumer compatibility endpoint
inspection endpoints F through W
inspection model imports
inspection service imports
service instances
endpoint-local error translation
```

The file remains functionally explicit, but inspection-related imports, service instances, and route functions now dominate the module.

Decision:

```text
Router correctness
= ACCEPTED

Router readability
= DEGRADED BY SIZE

Immediate router rewrite
= NOT APPROVED
```

## 3. Router Risks

The main risks are:

```text
incorrect import selection
incorrect service instance binding
incorrect response model binding
incorrect error code or phase
omitted endpoint during future changes
high review cost for adjacent contracts
```

The risk is caused by repeated contract wiring, not by the FastAPI router mechanism itself.

## 4. Simple Router Direction

The preferred future structure is limited router decomposition by responsibility:

```text
experimental_api_routes.py
  ├─ experimental record and compatibility routes
  └─ includes one inspection router

inspection_api_routes.py
  └─ inspection POST endpoints F-W
```

A second split inside the inspection router is not approved at this stage.

The objective is only to separate unrelated experimental-record CRUD from the inspection contract family.

Decision:

```text
One dedicated inspection router
= APPROVED AS A FUTURE CANDIDATE

One router module per inspection contract
= NOT APPROVED

Dynamic route registration framework
= NOT APPROVED

Automatic error-code generation
= NOT APPROVED
```

## 5. Workflow State

The Priority F workflow uses one explicit pytest command containing the bounded Runtime, production-hardening, vNext, and inspection tests.

Advantages:

```text
fully visible test scope
explicit auditability
no hidden discovery rules
clear failure location
```

Current problem:

```text
the command is too long to review safely
inspection test additions are easy to omit
copy-and-paste maintenance cost is high
```

Decision:

```text
Workflow test coverage
= ACCEPTED

Workflow command readability
= POOR

Implicit unrestricted test discovery
= NOT APPROVED
```

## 6. Simple Workflow Direction

The preferred simplification is to move explicit test paths into small checked-in pytest argument files or shell scripts while preserving the exact visible scope.

Preferred form:

```text
tests/test_groups/runtime_hardening.txt
tests/test_groups/vnext_core.txt
tests/test_groups/vnext_inspection.txt
```

or an equivalent checked-in script that invokes the same explicit files.

The workflow should then call a small number of auditable commands.

Example direction:

```text
python -m pytest $(cat tests/test_groups/runtime_hardening.txt) -q
python -m pytest $(cat tests/test_groups/vnext_core.txt) -q
python -m pytest $(cat tests/test_groups/vnext_inspection.txt) -q
```

The exact implementation requires a separate approved change and tests.

Decision:

```text
Checked-in explicit test groups
= APPROVED AS A FUTURE CANDIDATE

pytest tests/vnext without explicit bounds
= NOT APPROVED

Automatic file-glob expansion without review
= NOT APPROVED

Removing contract-specific tests
= NOT APPROVED
```

## 7. Minimal Change Order

Any future X4 implementation should proceed in this order:

```text
1. add explicit test-group files and validation tests
2. update workflow without changing covered test paths
3. verify Actions success
4. add one inspection router module
5. move existing inspection routes without endpoint changes
6. run all API and workflow tests
7. compare route inventory before and after
```

Router and workflow restructuring must not be performed in one unreviewed change.

## 8. Boundaries

Any restructuring must preserve:

```text
all existing endpoint paths
all request and response models
all status codes
all error codes and phases
all authentication dependencies
all request-local semantics
no inspection retrieval routes
no inspection persistence
no Runtime mutation
no GyroAuth dependency
```

## 9. Final Decision

```text
X4 router and workflow growth review
= COMPLETE

Current router behavior
= ACCEPTED

Current router size
= MAINTENANCE RISK

Dedicated inspection router
= APPROVED AS A FUTURE CANDIDATE

Current explicit workflow coverage
= ACCEPTED

Current workflow command length
= MAINTENANCE RISK

Checked-in explicit test groups
= APPROVED AS A FUTURE CANDIDATE

Immediate implementation change
= NOT YET APPROVED

Runtime and persistence boundaries
= UNCHANGED
```

## 10. Next Step

```text
X5: Create a single inspection API contract index for all approved experimental POST endpoints and prohibited retrieval or mutation operations.
```
