# GyroOS v4.0 Release Scope

## 1. Release Identity

```text
Release line: GyroOS v4.0
Primary release type: bounded Runtime and experimental inspection architecture
Implementation boundary: GyroOS
Application consumer boundary: GyroAuth / external consumers
```

## 2. Included Scope

GyroOS v4.0 includes the following completed and verified work.

### 2.1 Gyro Logic Core Mapping

```text
Structure → Slice → Stability
```

The invariant Gyro Logic Core remains unchanged.

GyroOS implements the Runtime reading through bounded Process execution, Operator Response, and continued Process selection.

### 2.2 Bounded Runtime

Included Runtime capabilities:

```text
POST /loop/step
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /trajectory/{trajectory_ref}
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

Included Runtime properties:

```text
bounded request execution
ProcessExecutor boundary
canonical Runtime records
immutable Process and Trajectory history
current-scope tracking
SQLite-backed atomic publication
restart reconstruction
OperatorResponse selection
```

### 2.3 Production Hardening

Included controls:

```text
environment profiles
production configuration fail-fast
Bearer authentication
request, rate, and concurrency limits
SQLite WAL and bounded lock waiting
repository-busy classification
structured logging and request correlation
schema compatibility checks
backup and restore verification
security response headers
bounded load tests
```

### 2.4 vNext Read-Only Projection

Included experimental projection capabilities remain:

```text
read-only
non-canonical
explicit-source based
Runtime-state preserving
```

Projection outputs do not select OperatorResponse, mutate Runtime state, rewrite canonical history, or create authentication or risk state.

### 2.5 Inspection API and F–W Hierarchy

Included experimental Inspection characteristics:

```text
POST-only
request-local
read-only
non-canonical
explicit references only
no implicit retrieval
```

Included hierarchy:

```text
F Receipt
→ G Batch Manifest
→ H Manifest Comparison
→ I Comparison Review Bundle
→ J Review-Bundle Comparison
→ K Review-Bundle Comparison Set
→ L Set Comparison
→ M Comparison Series
→ N Series Comparison
→ O Comparison Collection
→ P Collection Comparison
→ Q Comparison Sequence
→ R Sequence Comparison
→ S Comparison Register
→ T Register Comparison
→ U Comparison Ledger
→ V Ledger Comparison
→ W Comparison Archive
```

### 2.6 Consolidation and Verification

Included consolidation work:

```text
documentation index
checked-in workflow test groups
dedicated Inspection router
shared pure error response helper
small pure validation utility
route-boundary verification
Y Overall Review
Y Completion Review
```

### 2.7 Publication-Ready Architecture Figures

Primary figures:

```text
figures/gyroos_system_architecture_flow_en.svg
figures/gyroos_system_architecture_flow_jp.svg
```

These figures are approved as the primary architecture overview for README, GitHub Release, and future jxiv manuscripts.

## 3. Explicitly Excluded Scope

GyroOS v4.0 does not claim:

```text
distributed Runtime execution
multi-node consensus
multi-tenant authorization
public Internet deployment readiness
cloud-native orchestration
repository-backed Inspection persistence
Inspection GET, PUT, PATCH, or DELETE APIs
implicit Inspection retrieval
semantic trend inference
risk aggregation
authentication aggregation
GyroAuth decision logic inside GyroOS
formal proof of all Gyro Logic properties
complete mathematical formalization
production SLA or capacity guarantee
```

## 4. Experimental Boundaries

The following remain explicitly experimental:

```text
vNext projection contracts
Inspection API contracts
F–W hierarchy
consumer compatibility boundary
```

Experimental does not mean undefined. These contracts are documented and tested, but are not declared permanently stable for all future releases.

## 5. Layer and Dependency Rules

The release preserves:

```text
Gyro Logic → GyroOS → GyroAuth
```

Interpretation:

```text
Gyro Logic does not depend on GyroOS.
GyroOS implements Gyro Logic.
GyroAuth consumes and applies GyroOS outputs.
GyroOS does not import or depend on GyroAuth semantics.
```

## 6. Release Positioning

Recommended release title:

```text
GyroOS v4.0.0 — Bounded Runtime and Experimental Inspection Architecture
```

Recommended release summary:

> GyroOS v4.0.0 establishes a bounded, persistent Runtime implementation of Gyro Logic, adds production-hardening controls, and completes a read-only, non-canonical vNext Inspection architecture with explicit F–W contracts and a preserved GyroAuth consumer boundary.

## 7. jxiv Relationship

GitHub Release v4.0.0 is the implementation snapshot.

The later jxiv manuscript will explain:

```text
why the bounded Runtime boundary is required
how Structure → Slice → Stability maps into Runtime execution
why projection and Inspection remain read-only and non-canonical
why F–W references do not imply chronology or semantics
why GyroAuth remains an external consumer
how finite resources preserve Trajectory continuity without redefining the Core
```

The jxiv manuscript is not part of the v4.0 implementation scope and will be created after the GitHub Release is fixed.

## 8. Scope Decision

```text
GyroOS v4.0 release scope
= FIXED

Runtime scope
= INCLUDED

Production hardening
= INCLUDED

vNext projection
= INCLUDED AS EXPERIMENTAL

Inspection F–W hierarchy
= INCLUDED AS EXPERIMENTAL

Architecture figures
= INCLUDED

GyroAuth application logic
= EXCLUDED

jxiv manuscript
= POST-RELEASE ARTIFACT
```
