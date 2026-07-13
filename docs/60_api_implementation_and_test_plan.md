# 60. API Implementation and Test Plan

---

## 1. Purpose

This document defines **Priority E-9: API Implementation and Test Plan** for GyroOS.

The purpose is to convert the reviewed Priority E API contracts into a bounded, testable implementation plan without beginning a large or speculative implementation.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

The API represents one bounded Runtime execution of this Core.
It does not redefine Gyro Logic and does not implement a real operating system.

---

## 2. E-9 Decision Summary

The first implementation target is:

```text
Python
+
FastAPI
+
Pydantic
+
pytest
+
in-memory repositories
```

The first implementation must demonstrate:

```text
one HTTP request
=
one bounded Gyro Process
```

The primary endpoint remains:

```text
POST /loop/step
```

The initial implementation must preserve:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
≠ RuntimeContinuityResult
```

It must not begin with:

```text
persistent database
background worker
unbounded loop execution
distributed state
GyroAuth integration
production authentication
complex UI
```

---

## 3. Implementation Goal

The implementation is successful when a caller can:

```text
1. submit one canonical LoopStepRequest
2. execute one bounded Slice
3. receive one Boundary-aware SliceDone
4. receive one StabilityResult
5. receive one OperatorResponse
6. receive one RuntimeContinuityResult
7. retrieve the published Process result by explicit identity
8. verify lineage, references, and idempotency behavior
```

The implementation must make the Runtime relation visible and testable.
It does not need to model a complete OS.

---

## 4. First Implementation Scope

### 4.1 Required endpoints

```text
POST /loop/step
GET  /health
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

### 4.2 Recommended after the core path is stable

```text
GET /loop/state/{loop_id}
GET /loop/history/{loop_id}
GET /trajectory/{trajectory_id}
POST /memory/retrieve
```

### 4.3 Deferred until later

```text
POST /memory/compress
POST /reslice/execute
persistent database adapters
external object storage
background archive jobs
streaming endpoints
WebSocket
```

The deferred items must not block the first API implementation.

---

## 5. Proposed Repository Structure

Recommended initial structure:

```text
app/
  main.py
  api/
    routes/
      health.py
      loop.py
      process.py
      memory.py
    dependencies.py
    error_handlers.py
  models/
    enums.py
    request.py
    slice.py
    evidence.py
    stability.py
    response.py
    continuity.py
    result.py
    error.py
    records.py
  runtime/
    slice_engine.py
    stability_engine.py
    loop_controller.py
    continuity_builder.py
    update_engine.py
    process_executor.py
  validation/
    request_validator.py
    reference_validator.py
    lineage_validator.py
    result_validator.py
    current_scope_guard.py
    idempotency_guard.py
  repositories/
    interfaces.py
    memory_repository.py
    process_repository.py
    trajectory_repository.py
    idempotency_repository.py
  services/
    reference_resolver.py
    publication_service.py
    process_query_service.py
  config.py

tests/
  unit/
  integration/
  contract/
  scenarios/
  fixtures/
```

The exact path names may change.
The responsibility separation must not.

---

## 6. Core Module Responsibilities

### 6.1 API route layer

The route layer may:

```text
deserialize requests
invoke the process executor
map ApiError to HTTP status
serialize LoopStepResult
```

It must not:

```text
select OperatorResponse
classify Boundary State
calculate Stability directly
resolve hidden latest records
```

### 6.2 ProcessExecutor

`ProcessExecutor` coordinates the E-6 execution pipeline.

It owns orchestration, not Runtime judgment.

Candidate interface:

```python
class ProcessExecutor:
    def execute(self, request: LoopStepRequest) -> LoopStepResult:
        ...
```

### 6.3 SliceEngine

Input:

```text
RuntimeStructureInput
SliceRequest
resolved evidence
RuntimeLimits
```

Output:

```text
SliceDone
```

It may produce:

```text
representation
Deviation
SliceReadability
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
```

It must not select an OperatorResponse.

### 6.4 StabilityEngine

Input:

```text
SliceDone
applicable retained evidence
Stability policy
```

Output:

```text
StabilityResult
```

It must not select an OperatorResponse.

### 6.5 LoopController

The LoopController is the only component that selects:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Candidate interface:

```python
class LoopController:
    def select_response(
        self,
        slice_done: SliceDone,
        stability: StabilityResult,
        runtime_context: RuntimeDecisionContext,
    ) -> OperatorResponse:
        ...
```

The first implementation may use deterministic policy rules.
Those rules must be labeled as implementation policy, not Gyro Logic definitions.

### 6.6 ContinuityBuilder

Input:

```text
OperatorResponse
current SliceDone
prepared update or next request
```

Output:

