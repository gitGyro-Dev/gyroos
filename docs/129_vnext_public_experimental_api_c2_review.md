# 129. vNext Public Experimental API C2 Review

---

## 1. Scope

Reviewed:

```text
ExperimentalRepositoryProvider
experimental_repository_provider
get_experimental_repository
```

---

## 2. Contract Dependency

The provider depends on:

```text
ExperimentalRecordRepository
```

It does not expose concrete repository methods beyond the abstract contract.

Decision:

```text
Repository contract dependency
= ACCEPTED
```

---

## 3. Default Backend

The default backend is:

```text
InMemoryExperimentalRecordRepository
```

The verified JSON artifact repository is not selected by default for the initial public experimental API.

Decision:

```text
Initial backend selection
= ACCEPTED AS IN-MEMORY ONLY
```

---

## 4. Replacement Boundary

The provider permits explicit repository replacement for testing or configuration.

```text
replace_repository
≠ canonical backend promotion
≠ runtime store replacement
≠ migration
```

Decision:

```text
Explicit provider replacement boundary
= ACCEPTED
```

---

## 5. Runtime and Canonical Isolation

The provider does not depend on:

```text
app.repositories.store
ProcessExecutor
RuntimeSettings
SQLite repository
current/latest selection
canonical authority
GyroAuth
```

Decision:

```text
Runtime isolation
= ACCEPTED

Canonical authority absence
= ACCEPTED
```

---

## 6. Final Decision

```text
C2 repository dependency / provider boundary
= COMPLETE

Abstract repository dependency
= ACCEPTED

Default in-memory backend
= ACCEPTED

JSON backend public selection
= NOT APPROVED

Critical design blocker
= NONE IDENTIFIED
```

Proceed to:

```text
C3 experimental record routes
```
