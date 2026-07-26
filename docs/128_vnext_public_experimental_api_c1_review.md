# 128. vNext Public Experimental API C1 Review

---

## 1. Scope

Reviewed:

```text
ExperimentalApiSettings
ExperimentalApiModel
ExperimentalRecordCreateRequest
ExperimentalRecordResponse
ExperimentalRecordListResponse
ExperimentalApiError
```

The review covers public experimental record API settings and transport models only.

---

## 2. Namespace and Runtime Separation

C1 introduces no routes and does not modify:

```text
POST /loop/step
RuntimeSettings
ProcessExecutor
StabilityEngine
OperatorResponse selection
```

Decision:

```text
Runtime separation
= ACCEPTED
```

---

## 3. Public Record Boundary

The create request converts only to:

```text
ExperimentalRecordEnvelope
```

The public model does not reconstruct or expose typed Semantic, Readability, Continuity, Trajectory, or Runtime records.

Decision:

```text
Opaque envelope boundary
= ACCEPTED

Typed reconstruction absence
= ACCEPTED
```

---

## 4. Resource Limit Boundary

Settings define only:

```text
max_payload_bytes
max_metadata_bytes
max_list_results
max_record_id_length
max_record_type_length
```

They do not define canonical authority, current/latest selection, ordering, Runtime behavior, persistence backend, or GyroAuth mapping.

Decision:

```text
Resource settings boundary
= ACCEPTED
```

---

## 5. Validation Boundary

The request rejects:

```text
empty record IDs and record types
extra fields
oversized IDs
oversized record type labels
oversized payloads
oversized metadata
non-JSON-serializable values
```

It does not validate `record_type` against a registry.

Decision:

```text
Transport validation boundary
= ACCEPTED
```

---

## 6. Ordering Boundary

List responses state:

```text
ordering = UNSPECIFIED
```

This does not define establishment, Runtime, Trajectory, revision, or canonical order.

Decision:

```text
Ordering non-semantics
= ACCEPTED
```

---

## 7. Final Decision

```text
C1 experimental API settings and public models
= COMPLETE

Public envelope contract
= ACCEPTED

Resource limits
= ACCEPTED

Runtime isolation
= ACCEPTED

Persistence backend selection
= NOT PART OF C1

Route exposure
= NOT PART OF C1

Critical design blocker
= NONE IDENTIFIED
```

Proceed to:

```text
C2 repository dependency / provider boundary
```
