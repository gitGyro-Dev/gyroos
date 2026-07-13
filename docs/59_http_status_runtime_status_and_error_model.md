# 59. HTTP Status, Runtime Status, and Error Model

---

## 1. Purpose

This document defines **Priority E-8: HTTP Status, Runtime Status, and Error Model** for the GyroOS API.

The purpose is to separate:

```text
HTTP transport result
API contract error
Runtime result
```

before implementation begins.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

HTTP semantics represent whether the API request was accepted and executed according to contract.
They do not redefine Gyro Logic and do not select an `OperatorResponse`.

---

## 2. E-8 Decision Summary

The first API uses three distinct result domains:

```text
1. HTTP Status
   = transport and API contract outcome

2. ApiError
   = structured explanation of API or execution-contract failure

3. LoopStepResult
   = valid Runtime result of one bounded Gyro Process
```

The canonical rule is:

```text
valid Runtime uncertainty or non-continuation
≠ HTTP error
```

The following may be returned with `200 OK`:

```text
Boundary State = UNKNOWN
Boundary State = VOID
StabilityStatus = NOT_EVALUABLE
StabilityStatus = VOID_RELATED
OperatorResponse = DEFER
OperatorResponse = JUMP
OperatorResponse = STOP
```

These results express Runtime meaning.
They do not indicate malformed API usage.

---

## 3. Domain Separation

### 3.1 HTTP Status

HTTP status indicates whether the endpoint request was accepted, validated, executed, and published according to the API contract.

It does not express:

```text
Stability
Boundary readability
Boundary State
Void evidence
OperatorResponse
Runtime Continuity
application verdict
```

### 3.2 ApiError

`ApiError` explains why a valid `LoopStepResult` could not be returned.

Examples:

```text
malformed JSON
unsupported enum
missing explicit reference
reference type mismatch
lineage conflict
idempotency conflict
current-scope conflict
payload limit violation
publication failure
unexpected implementation failure
```

### 3.3 LoopStepResult

`LoopStepResult` is the complete valid result group:

```text
SliceDone
+
StabilityResult
+
OperatorResponse
+
RuntimeContinuityResult
+
required lineage and created records
```

A valid `LoopStepResult` must not be wrapped as an `ApiError` merely because it contains uncertainty, unreadability, pending relation, non-continuous reconnection, or current-scope termination.

---

## 4. Canonical HTTP Status Mapping

The first API uses the following primary HTTP categories.

```text
200 OK
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
413 Payload Too Large
415 Unsupported Media Type
422 Unprocessable Content
429 Too Many Requests
500 Internal Server Error
503 Service Unavailable
504 Gateway Timeout
```

The implementation may support additional standard statuses later, but must preserve the responsibility boundaries defined here.

---

## 5. `200 OK`

Return `200 OK` when one complete valid Runtime result is available.

Examples:

```text
OperatorResponse = CONTINUE
OperatorResponse = ADJUST
OperatorResponse = RESLICE
OperatorResponse = JUMP
OperatorResponse = DEFER
OperatorResponse = STOP
```

Also valid:

```text
Boundary State = UNKNOWN
Boundary State = VOID
StabilityStatus = NOT_EVALUABLE
StabilityStatus = VOID_RELATED
continuability = false
```

### 5.1 Idempotent replay

A completed idempotent replay also returns `200 OK` with the original `LoopStepResult`.

Recommended observability fields:

```text
replayed = true
original_process_id
original_completed_at
```

These fields do not change Runtime semantics.

### 5.2 No partial success

The first API does not use `206 Partial Content` for incomplete Runtime result groups.

```text
partial Runtime result
≠ successful /loop/step result
```

---

## 6. `400 Bad Request`

Use `400 Bad Request` for malformed request syntax or basic request decoding failure.

Examples:

```text
invalid JSON
missing request body
invalid UTF-8 transport body
incorrect top-level JSON type
malformed query parameter
```

`400` is primarily a transport or serialization failure before canonical object validation.

It must not create:

```text
process_id
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
```

---

## 7. `401 Unauthorized`

Use `401 Unauthorized` when valid authentication credentials are required but absent or invalid.

Examples:

```text
missing access token
expired access token
invalid signature
unsupported authentication scheme
```

Authentication failure must not be converted into:

```text
Boundary State = VOID
StabilityStatus = UNSTABLE
OperatorResponse = STOP
```

GyroOS Runtime meaning is not a substitute for API access control.

---

## 8. `403 Forbidden`

Use `403 Forbidden` when the caller is authenticated but not authorized for the requested operation or record.

Examples:

