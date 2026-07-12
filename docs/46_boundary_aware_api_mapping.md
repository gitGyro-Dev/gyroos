# 46. Boundary-aware API Mapping

---

## 1. Purpose

This document defines the **Boundary-aware API Mapping** of GyroOS after the Gyro Logic v3.1 Core Definition refinement and the Priority B Runtime Continuity refinement.

The purpose is not to redefine Gyro Logic.

The invariant Core remains:

```text
Structure
↓
Slice
↓
Stability
```

Boundary and Boundary State remain Slice-derived runtime relations.

Operator Response remains responsible for selecting the next Runtime Continuity relation.

This document addresses:

```text
Priority C-8: Boundary-aware API Mapping
```

---

## 2. Core API Principle

The canonical GyroOS runtime endpoint remains:

```text
POST /loop/step
```

`/loop/step` represents one bounded Gyro Process and one Operator Response.

A Boundary-aware `/loop/step` must preserve the following conceptual separation:

```text
SliceDone
≠ StabilityResult
≠ OperatorResponse
```

Boundary-aware API design must not collapse these into a single result such as:

```json
{
  "boundary": "normal",
  "decision": "continue"
}
```

Such a response hides:

```text
how Boundary became readable
how Boundary State was classified
whether the path was stable
which evidence was considered
why the Operator Response was selected
```

---

## 3. Boundary-aware API Mapping

The safe high-level relation is:

```text
POST /loop/step
↓
Runtime Structure
↓
Slice {
  Operator Orientation
  Slice Policy
  slice-ing
  slice-done
}
↓
Boundary-aware SliceDone
↓
StabilityResult
↓
Loop Controller / Operator Response
↓
Runtime Continuity result
```

Boundary is not inserted as an additional API stage.

Incorrect:

```text
Structure
→ Slice
→ Boundary API
→ Stability
```

Correct:

```text
Boundary evidence is included in or referenced by SliceDone.
```

---

## 4. Request Mapping

A Boundary-aware `/loop/step` request may include:

```json
{
  "process_id": "process-001",
  "structure": {
    "structure_id": "structure-001",
    "current_mode": {},
    "retained_conditions": {},
    "continuity_refs": []
  },
  "slice": {
    "orientation": {
      "orientation_id": "orientation-001",
      "target": "relation-x",
      "direction": "distinguish"
    },
    "policy": {
      "policy_id": "policy-001",
      "resolution": "bounded",
      "dimensions": [],
      "constraints": {}
    }
  },
  "context_refs": [],
  "trajectory_ref": "trajectory-001",
  "runtime_limits": {}
}
```

The request may provide conditions under which a Boundary can become readable.

However:

```text
request does not directly declare the theoretical Boundary
request does not directly declare Stability
request does not directly declare Operator Response
```

An application may provide candidate distinctions or policy constraints, but GyroOS must preserve the distinction between:

```text
candidate input
and
Boundary made readable through Slice
```

---

## 5. Boundary-aware SliceDone Mapping

A candidate API representation is:

```json
{
  "slice_done": {
    "slice_id": "slice-001",
    "process_id": "process-001",
    "representation": {},
    "deviation": {},
    "readability": {
      "status": "readable",
      "evidence_refs": []
    },
    "boundaries": [],
    "boundary_states": [],
    "context_refs": [],
    "void_refs": [],
    "orientation_ref": "orientation-001",
    "slice_policy_ref": "policy-001",
    "trajectory_ref": "trajectory-001"
  }
}
```

Important:

```text
Boundary-aware
≠ Boundary-required
```

Therefore, the following is valid:

```json
{
  "boundaries": [],
  "boundary_states": []
}
```

when no Boundary became sufficiently readable under the current Slice.

---

## 6. Boundary Evidence Object

A Boundary evidence object may be represented as:

```json
{
  "boundary_id": "boundary-001",
  "source_slice_id": "slice-001",
  "distinction_type": "relation",
  "subject_ref": "object-a",
  "counterpart_ref": "object-b",
  "readability": "readable",
  "confidence": 0.74,
  "evidence_refs": [
    "evidence-001"
  ],
  "context_refs": [],
  "resolution": "bounded",
  "lineage": {
    "refined_from": null,
    "conflicts_with": [],
    "coexists_with": []
  }
}
```

