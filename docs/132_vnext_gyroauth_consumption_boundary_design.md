# 132. vNext GyroAuth Consumption Boundary Design

---

## 1. Purpose

This document defines integration gate D inside GyroOS:

```text
GyroOS public experimental record API
↓
GyroAuth read-only consumption boundary
```

The purpose is to define what GyroOS may expose for GyroAuth consumption without introducing a GyroAuth dependency into GyroOS.

The layer direction remains:

```text
Gyro Logic
↓
GyroOS
↓
GyroAuth
```

GyroOS must not import GyroAuth models, states, policies, or decisions.

---

## 2. Verified Source Boundary

The verified GyroOS source contract is:

```text
GET /vnext/experimental/records/{record_id}
GET /vnext/experimental/records
```

The source returns opaque:

```text
ExperimentalRecordEnvelope
```

Initial GyroAuth consumption is read-only.

The initial D scope must not authorize GyroAuth-specific use of:

```text
POST /vnext/experimental/records
DELETE /vnext/experimental/records/{record_id}
```

---

## 3. Contract Separation

The following remain distinct:

```text
ExperimentalRecordEnvelope
≠ authentication request

ExperimentalRecordEnvelope
≠ authentication result

StabilityScene
≠ AUTH_STABLE

ContinuityRelationRecord
≠ identity proof

TrajectoryGraph
≠ authentication trajectory

RuntimeSnapshot
≠ authentication session state
```

GyroOS exposes source records only. Interpretation remains consumer-owned.

---

## 4. D1 Contract Models and Settings

GyroOS should define transport-neutral consumer contract models:

```text
ExperimentalConsumerReference
ExperimentalConsumerSnapshot
ExperimentalConsumptionRequest
ExperimentalConsumptionResult
ExperimentalConsumptionSettings
ExperimentalHttpTransportSettings
```

These models describe read-only inspection mechanics only.

They must not define:

```text
auth_state
auth_score
next_action
identity continuity
attack classification
trajectory continuity
```

`accepted_for_inspection` means only that an explicit record passed boundary checks.

---

## 5. D2 Caller-supplied Envelope Adapter and Service

GyroOS should provide:

```text
CallerSuppliedExperimentalEnvelopeAdapter
ExperimentalRecordInspectionService
```

Responsibilities:

```text
adapt one supplied envelope
verify explicit record ID
verify optional process ID
verify optional record type
copy payload and metadata
return inspection-only result
```

Non-responsibilities:

```text
calculate authentication score
select authentication state
select next action
infer identity continuity
infer attack
infer recovery
persist consumer state
```

---

## 6. D3 Optional Read-only HTTP Transport Adapter

GyroOS may provide a reference client for its own verified API:

```text
ExperimentalReadOnlyHttpClient
ExperimentalRecordHttpAdapter
```

Allowed operation:

```text
GET /vnext/experimental/records/{record_id}
```

No POST, PUT, PATCH, or DELETE operation is part of D3.

Transport authentication remains service-access authentication only.

```text
transport bearer token
≠ end-user authentication evidence
```

---

## 7. Mapping Boundary

The following automatic mappings are not approved:

```text
StabilityScene → AUTH_STABLE
ContinuityRelationRecord → identity continuity
TrajectoryGraph → authentication trajectory
RuntimeSnapshot → authentication context
DifferenceObject → deviation risk
BoundaryEvaluation → attack classification
OperatorResponse → next action
```

Future interpretation must be explicit and owned by GyroAuth.

---

## 8. Error Boundary

The boundary must distinguish:

```text
invalid supplied envelope
record ID mismatch
process ID mismatch
record type mismatch
record unavailable
transport failure
non-success HTTP response
invalid JSON response
```

These errors must not become authentication outcomes.

---

## 9. Persistence Boundary

Initial D remains request-local and inspection-only.

It must not write to:

```text
current SQLite schema
Runtime history
canonical experimental persistence
authentication session storage
identity trajectory storage
```

---

## 10. Proposed Sequence

```text
D1. consumer contract models and settings
↓
Review
↓
D2. caller-supplied envelope adapter and inspection service
↓
Review
↓
D3. optional read-only HTTP transport adapter
↓
Actions verification
↓
D Review
```

---

## 11. Final Design Decision

```text
D GyroAuth consumption boundary design
= COMPLETE

Repository ownership
= GYROOS

Initial direction
= READ-ONLY

Automatic authentication mapping
= NOT APPROVED

GyroAuth dependency in GyroOS
= NOT APPROVED

Canonical persistence
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```