```text
caller cannot execute /loop/step
caller cannot read referenced record
caller cannot invoke memory compression
caller cannot access the requested loop or trajectory
```

Authorization denial is an API error.
It is not an `OperatorResponse`.

---

## 9. `404 Not Found`

Use `404 Not Found` when an explicitly addressed endpoint resource or explicit retained reference does not exist in the caller-visible scope.

Examples:

```text
GET /process/{process_id} where process does not exist
GET /memory/record/{record_id} where record does not exist
source_ref does not resolve
parent_slice_ref does not resolve
requested_by_response_ref does not resolve
```

### 9.1 Missing reference is not Void

```text
missing API record
≠ VoidEvidence
≠ Boundary State = VOID
```

A storage lookup failure must not create a Runtime Void classification.

### 9.2 Hidden resource policy

An implementation may return `404` instead of `403` when revealing resource existence would violate its security policy.
That transport policy must not change Runtime semantics.

---

## 10. `409 Conflict`

Use `409 Conflict` when the request is individually well-formed but conflicts with current identity, lineage, idempotency, or current-scope state.

Canonical examples:

```text
same idempotency key + different canonical request digest
expected_current_scope_ref mismatch
embedded and referenced object share identity but differ in content
request_id reused for different canonical request
lineage target already superseded in the submitted current scope
same prepared RESLICE request already consumed when single-use policy applies
in-progress duplicate idempotent execution
```

A `409` conflict must not be converted into:

```text
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Conflict resolution belongs to the API caller or explicit retry policy.

---

## 11. `413 Payload Too Large`

Use `413 Payload Too Large` when the transport or canonical request exceeds configured size limits.

Examples:

```text
request body exceeds max_payload_bytes
embedded evidence collection exceeds total payload allowance
single metadata object exceeds extension limit
```

This is an admission failure.
No Process artifact is created.

The server must not silently compress request content to make the request acceptable.

---

## 12. `415 Unsupported Media Type`

Use `415 Unsupported Media Type` when the request content type is unsupported.

Initial supported request type:

```text
application/json
```

This is a transport failure and produces no Runtime artifacts.

---

## 13. `422 Unprocessable Content`

Use `422 Unprocessable Content` when the serialized request is structurally readable but violates the canonical API object contract.

Examples:

```text
unsupported canonical enum
confidence outside 0.0 to 1.0
NaN or Infinity
source_type and source_ref type mismatch
RESLICE without parent lineage
RESLICE without prior RESLICE OperatorResponse
VOID Boundary State without identifiable Boundary
invalid Response / Continuity pair in submitted imported result
reference list contains null or duplicate entries where prohibited
metadata attempts to override canonical fields
```

### 13.1 `400` versus `422`

```text
400
= request could not be decoded as the expected request representation

422
= request was decoded, but canonical field or relation validation failed
```

### 13.2 Validation error is not Runtime uncertainty

```text
invalid VOID classification
→ 422

valid Boundary State = UNKNOWN
→ 200
```

---

## 14. `429 Too Many Requests`

Use `429 Too Many Requests` when execution is rejected by transport rate policy or admission capacity policy.

Examples:

```text
caller rate limit exceeded
concurrent request quota exceeded
bounded admission queue full
```

Recommended header:

```text
Retry-After
```

A `429` result is not:

```text
OperatorResponse = DEFER
OperatorResponse = STOP
Gyro-OOM Damper action
```

Runtime pressure observed during a valid Process and API admission pressure are different responsibilities.

---

## 15. `500 Internal Server Error`

Use `500 Internal Server Error` for unexpected implementation failures where no more specific contract status applies.

Examples:

```text
unexpected engine exception
serialization bug in generated result
internal invariant violation
atomic publication failure with unknown cause
unhandled storage adapter failure
```

### 15.1 No response fallback

The implementation must not convert internal failure into a fabricated Runtime result.

Incorrect:

```text
LoopController produced invalid RESLICE result
→ replace with STOP
```

Correct:

```text
invalid generated result
→ do not publish completed Process
→ return structured 500-class ApiError
```

---

## 16. `503 Service Unavailable`

Use `503 Service Unavailable` when the API cannot currently execute the request because a required subsystem is unavailable before or during bounded execution.

Examples:

```text
required record store unavailable
policy registry unavailable
reference resolver unavailable
atomic publication service unavailable
runtime temporarily disabled
```

The response may include a bounded retry recommendation.

A `503` is not an `OperatorResponse = DEFER`.

---

## 17. `504 Gateway Timeout`

Use `504 Gateway Timeout` when the serving gateway or synchronous execution boundary expires without a complete publishable result.

The first API must not translate timeout into:

```text
DEFER
STOP
JUMP
```

No incomplete `LoopStepResult` is returned as success.

If the implementation retains a diagnostic execution-attempt record, it must remain distinct from a completed Process result.

---

## 18. Canonical `ApiError` Object

```python
class ApiError:
    error_id: str
    error_code: str
    message: str

    category: ApiErrorCategory
    phase: ApiExecutionPhase | None

    field_path: str | None
    related_refs: list[str]
    validation_issues: list[ValidationIssue]

    request_id: str | None
    loop_id: str | None
    client_trace_id: str | None

    retryable: bool
    retry_after_ms: int | None

    documentation_ref: str | None
    details: dict
    occurred_at: str