This object is an implementation representation.

It is not a replacement for the Gyro Logic definition of Boundary.

The field:

```text
confidence
```

must not be treated as Stability.

```text
Boundary confidence ≠ Stability value
```

---

## 7. Boundary State Object

A Boundary State may be represented as:

```json
{
  "boundary_state_id": "boundary-state-001",
  "boundary_ref": "boundary-001",
  "state": "UNKNOWN",
  "provisional": true,
  "evidence_refs": [
    "evidence-001"
  ],
  "context_refs": [],
  "classified_under": {
    "slice_id": "slice-001",
    "orientation_ref": "orientation-001",
    "slice_policy_ref": "policy-001",
    "trajectory_ref": "trajectory-001"
  },
  "lineage": {
    "reclassified_from": null,
    "supersedes_for_current_scope": null
  }
}
```

Candidate state values include:

```text
NORMAL
NON
UN
ABSENCE
BLANK
UNKNOWN
VOID
```

These are provisional runtime classifications.

They are not HTTP status codes.

They are not Stability statuses.

They are not Operator Responses.

---

## 8. Void API Separation

The API must distinguish:

```text
Void as Boundary State
Void evidence
Void reference
DEFER_VOID response
```

Example:

```json
{
  "boundary_states": [
    {
      "boundary_state_id": "boundary-state-void-001",
      "boundary_ref": "boundary-002",
      "state": "VOID",
      "provisional": true
    }
  ],
  "void_refs": [
    "void-evidence-001"
  ],
  "operator_response": {
    "response_type": "DEFER"
  }
}
```

The following must not be assumed:

```text
state = VOID
→ response = DEFER_VOID
```

The response is selected only after full runtime evidence is considered.

---

## 9. Stability Mapping

A StabilityResult remains separate from Boundary information.

Candidate representation:

```json
{
  "stability": {
    "status": "adaptive",
    "value": 0.71,
    "readability": "established",
    "continuable": true,
    "source_slice_ref": "slice-001",
    "considered_boundary_refs": [
      "boundary-001"
    ],
    "considered_boundary_state_refs": [
      "boundary-state-001"
    ],
    "evidence_refs": []
  }
}
```

Important:

```text
considered Boundary evidence
≠ Boundary determines Stability automatically
```

The API must allow:

```text
Boundary readable + Stability not_evaluable
Boundary absent + Stability established
multiple Boundaries + one StabilityResult
```

---

## 10. Operator Response Mapping

Boundary-aware Operator Response may be represented as:

```json
{
  "operator_response": {
    "response_id": "response-001",
    "response_type": "RESLICE",
    "reason": "Additional context may refine the current Unknown relation.",
    "considered_boundary_refs": [
      "boundary-001"
    ],
    "considered_boundary_state_refs": [
      "boundary-state-001"
    ],
    "decisive_evidence_refs": [
      "evidence-001"
    ],
    "conflicting_evidence_refs": [],
    "continuity_effect": "new_slice_requested",
    "next_request_ref": "reslice-request-001"
  }
}
```

The valid response space remains aligned with Priority B:

```text
CONTINUE
ADJUST
RESLICE
JUMP
DEFER
STOP
```

Boundary State values must not be reused as response values.

Incorrect:

```json
{
  "operator_response": "UNKNOWN"
}
```

Correct:

```json
{
  "boundary_state": "UNKNOWN",
  "operator_response": "RESLICE"
}
```

when RESLICE is selected after considering the full runtime context.

---

## 11. Runtime Continuity Mapping

The API should expose the continuity effect separately from the response label.

Example:

```json
{
  "continuity": {
    "source_type": "established_runtime_result",
    "source_ref": "slice-001",
    "relation_type": "reslice_requested",
    "target_type": "retained_context",
    "target_ref": "context-001",
    "traceability_preserved": true,
    "next_ready": true
  }
}
```

For Defer:

