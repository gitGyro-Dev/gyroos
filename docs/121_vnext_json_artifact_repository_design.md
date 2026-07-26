# 121. vNext JSON Artifact Repository Design

---

## 1. Purpose

This document defines integration gate B4:

```text
ExperimentalRecordEnvelope
↓
JSON artifact serialization
↓
file-system persistence
↓
JSON artifact loading
```

The goal is durable experimental persistence without modifying the current canonical SQLite schema.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

JSON artifact persistence is an implementation concern. It is not a new Core stage, authority mechanism, Runtime history, or Trajectory history.

---

## 2. Design Decision

Initial B4 selects:

```text
one JSON file per ExperimentalRecordEnvelope
```

with a repository-private root directory.

Rejected for the first implementation:

```text
single monolithic JSON file
JSON Lines append log
canonical SQLite integration
experimental SQLite tables
external object storage
GitHub-backed persistence
```

Reason:

```text
one-record-per-file
= minimal blast radius
+ simple replacement semantics
+ isolated corruption boundary
+ direct record_id lookup
```

---

## 3. Proposed Components

```text
JsonArtifactRepositorySettings
JsonArtifactPathPolicy
JsonArtifactExperimentalRecordRepository
```

### 3.1 JsonArtifactRepositorySettings

Proposed fields:

```text
root_directory
file_suffix = ".json"
create_root = true
encoding = "utf-8"
indent = 2
```

The first implementation should not expose retention, compression, encryption, remote synchronization, or schema migration settings.

### 3.2 JsonArtifactPathPolicy

Responsibilities:

```text
validate record_id for file-system safety
map record_id to one repository-owned file path
reject path traversal
reject absolute paths
reject directory separators
```

The path policy must not derive directories from `process_id`, `record_type`, or payload content in the first implementation.

### 3.3 JsonArtifactExperimentalRecordRepository

The implementation should satisfy the existing contract:

```text
ExperimentalRecordRepository
```

Operations:

```text
save(envelope)
get(record_id)
list(process_id=None, record_type=None)
delete(record_id)
```

---

## 4. Artifact Format

Each file stores one complete `ExperimentalRecordEnvelope` serialized as JSON.

Recommended shape:

```json
{
  "record_id": "record-001",
  "process_id": "process-001",
  "record_type": "TrajectoryGraph",
  "payload": {},
  "source_ref": null,
  "provisional": true,
  "stored_at": "2026-07-26T00:00:00Z",
  "metadata": {}
}
```

The serialized shape is the envelope representation only.

It does not add:

```text
canonical_version
schema_authority
current_marker
latest_marker
supersedes_ref
trajectory_position
runtime_sequence
```

---

## 5. Save Semantics

Saving should use atomic replacement within the repository directory:

```text
serialize envelope
↓
write temporary file in same directory
↓
flush file content
↓
replace target path atomically where supported
```

The first implementation should use same-directory temporary files so that replacement does not cross file systems.

Saving the same `record_id` replaces the prior artifact.

As with the in-memory repository:

```text
file replacement
≠ canonical supersession
≠ version progression
≠ current-record selection
```

---

## 6. Read Semantics

`get(record_id)` should:

```text
resolve repository-owned path
read UTF-8 JSON
validate as ExperimentalRecordEnvelope
return an independent model instance
```

It should not:

```text
reconstruct payload into StabilityScene or another typed model
resolve source_ref
validate record_type against a registry
select a newer replacement
repair malformed artifacts
```

Malformed JSON or envelope validation failure should surface as an explicit repository error rather than being silently ignored.

---

## 7. List Semantics

`list` should:

```text
scan repository-owned files with the configured suffix
load valid ExperimentalRecordEnvelope artifacts
apply exact-match process_id filter when supplied
apply exact-match record_type filter when supplied
return independent model instances
```

The contract must not promise semantic ordering.

```text
file-system enumeration order
≠ time order
≠ stored_at order
≠ establishment order
≠ Trajectory order
≠ canonical history
```

For deterministic tests, the implementation may sort by file name internally, but such sorting remains a storage presentation detail only.

---

## 8. Delete Semantics

`delete(record_id)` should:

```text
resolve repository-owned path
remove the file when present
return true when removed
return false when absent
```

Delete does not create:

```text
tombstone semantics
logical deletion history
Trajectory break
Identity break
continuity break
```

---

## 9. Error Model

