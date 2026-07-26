# 122. vNext JSON Artifact Repository B4.1 Review

---

## 1. Scope

Reviewed:

```text
ExperimentalRepositoryError
InvalidArtifactRecordIdError
ArtifactSerializationError
ArtifactDeserializationError
ArtifactValidationError
ArtifactStorageError
JsonArtifactRepositorySettings
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

## 2. Error Boundary

The error hierarchy is local to the experimental JSON artifact repository.

It separates:

```text
unsafe artifact identity
serialization failure
deserialization failure
envelope validation failure
filesystem/storage failure
```

It does not convert these failures into Runtime decisions, OperatorResponse values, canonical repository states, or GyroAuth outcomes.

Decision:

```text
Error separation
= ACCEPTED
```

---

## 3. Settings Boundary

Settings define only:

```text
repository root
text encoding
JSON indentation
file suffix
fsync-on-save preference
```

They do not define:

```text
canonical authority
current/latest selection
record versioning
Trajectory order
Runtime execution
OperatorResponse mapping
typed reconstruction
public API behavior
```

Decision:

```text
Settings minimality
= ACCEPTED
```

---

## 4. Immutability

`JsonArtifactRepositorySettings` is frozen.

Configuration mutation after repository construction is therefore not an implicit storage state change.

Decision:

```text
Settings immutability
= ACCEPTED
```

---

## 5. Validation Scope

Validation is limited to mechanical configuration safety:

```text
non-empty encoding
non-negative indentation
non-empty extension-like suffix
Path normalization to pathlib.Path
```

No filesystem access, directory creation, path containment, or record ID validation occurs in B4.1.

Those responsibilities remain reserved for B4.2 path policy and B4.3 repository operations.

Decision:

```text
Validation responsibility boundary
= ACCEPTED
```

---

## 6. Review Decision

```text
B4.1 errors / settings
= COMPLETE

Error hierarchy
= ACCEPTED

Settings model
= ACCEPTED

Critical design blocker
= NONE IDENTIFIED

B4.2 path policy
= APPROVED TO PROCEED
```

B4.1 does not modify:

```text
current SQLite schema
Runtime behavior
public API
GyroAuth boundary
ExperimentalRecordRepository contract
```
