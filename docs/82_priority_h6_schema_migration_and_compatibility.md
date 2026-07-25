# 82. Priority H-6 — Schema Migration and Compatibility

---

## 1. Purpose

H-6 introduces an explicit database-schema compatibility boundary for the SQLite-backed GyroOS Runtime repository.

The purpose is to prevent an incompatible or partially formed database from being accepted silently at startup.

The invariant Core remains unchanged:

```text
Structure
↓
Slice
↓
Stability
```

Database schema compatibility is a persistence and deployment concern. It does not evaluate Stability, select OperatorResponse, or alter canonical Process meaning.

---

## 2. Schema Version Contract

The current database schema version remains:

```text
SCHEMA_VERSION = 1
```

H-6 adds a persistent metadata table:

```text
schema_metadata
```

The authoritative row is:

```text
metadata_key   = database_schema_version
metadata_value = 1
```

The database-level version is separate from each canonical record's `schema_version` field.

```text
database schema version
→ validates the repository layout

record schema version
→ validates the serialized canonical record shape
```

---

## 3. New Database Initialization

For a new empty database, `SQLiteStore` creates:

```text
runtime_records
current_scope
idempotency_entries
schema_metadata
```

It then registers:

```text
database_schema_version = 1
```

Schema metadata is created in the same initialization transaction as the repository tables.

---

## 4. Legacy Database Adoption

Databases created before H-6 do not contain `schema_metadata`.

H-6 treats such a database as a legacy candidate only when one or more known Runtime tables already exist.

Before adopting the database as schema version 1, GyroOS validates the required tables:

```text
runtime_records
current_scope
idempotency_entries
```

It also validates the required columns used by the current repository implementation.

Only after this structural check passes is the metadata row inserted:

```text
database_schema_version = 1
```

This is a compatibility adoption step, not a structural rewrite of canonical data.

---

## 5. Incompatible Database Rejection

Startup fails with `RepositorySchemaMismatch` when:

```text
stored database schema version is unknown
legacy database is missing required tables
legacy table is missing required columns
database schema metadata is missing after initialization
```

Example unknown-version failure:

```text
unsupported database schema version 999; runtime supports 1
```

GyroOS does not continue with partial repository access after this failure.

---

## 6. Migration Policy

H-6 does not introduce arbitrary automatic migrations.

Current policy:

```text
new empty database
→ create schema version 1

validated pre-H-6 database with version-1 layout
→ register schema version 1

known future migration path
→ not yet implemented

unknown or incomplete database
→ fail startup
```

A future schema change must provide an explicit ordered migration before `SCHEMA_VERSION` is incremented.

Destructive migration must never be inferred solely from table names or metadata timestamps.

---

## 7. Public Repository Diagnostic

`SQLiteStore` adds:

```text
get_database_schema_version()
```

This returns the persistent database schema version and raises `RepositorySchemaMismatch` when the metadata row is absent.

The value is not currently exposed by the public health endpoint.

---

## 8. Implemented Files

Added:

```text
tests/test_schema_compatibility.py
docs/82_priority_h6_schema_migration_and_compatibility.md
```

Updated:

```text
app/sqlite_repository.py
.github/workflows/priority-f-poc.yml
```

---

## 9. Test Coverage

The H-6 tests verify:

```text
new database registers current schema version
valid legacy database is adopted as version 1
unknown future schema version is rejected
legacy database missing required tables is rejected
legacy table missing required columns is rejected
```

The existing repository tests continue to verify record-level schema mismatch handling during reconstruction.

The workflow now executes the H-6 schema compatibility test file.

Verified GitHub Actions run:

```text
run_id = 30141699950
conclusion = success
```

---

## 10. Deferred Migration Work

H-6 does not yet implement:

```text
schema version 1 → version 2 migration
migration registry
migration CLI
migration dry-run
backup-before-migration orchestration
rollback migration
online migration
multi-process migration lock
migration audit history
health endpoint schema disclosure
```

Backup and restore policy belongs to H-7.

---

## 11. Responsibility Review

```text
SQLiteStore initialization
→ creates and validates database layout

schema_metadata
→ stores authoritative database schema version

RepositorySchemaMismatch
→ represents unsupported or incomplete layout

canonical record reconstruction
→ continues to validate each record schema version separately
```

Database schema metadata does not become part of Process identity, trajectory, Stability, OperatorResponse, or canonical Runtime memory.

---

## 12. H-6 Decision

```text
H-6 Schema Migration and Compatibility
= COMPLETE

Persistent database schema metadata
= IMPLEMENTED

Legacy version-1 structural adoption
= IMPLEMENTED

Unknown-version startup rejection
= IMPLEMENTED

Destructive automatic migration
= NOT IMPLEMENTED

GitHub Actions execution verification
= COMPLETE
```

The next Priority H step is:

```text
H-7 Backup, Restore, and Recovery Operations
```