Proposed repository-specific errors:

```text
ExperimentalRepositoryError
InvalidArtifactRecordIdError
ArtifactSerializationError
ArtifactDeserializationError
ArtifactValidationError
ArtifactStorageError
```

The implementation should not suppress malformed or inaccessible artifacts.

The initial contract does not require per-record error recovery during `list`. The safest first behavior is fail-fast with the offending path identified in the exception.

---

## 10. File-system Safety

The first implementation must enforce:

```text
repository root containment
no path traversal
no absolute record ID path
no slash or backslash in record_id
same-directory atomic replacement
UTF-8 encoding
private temporary file naming
cleanup of temporary file after failed save when possible
```

The repository must not follow caller-controlled paths embedded in payload or metadata.

Symlink handling should remain conservative. The first implementation should reject a repository root that is not a directory and should avoid resolving artifact paths outside the configured root.

---

## 11. Concurrency Boundary

Initial B4 target:

```text
thread-safe within one Python process
best-effort atomic file replacement
```

Not approved initially:

```text
multi-process locking
network file-system coordination
distributed consistency
transaction groups
compare-and-swap
```

A process-local lock may protect save/get/list/delete coordination, but it does not provide cross-process safety.

---

## 12. Typed Reconstruction Boundary

JSON artifact loading returns:

```text
ExperimentalRecordEnvelope
```

It does not return:

```text
StabilityScene
ReadabilityContext
ContinuityRelationRecord
TrajectoryGraph
RuntimeSnapshot
```

Therefore:

```text
artifact loading
≠ typed vNext reconstruction
```

Typed reconstruction remains a separate, unapproved future gate.

---

## 13. Runtime and Projection Boundary

The JSON repository does not automatically receive output from:

```text
POST /loop/step
ReadOnlyRuntimeProjectionService
SemanticAssemblyService
IncorporatedReadabilityAssemblyService
ContinuityReadabilityAssemblyService
TrajectoryAssemblyService
```

A caller must explicitly create an `ExperimentalRecordEnvelope` and invoke `save`.

Therefore:

```text
assembly result
↛ automatic persistence

Runtime result
↛ automatic persistence
```

---

## 14. Public API and GyroAuth Boundary

B4 does not expose:

```text
HTTP routes
public artifact download
public record listing
GyroAuth repository access
GyroAuth interpretation
```

Public experimental API remains integration gate C.

GyroAuth consumption remains integration gate D.

---

## 15. Test Plan

The first implementation should test:

```text
save/get round trip
UTF-8 JSON serialization
datetime serialization and validation
nested payload preservation
same-ID atomic replacement
process_id filter
record_type filter
combined filters
delete success/failure
root directory creation
invalid record_id rejection
path traversal rejection
malformed JSON failure
invalid envelope failure
temporary-file cleanup where observable
independent returned instances
no typed reconstruction
no canonical/current/version semantics
```

Tests must use temporary directories and must not write to the repository working tree.

---

## 16. Review Gates

Recommended implementation sequence:

```text
B4.1 repository-specific errors and settings
↓
Review
↓
B4.2 path policy
↓
Review
↓
B4.3 JSON repository implementation
↓
Actions verification
↓
B4 Review
```

Each review must confirm that no current SQLite, Runtime, public API, or GyroAuth behavior changed.

---

## 17. Layer Consistency Check

```text
Gyro Logic definitions changed
= NO

JSON persistence added to Core
= NO

Current SQLite schema changed
= NO

Typed reconstruction approved
= NO

Automatic Runtime persistence approved
= NO

Public API approved
= NO

GyroAuth consumption approved
= NO
```

---

## 18. Current Decision

```text
B1-B3 Experimental Repository Review
= COMPLETE

B4 JSON artifact repository design
= COMPLETE

Selected artifact shape
= ONE JSON FILE PER EXPERIMENTAL RECORD ENVELOPE

Atomic same-file replacement
= REQUIRED WHERE SUPPORTED

Path traversal protection
= REQUIRED

Typed reconstruction
= NOT APPROVED

Current SQLite integration
= NOT APPROVED

Public API exposure
= NOT APPROVED

GyroAuth consumption
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```

---

## 19. Next

Proceed in bounded steps:

```text
B4.1 repository-specific errors and settings
B4.2 path policy
B4.3 JsonArtifactExperimentalRecordRepository
```

Do not implement B4 as one unreviewed change set.
