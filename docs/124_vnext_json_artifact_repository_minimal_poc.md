# 124. vNext JSON Artifact Repository Minimal PoC

---

## 1. Scope

Implemented:

```text
B4.1 errors / settings
B4.2 path policy
B4.3 JSON artifact repository
```

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

---

## 2. Components

Added:

```text
app/vnext/json_artifact_repository.py
```

Components:

```text
ExperimentalRepositoryError hierarchy
JsonArtifactRepositorySettings
JsonArtifactPathPolicy
JsonArtifactExperimentalRecordRepository
```

The repository implements:

```text
ExperimentalRecordRepository
```

---

## 3. Storage Shape

```text
one ExperimentalRecordEnvelope
=
one UTF-8 JSON artifact
```

The stored JSON contains only the envelope fields.

It does not add:

```text
canonical version
current/latest marker
supersession relation
Trajectory position
Runtime sequence
typed model discriminator beyond record_type text
```

---

## 4. Save Boundary

Save performs:

```text
safe artifact path resolution
JSON serialization
same-directory temporary write
flush
optional fsync
os.replace to final artifact
temporary cleanup
```

Replacement is a storage operation only.

```text
file replacement
≠ canonical supersession
≠ version progression
≠ current-record selection
```

---

## 5. Read Boundary

Read performs:

```text
UTF-8 decode
JSON parse
ExperimentalRecordEnvelope validation
filename / record_id consistency validation
```

Read returns:

```text
ExperimentalRecordEnvelope
```

It does not reconstruct:

```text
StabilityScene
ReadabilityContext
ContinuityRelationRecord
TrajectoryGraph
RuntimeSnapshot
```

---

## 6. List Boundary

List supports filters:

```text
process_id
record_type
```

File enumeration order has no semantic meaning.

```text
list order
≠ time order
≠ stored_at order
≠ establishment order
≠ Trajectory order
≠ canonical history
```

---

## 7. Delete Boundary

Delete removes only the artifact selected by a safe record ID.

It returns:

```text
true when removed
false when absent
```

Delete does not imply semantic invalidation, rollback, Runtime deletion, or GyroAuth revocation.

---

## 8. Error Boundary

Explicit errors distinguish:

```text
unsafe record ID
serialization failure
deserialization failure
validation failure
storage failure
```

Corrupt or invalid artifacts are not silently ignored.

---

## 9. Concurrency Boundary

The implementation provides:

```text
RLock protection within one Python process
best-effort same-filesystem atomic replace
```

It does not provide:

```text
multi-process locking
transaction groups
compare-and-swap
distributed consistency
crash recovery protocol
```

---

## 10. Isolation

Unchanged:

```text
current SQLite schema
Runtime behavior
OperatorResponse behavior
public API
GyroAuth consumption
repository reconstruction registry
```

---

## 11. Tests

Added:

```text
tests/vnext/test_json_artifact_repository_settings.py
tests/vnext/test_json_artifact_path_policy.py
tests/vnext/test_json_artifact_repository.py
```

Coverage includes:

```text
settings validation and immutability
error hierarchy
record ID safety
root containment
temporary path generation
save/get round trip
deep-copy boundary
same-ID replacement
list filtering
delete behavior
corrupt JSON failure
invalid envelope failure
filename / record_id mismatch failure
absence of canonical and typed reconstruction fields
```

---

## 12. Current Decision

```text
B4.1 errors / settings
= IMPLEMENTED AND REVIEWED

B4.2 path policy
= IMPLEMENTED AND REVIEWED

B4.3 JSON artifact repository
= IMPLEMENTED

GitHub Actions verification
= PENDING

Current SQLite schema
= UNCHANGED

Typed reconstruction registry
= NOT IMPLEMENTED

Public API
= UNCHANGED

GyroAuth consumption
= UNCHANGED
```