```

### 18.1 Required fields

```text
error_id
error_code
message
category
related_refs
validation_issues
retryable
occurred_at
```

### 18.2 Optional and nullable fields

```text
phase
field_path
request_id
loop_id
client_trace_id
retry_after_ms
documentation_ref
details
```

### 18.3 Restrictions

`ApiError` must not contain fields pretending to be:

```text
StabilityResult
BoundaryStateRecord
VoidEvidence
OperatorResponse
RuntimeContinuityResult
```

An `error_code` must not use canonical OperatorResponse values as error meanings.

---

## 19. ApiErrorCategory

Canonical initial categories:

```text
TRANSPORT
AUTHENTICATION
AUTHORIZATION
NOT_FOUND
VALIDATION
IDENTITY_CONFLICT
CURRENT_SCOPE_CONFLICT
RATE_LIMIT
DEPENDENCY_UNAVAILABLE
TIMEOUT
INTERNAL
```

These categories are API implementation classifications.
They are not Gyro Logic or Runtime classifications.

---

## 20. ApiExecutionPhase

Canonical phase values align with the `/loop/step` execution contract:

```text
TRANSPORT_ADMISSION
REQUEST_DESERIALIZATION
REQUEST_VALIDATION
IDEMPOTENCY_CHECK
REFERENCE_RESOLUTION
PRECONDITION_VALIDATION
PROCESS_RESERVATION
SLICE_EXECUTION
SLICE_DONE_VALIDATION
STABILITY_READING
RESPONSE_SELECTION
CONTINUITY_CONSTRUCTION
NEXT_EFFECT_PREPARATION
RECORD_PREPARATION
RESULT_VALIDATION
ATOMIC_PUBLICATION
RESPONSE_SERIALIZATION
```

The phase helps locate failure responsibility.
It must not imply an OperatorResponse.

---

## 21. ValidationIssue

```python
class ValidationIssue:
    issue_code: str
    message: str
    field_path: str | None
    object_ref: str | None
    expected: dict | None
    actual: dict | None