```text
RuntimeContinuityResult
```

It records the effect of the selected response.
It does not select the response.

### 6.7 Repositories

The first implementation uses in-memory repositories behind interfaces.

Required interfaces should include:

```text
ProcessRepository
MemoryRecordRepository
TrajectoryRepository
IdempotencyRepository
CurrentScopeRepository
```

Storage strategy must remain replaceable.

```text
storage implementation
≠ Runtime meaning
```

---

## 7. Pydantic Model Strategy

Use strict canonical models for:

```text
LoopStepRequest
RuntimeStructureInput
SliceRequest
OperatorOrientation
SlicePolicy
RuntimeLimits
SliceDone
BoundaryEvidence
BoundaryStateRecord
ContextEvidence
VoidEvidence
StabilityResult
OperatorResponse
RuntimeContinuityResult
UpdateDecision
NextProcessPreparation
DeferredRelationRecord
LoopStepResult
ApiError
```

Recommended rules:

```text
forbid unknown fields in canonical objects
use enum classes for controlled vocabularies
use default_factory for collections
validate normalized values within 0.0 to 1.0
reject NaN and Infinity
use timezone-aware UTC timestamps
```

Extension data belongs only in documented `metadata` objects.

`metadata` must not override canonical fields.

---

## 8. Canonical Enum Set

The first implementation must use exactly the canonical values.

### SliceMode

```text
SLICE
RESLICE
```

### OperatorResponseType

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

### RuntimeContinuityType

```text
DIRECT_CONNECTION
ADJUSTED_CONNECTION
RESLICE_CONNECTION
JUMP_RECONNECTION
DEFERRED_PENDING_RELATION
STOPPED_FOR_CURRENT_SCOPE
```

### StabilityStatus

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED
```

### Initial BoundaryStateType

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

Compatibility aliases must not be accepted by canonical request models:

```text
CHANGE_ORIENTATION
RESLICE_CONTEXT
DEFER_VOID
VOID as OperatorResponse
```

---

## 9. Implementation Sequence

Implementation must proceed in small, reviewable steps.

### Phase I — Model foundation

```text
1. canonical enums
2. request models
3. SliceDone and evidence models
4. Stability, Response, and Continuity models
5. LoopStepResult and ApiError
```

Acceptance condition:

```text
all canonical examples serialize and deserialize
invalid aliases are rejected
normalized values are validated
```

### Phase II — In-memory identity and repositories

```text
1. server-owned ID generator
2. ProcessRepository
3. MemoryRecordRepository
4. IdempotencyRepository
5. CurrentScopeRepository
6. TrajectoryRepository
```

Acceptance condition:

```text
explicit references resolve by type
conflicting identities are rejected
no implicit latest-object lookup exists
```

### Phase III — Validation pipeline

```text
1. request-shape validation
2. reference resolution
3. lineage validation
4. current-scope guard
5. idempotency guard
6. result-group validation
```

Acceptance condition:

```text
invalid requests create no completed Process
invalid generated result groups are not published
```

### Phase IV — Minimal Runtime engines

```text
1. deterministic SliceEngine
2. deterministic StabilityEngine
3. deterministic LoopController policy
4. ContinuityBuilder
5. UpdateEngine stub where needed
```

Acceptance condition:

```text
one request executes one Slice
only LoopController selects OperatorResponse
Response and Continuity remain consistent
```

### Phase V — `/loop/step`

Implement the E-6 pipeline exactly.

Acceptance condition:

```text
valid request returns complete LoopStepResult
atomic publication succeeds
idempotent replay returns prior result
RESLICE prepares but does not execute the next Process
```

### Phase VI — Read endpoints

```text
GET /health
GET /process/{process_id}
GET /memory/record/{record_id}
```

Acceptance condition:

```text
only published records are returned as completed Runtime results
missing records return ApiError
```

### Phase VII — Optional support reads

```text
GET /loop/state/{loop_id}
GET /loop/history/{loop_id}
GET /trajectory/{trajectory_id}
POST /memory/retrieve
```

These begin only after the primary endpoint is stable.

---

## 10. Test Strategy

Tests are divided into five layers.

```text
1. model tests
2. unit tests
3. contract tests
4. integration tests
5. scenario tests
```

---

## 11. Model Tests

Model tests verify serialization and field constraints.

Required cases include:

```text
required field missing
unsupported enum
null in required field
empty required ID
NaN or Infinity
confidence outside 0.0 to 1.0
duplicate references
unknown canonical field
legacy response alias
```

Examples:

```text
OperatorResponseType = VOID
→ rejected
```

```text
BoundaryStateType = VOID
→ accepted when object relation is valid
```

Model tests do not validate every cross-object relation.

---

## 12. Unit Tests

### 12.1 ReferenceResolver

Test:

```text
correct identity and type
missing reference
wrong record type
conflicting embedded and referenced content
no implicit latest-object resolution
```

### 12.2 LineageValidator

Test:

```text
valid parent Process and Slice
self-cycle rejection
invalid RESLICE response lineage
Boundary State reclassification history
trajectory branch preservation
current-scope supersession without history deletion
```

### 12.3 StabilityEngine

Test:

```text
STABLE
ADAPTIVE
UNSTABLE
NOT_EVALUABLE
VOID_RELATED
```

Also verify:

```text
continuability = true
≠ automatic CONTINUE
```

### 12.4 LoopController

Test all six canonical responses.

Verify:

```text
ContextEvidence does not automatically select RESLICE
VOID does not automatically select DEFER
low Stability does not automatically select STOP
large Deviation does not automatically select JUMP
```

### 12.5 ContinuityBuilder

Verify exact mapping:

```text
CONTINUE → DIRECT_CONNECTION
ADJUST   → ADJUSTED_CONNECTION
RESLICE  → RESLICE_CONNECTION
JUMP     → JUMP_RECONNECTION
DEFER    → DEFERRED_PENDING_RELATION
STOP     → STOPPED_FOR_CURRENT_SCOPE
```

### 12.6 IdempotencyGuard

Test:

```text
same key + same digest + completed result
→ replay prior result

