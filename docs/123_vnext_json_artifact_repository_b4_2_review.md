# 123. vNext JSON Artifact Repository B4.2 Review

---

## 1. Scope

Reviewed:

```text
JsonArtifactPathPolicy
```

The policy maps one safe `record_id` to:

```text
one repository-contained artifact path
one same-directory temporary path
```

---

## 2. Record ID Safety

Rejected:

```text
empty IDs
.
..
absolute paths
forward-slash paths
backslash paths
NUL-containing IDs
```

The policy does not sanitize unsafe IDs into a different identity. It rejects them explicitly.

Decision:

```text
Record ID safety
= ACCEPTED
```

---

## 3. Root Containment

Artifact and temporary paths must remain under the resolved repository root.

```text
record_id
→ repository root / record_id + suffix
```

Path traversal and containment escape are rejected.

Decision:

```text
Root containment
= ACCEPTED
```

---

## 4. Temporary Path Boundary

Temporary paths are generated:

```text
in the same directory as the final artifact
with a unique UUID component
with a .tmp suffix
```

This enables later same-filesystem replacement without defining transaction, version, or canonical semantics.

Decision:

```text
Temporary path policy
= ACCEPTED
```

---

## 5. Filesystem Responsibility Boundary

B4.2 does not:

```text
create directories
create files
read files
write files
delete files
perform atomic replacement
acquire locks
```

Those operations remain B4.3 repository responsibilities.

Decision:

```text
Path / storage separation
= ACCEPTED
```

---

## 6. Semantic Non-responsibilities

The policy does not define:

```text
canonical authority
current/latest record
record version
Trajectory order
Runtime sequence
typed reconstruction
```

Decision:

```text
Semantic isolation
= ACCEPTED
```

---

## 7. Final Decision

```text
B4.2 path policy
= COMPLETE

JsonArtifactPathPolicy
= ACCEPTED AS PURE PATH POLICY

Critical design blocker
= NONE IDENTIFIED

B4.3 JSON artifact repository
= APPROVED TO PROCEED
```