```

Rules:

```text
validation_issues may contain multiple independent issues
field_path uses one documented path notation
actual must avoid exposing secrets or large raw payloads
```

Recommended field path notation for the first API:

```text
JSON Pointer
```

Example:

```text
/slice_request/source_ref
/operator_response/next_request/mode
```

---

## 22. Error Code Naming

`error_code` must be stable, machine-readable, and independent from localized message text.

Recommended format:

```text
GYRO_API_<CATEGORY>_<SPECIFIC_CONDITION>
```

Examples:

```text
GYRO_API_TRANSPORT_INVALID_JSON
GYRO_API_VALIDATION_UNSUPPORTED_ENUM
GYRO_API_VALIDATION_REFERENCE_TYPE_MISMATCH
GYRO_API_VALIDATION_INVALID_RESLICE_LINEAGE
GYRO_API_VALIDATION_VOID_WITHOUT_BOUNDARY
GYRO_API_IDENTITY_IDEMPOTENCY_CONFLICT
GYRO_API_SCOPE_CURRENT_SCOPE_CONFLICT
GYRO_API_NOT_FOUND_RECORD
GYRO_API_RATE_LIMIT_EXCEEDED
GYRO_API_DEPENDENCY_RECORD_STORE_UNAVAILABLE
GYRO_API_INTERNAL_RESULT_INVARIANT_VIOLATION
```

Error codes must not be changed casually after publication.

---

## 23. Retryability Rules

`retryable` means the same canonical request may reasonably succeed later without changing its semantic content.

Typical candidates:

```text
429 rate limit
503 temporary dependency unavailable
504 timeout when idempotency protection exists
in-progress idempotent duplicate
```

Typically non-retryable without request correction:

```text
400 malformed request
401 invalid credentials
403 forbidden
404 missing immutable reference
409 same idempotency key with different digest
422 canonical validation failure
```

Retryability remains condition-specific.
For example, a `404` for an eventually materialized external reference may be retryable only when the endpoint contract explicitly permits that behavior.

---

## 24. Idempotency and Error Results

### 24.1 Completed result

```text
same key + same digest + completed result
→ 200 with original LoopStepResult
```

### 24.2 In-progress request

```text
same key + same digest + execution in progress
→ bounded 409 conflict or documented in-progress error
```

The first implementation should not hold the connection indefinitely.

### 24.3 Conflicting key reuse

```text
same key + different digest
→ 409
```

### 24.4 Failed prior attempt

A failed attempt must not be replayed as a valid completed result.
The implementation may allow a protected retry using the same key when no completed result was published, provided the policy is documented and duplicate concurrent execution is prevented.

---

## 25. Publication and Failure Semantics

The success publication rule remains:

```text
complete valid result group
→ publish atomically
→ return 200
```

Failure rule:

```text
incomplete or inconsistent result group
→ publish no completed Process result
→ return ApiError
```

Required result group:

```text
ProcessRecord
SliceDone
StabilityResult
OperatorResponse
RuntimeContinuityResult
required UpdateDecision or NextProcessPreparation
required Memory / Trajectory records
```

A diagnostic failed-attempt record may be retained internally, but it must not appear as a completed Runtime result.

---

## 26. Support Endpoint Status Rules

### 26.1 Read endpoints

Examples:

```text
GET /process/{process_id}
GET /memory/record/{record_id}
GET /trajectory/{trajectory_id}
```

Typical statuses:

```text
200 = resource returned
401 = authentication required
403 = not authorized
404 = resource not found or intentionally hidden
```

### 26.2 Memory operation endpoints

```text
POST /memory/retrieve
POST /memory/compress
```

Typical statuses:

```text
200 = synchronous operation completed
202 = explicitly accepted asynchronous mode, only if later introduced
404 = referenced record missing
409 = current-scope or operation conflict
422 = invalid operation contract
```

The first bounded implementation should prefer synchronous `200` behavior and avoid background operation complexity.

### 26.3 Re-Slice execution endpoint

```text
POST /reslice/execute
```

Typical statuses:

```text
200 = one bounded Re-Slice Process completed
404 = required prior record missing
409 = prepared request conflict or already consumed
422 = invalid Re-Slice lineage or request relation
```

`/reslice/execute` must not decide `RESLICE`.

---

## 27. Response Headers

Recommended response headers:

```text
Content-Type: application/json
X-Gyro-Request-Id
X-Gyro-Process-Id          # successful new execution only
X-Gyro-Idempotent-Replay   # true when replayed
X-Gyro-API-Version
X-Gyro-Runtime-Version
Retry-After                # when applicable
```

Headers are observability and protocol metadata.
They must not replace canonical body identity or lineage fields.

---

## 28. Error Logging and Information Exposure

Server logs may retain implementation diagnostics, but API errors must avoid exposing:

```text
secrets
credentials
internal stack traces
private record content
raw policy internals
unbounded payload copies
```

The client-facing error should include enough information to correct the request or identify the failed reference without revealing protected internals.

`error_id` should allow server-side correlation with detailed logs.

---

## 29. Application Boundary

The API error model must not return application verdicts such as:

```text
authenticated
access_denied
fraud
malware
approved
rejected
```

`401` and `403` express access to the GyroOS API itself.
They do not express a GyroAuth authentication result or another application-layer decision.

---

## 30. Acceptance Criteria

Priority E-8 is accepted when:

```text
1. HTTP status is separated from Runtime result.
2. UNKNOWN, VOID, NOT_EVALUABLE, DEFER, JUMP, and STOP may remain valid 200 outcomes.
3. Missing API references are not converted into VoidEvidence.
4. Access-control failure is not converted into Stability or OperatorResponse.
5. Validation errors use 400 or 422 according to decoding versus semantic failure.
6. Identity, idempotency, and current-scope conflicts use 409.
7. Rate admission failure is not converted into DEFER.
8. Timeout is not converted into STOP or DEFER.
9. Internal failures do not fabricate fallback Runtime results.
10. ApiError remains distinct from all Runtime result objects.
11. Partial Runtime result groups are never returned as successful completion.
12. Retryability is explicit and condition-specific.
```

---

## 31. E-8 Decision

```text
Priority E-8
Status: ACCEPTED
```

The canonical first API relation is:

```text
HTTP 200
→ complete valid LoopStepResult

HTTP 4xx / 5xx
→ structured ApiError
```

with the invariant:

```text
Runtime uncertainty or non-continuation
≠ API failure
```

The next step is:

```text
Priority E-9
= API Implementation and Test Plan
```