same key + different digest
→ conflict

same key + in-progress execution
→ bounded conflict
```

---

## 13. Contract Tests

Contract tests verify the public API contract independent of internal implementation details.

Required request contract tests:

```text
valid initial SLICE request
valid RESLICE request
invalid RESLICE without parent lineage
invalid source type mismatch
invalid current-scope expectation
```

Required response contract tests:

```text
complete LoopStepResult
all server-owned IDs present
all process_id values match
Response / Continuity mapping valid
created record refs resolve
```

Required error contract tests:

```text
400 invalid JSON
404 missing explicit reference
409 idempotency conflict
409 current-scope conflict
413 payload too large
415 unsupported media type
422 semantic validation error
429 admission limit
500 internal publication failure
503 dependency unavailable
504 timeout
```

Runtime outcomes must remain valid `200` responses where execution succeeded:

```text
UNKNOWN
VOID
NOT_EVALUABLE
DEFER
JUMP
STOP
```

---

## 14. Integration Tests

Integration tests exercise the full in-memory stack.

Required flow:

```text
HTTP request
→ FastAPI route
→ validation pipeline
→ ProcessExecutor
→ Runtime engines
→ result validation
→ atomic repository publication
→ HTTP response
```

Required cases:

```text
successful initial Process
idempotent replay
missing reference before Process creation
result validation failure with no completed publication
published Process retrieval
memory record retrieval
```

Verify that a failed request does not publish:

```text
ProcessRecord with COMPLETED status
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
```

---

## 15. Boundary-aware Scenario Tests

The first implementation must include at least four scenarios.

### Scenario A — Readable Boundary / NORMAL / CONTINUE

Expected characteristics:

```text
Boundary readable
target relation readable
BoundaryState = NORMAL
Stability = STABLE
OperatorResponse = CONTINUE
Continuity = DIRECT_CONNECTION
```

This is a PoC policy scenario, not a universal mapping rule.

### Scenario B — UNKNOWN / Context source / RESLICE

Expected characteristics:

```text
Boundary State = UNKNOWN
ContextEvidence available
policy selects RESLICE
next_request present
next_request.mode = RESLICE
current request executes no second Process
Continuity = RESLICE_CONNECTION
```

### Scenario C — VOID evidence / DEFER

Expected characteristics:

```text
identifiable Boundary
target relation unreadable or unconnectable
BoundaryState = VOID
VoidEvidence retained
policy selects DEFER
DeferredRelationRecord created
Continuity = DEFERRED_PENDING_RELATION
```

Verify:

```text
VoidEvidence has no deferred field
```

### Scenario D — Conflicting Boundary evidence / ADJUST or JUMP

Expected characteristics:

```text
conflicting Boundary evidence retained
policy selects ADJUST or JUMP
prior trajectory remains traceable
Continuity matches selected response
```

No Boundary State alone directly selects the response.

---

## 16. Negative Tests

The implementation must explicitly test unsafe interpretations.

```text
VOID as OperatorResponse
→ rejected

Context exists
→ no automatic RESLICE

VoidEvidence exists
→ no automatic DEFER

Stability value is low
→ no universal STOP

missing memory record
→ 404, not VoidEvidence

timeout
→ API error, not DEFER

invalid RESLICE result
→ publication failure, not fallback STOP