```json
{
  "continuity": {
    "source_type": "retained_traceable_runtime_relation",
    "source_ref": "void-evidence-001",
    "relation_type": "retained_pending",
    "target_type": null,
    "target_ref": null,
    "traceability_preserved": true,
    "next_ready": false
  }
}
```

This follows the Priority B refinement:

```text
continuity source
= established runtime result
  or retained traceable runtime relation
```

---

## 12. Full `/loop/step` Response Example

```json
{
  "process_id": "process-001",
  "slice_done": {
    "slice_id": "slice-001",
    "representation": {
      "relation": "partially_readable"
    },
    "deviation": {
      "value": 0.29
    },
    "readability": {
      "status": "readable"
    },
    "boundaries": [
      {
        "boundary_id": "boundary-001",
        "distinction_type": "membership",
        "readability": "readable",
        "confidence": 0.68
      }
    ],
    "boundary_states": [
      {
        "boundary_state_id": "boundary-state-001",
        "boundary_ref": "boundary-001",
        "state": "UNKNOWN",
        "provisional": true
      }
    ],
    "context_refs": [
      "context-001"
    ],
    "void_refs": []
  },
  "stability": {
    "status": "adaptive",
    "value": 0.72,
    "continuable": true,
    "source_slice_ref": "slice-001"
  },
  "operator_response": {
    "response_type": "RESLICE",
    "reason": "Retained context may refine the current Boundary State.",
    "considered_boundary_refs": [
      "boundary-001"
    ],
    "considered_boundary_state_refs": [
      "boundary-state-001"
    ],
    "next_request_ref": "reslice-request-001"
  },
  "continuity": {
    "source_type": "established_runtime_result",
    "source_ref": "slice-001",
    "relation_type": "reslice_requested",
    "target_type": "context",
    "target_ref": "context-001",
    "traceability_preserved": true,
    "next_ready": true
  }
}
```

This example demonstrates:

```text
Boundary State = UNKNOWN
Stability = adaptive and continuable
Operator Response = RESLICE
```

These values coexist without being collapsed into one judgment.

---

## 13. Support Endpoints

The canonical runtime relation remains:

```text
POST /loop/step
```

The following support endpoints may be introduced later:

```text
GET  /boundary/{boundary_id}
GET  /boundary/{boundary_id}/history
GET  /boundary-state/{boundary_state_id}
GET  /trajectory/{trajectory_id}/boundaries
GET  /process/{process_id}/boundary-evidence
POST /reslice/execute
```

These support endpoints must not redefine the runtime ownership model.

```text
Boundary support endpoint
≠ separate Boundary controller

Re-Slice support endpoint
≠ Operator Response owner
```

`POST /reslice/execute` executes a Re-Slice request already selected by Operator Response.

---

## 14. Query and History Mapping

Boundary history should be queryable as lineage rather than only as latest state.

Example:

```json
{
  "boundary_id": "boundary-001",
  "history": [
    {
      "boundary_state": "UNKNOWN",
      "source_slice_ref": "slice-001"
    },
    {
      "boundary_state": "NORMAL",
      "source_slice_ref": "slice-002",
      "relation": "reclassified_from"
    }
  ]
}
```

The API should not silently return only:

```json
{
  "boundary_state": "NORMAL"
}
```

when prior classification history is relevant to Runtime Continuity or auditability.

---

## 15. HTTP Status Mapping

Boundary State and Operator Response must not be confused with HTTP status.

Examples:

```text
Boundary State = VOID
Operator Response = DEFER
HTTP status = 200
```

may be valid when the runtime successfully processed the step and returned a valid deferred result.

Likewise:

```text
Operator Response = STOP
HTTP status = 200
```

may be valid when STOP is the expected runtime result.

HTTP errors should be reserved for API-level failures such as:

```text
invalid schema
missing required request field
unsupported API version
unauthorized access
internal execution failure
```

They must not be used merely because a Boundary State is Unknown or Void.

---

## 16. API Versioning

Boundary-aware fields should be versioned explicitly.

Candidate mapping:

```text
/loop/step
API version header or schema version field
```

Example:

```json
{
  "schema_version": "gyroos-runtime-v4-boundary-1"
}
```