current-scope mismatch
→ 409, not JUMP or STOP
```

---

## 17. Atomic Publication Tests

The Process result group includes:

```text
ProcessRecord
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
required additional records
TrajectoryEdge
current-scope update
idempotency completion record
```

Test two outcomes only:

```text
all required records published consistently
```

or:

```text
no completed Process result published
```

A half-published successful Process is invalid.

The in-memory implementation may simulate a transaction using a staged write set followed by one commit operation.

---

## 18. Coverage Priorities

Coverage percentage alone is not the success criterion.

Highest-priority coverage areas:

```text
canonical enum rejection
reference type safety
lineage validation
Response ownership
Response / Continuity mapping
VOID Boundary rule
RESLICE next-request rule
DEFER pending-record separation
STOP current-scope semantics
idempotency
atomic publication
```

Lower-priority areas for the first implementation:

```text
storage performance
large-scale concurrency
external database behavior
complex compression algorithms
UI coverage
```

---

## 19. Test Fixtures

Recommended fixtures:

```text
base RuntimeStructureInput
base OperatorOrientation
base SlicePolicy
base RuntimeLimits
readable Boundary evidence
UNKNOWN Boundary State
VOID Boundary State and VoidEvidence
ContextEvidence
prior RESLICE OperatorResponse
valid parent Process and Slice
current-scope reference
```

Fixtures should preserve explicit identities and avoid implicit global latest-state assumptions.

---

## 20. Determinism and Replay

The first implementation should prefer deterministic engines and policies.

Record:

```text
request_digest
canonicalization_version
runtime_version
policy_version
created_at
```

Idempotent replay returns the prior published result.

Semantic replay tests should verify:

```text
same canonical semantic input
+
same policy version
→ equivalent decision path
```

Wall-clock timestamps and generated artifact IDs do not need to be identical for non-idempotent semantic replay.

---

## 21. Logging and Observability

The first implementation may log:

```text
request_id
loop_id
process_id
phase
error_id
runtime_version
policy_version
replayed
```

It must not log unrestricted payloads or evidence content by default.

Logs must not become the only source of lineage or Runtime identity.

```text
log entry
≠ Runtime record
```

---

## 22. Security and Input Safety

Even as a PoC, the API must apply:

```text
payload size limits
collection size limits
string length limits
strict enum validation
timeout boundary
no dynamic code execution from payload
no arbitrary object import
no unrestricted filesystem path input
```

Metadata and policy parameters must be treated as data, not executable instructions.

This is API implementation safety.
It is not GyroAuth.

---

## 23. Dependency Plan

Recommended initial dependencies:

```text
fastapi
uvicorn
pydantic
pytest
httpx
```

Optional:

```text
pytest-cov
ruff
mypy
```

Avoid adding database, queue, cache-server, or UI dependencies before the core contract tests pass.

---

## 24. CI Candidate

A later GitHub Actions workflow may run:

```text
ruff check
mypy
pytest
```

Initial required gate:

```text
all contract tests pass
all scenario tests pass
no legacy enum appears in canonical models
```

CI design is an implementation follow-up and is not required to complete Priority E-9.

---

## 25. Implementation Non-goals

The first implementation must not attempt:

```text
real OS scheduling
real process isolation
production-grade persistence
distributed transaction
multi-region replication
GyroAuth authentication verdicts
malware or vulnerability verdicts
autonomous unbounded reslicing
automatic application policy generation
full Dynamic Equivalence engine
production privacy compliance claims
```

These may require separate design priorities.

---

## 26. Acceptance Criteria

Priority E-9 is accepted when the implementation plan ensures:

```text
1. the first implementation is bounded and minimal
2. one request executes one Process
3. canonical schemas directly map to modules
4. only LoopController selects OperatorResponse
5. Response and Continuity remain separate and consistent
6. Boundary, Context, and Void evidence remain separate
7. explicit references and lineage are testable
8. invalid requests publish no completed Process
9. valid Runtime uncertainty remains a 200 result
10. idempotency and atomic publication have tests
11. four Boundary-aware scenarios are covered
12. deferred features do not block the core implementation
```

---

## 27. Recommended First Coding Milestone

The first coding milestone should contain only:

```text
canonical Pydantic models
in-memory repositories
validation skeleton
minimal deterministic Runtime engines
POST /loop/step
GET /health
GET /process/{process_id}
contract and scenario tests
```

Do not implement optional support operations in the first milestone.

---

## 28. E-9 Decision

```text
Priority E-9
Status: ACCEPTED
```

The API contract is ready for a final Priority E cross-document review before implementation begins.

Next:

```text
Priority E-10
= Priority E Cross-document Review and Refinement
```