Versioning should distinguish:

```text
field addition
semantic change
enum expansion
lineage relation change
response contract change
```

A new Boundary State value must not be introduced silently if clients depend on exhaustive enum handling.

---

## 17. Data Minimization and Resolution Decay

The API does not need to expose all stored Boundary evidence in every response.

A response may expose:

```text
full object
summary
reference
lineage pointer
```

depending on:

```text
API scope
runtime cost
privacy policy
memory tier
client capability
```

However, minimization must not collapse conceptual distinctions.

The following references should remain distinguishable:

```text
boundary_ref
boundary_state_ref
void_ref
stability_ref
operator_response_ref
trajectory_ref
```

---

## 18. GyroAuth Boundary

GyroOS API must not embed GyroAuth-specific decisions into Boundary-aware runtime fields.

Incorrect:

```json
{
  "boundary_state": "AUTH_FAIL"
}
```

Correct layering:

```text
GyroOS
→ Boundary / Boundary State / Stability / Operator Response evidence

GyroAuth
→ authentication-specific interpretation and selection
```

GyroAuth may consume GyroOS results, but GyroOS must not redefine Boundary State as authentication state.

---

## 19. Design Constraints

Boundary-aware API Mapping MUST NOT:

```text
add Boundary to the Core
add Boundary as a mandatory Runtime Stage
collapse Boundary into Difference / Deviation
collapse Boundary State into Stability
collapse Boundary State into Operator Response
automatically map Void to DEFER, JUMP, or STOP
return only the latest Boundary State when lineage is required
use HTTP errors as Boundary State results
make support endpoints the owner of Operator Response
mix GyroAuth application judgments into GyroOS
```

Boundary-aware API Mapping MUST:

```text
preserve SliceDone, StabilityResult, and OperatorResponse separation
represent Boundary as Slice-derived evidence
represent Boundary State as provisional relation
preserve Boundary and Boundary State references
support multiple Boundaries per SliceDone
preserve lineage and traceability
represent Runtime Continuity effects explicitly
keep /loop/step as the canonical runtime endpoint
support bounded and versioned API evolution
```

---

## 20. Key Insight

Boundary-aware API design is not the addition of a Boundary decision field.

It is the preservation of responsibility boundaries across the runtime contract.

```text
Slice makes a distinction readable.
SliceDone preserves its evidence.
Stability reads continuable establishment.
Operator Response selects the next relation.
The API exposes these without collapsing them.
```

Japanese:

```text
Boundary-aware APIとは、Boundary判定値を追加することではない。
Slice・SliceDone・Stability・Operator Responseの責務境界を、
API contract上でも崩さずに表現することである。
```

---

## 21. Summary

The canonical Boundary-aware GyroOS runtime API remains:

```text
POST /loop/step
```

The response should preserve:

```text
Boundary-aware SliceDone
StabilityResult
OperatorResponse
Runtime Continuity result
```

as distinct runtime objects.

Boundary and Boundary State are Slice-derived evidence.

They may influence Stability and Operator Response, but they do not determine either automatically.

The invariant Core remains unchanged:

```text
Structure → Slice → Stability
```

---

## 22. Next

```text
Priority C-9: Boundary-aware PoC Impact
```

---

## Priority C-10 Refinement

The API naming rule is:

```text
*_evidence
= directly embedded evidence objects

*_records
= identified classification records with lineage

*_refs
= identifiers of separately stored objects
```

A response may therefore expose either embedded values:

```json
{
  "boundary_evidence": [],
  "boundary_state_records": [],
  "void_evidence": []
}
```

or external references:

```json
{
  "boundary_refs": [],
  "boundary_state_refs": [],
  "void_refs": []
}
```

or both when explicitly documented.

The following API values must remain separate:

```text
boundary_readability
boundary_state_confidence
stability
response_confidence
```

An unreadable Boundary distinction should be represented as unclassified or unreadable Boundary evidence. It must not be converted automatically into:

```text
boundary_state = VOID
operator_response = DEFER
HTTP error
```

`VOID` is valid only when the relevant Boundary is identifiable and the target relation is insufficiently readable or connectable relative to it.
