# GyroOS

**Execution Architecture for Gyro Process, Operator Response, Context-aware Runtime, and Dynamic Equivalence**

---

## 📄 Publication

GyroOS v4.0 is now published on Jxiv.

- English preprint: https://doi.org/10.51094/jxiv.5842
- Zenodo archive: https://doi.org/10.5281/zenodo.21641266
- GitHub Release: v4.0.0

The Japanese translation will be prepared and submitted after reconciling it against the public English version.

---

## 🧭 What is GyroOS?

GyroOS is the execution layer of **Gyro Logic**.

It does not redefine Gyro Logic.  
It implements Gyro Logic as a runtime system.

The invariant theoretical core is:

```text
Structure → Slice → Stability
```

GyroOS maps this core into runtime continuity. The internal runtime reading of Slice is:

```text
Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
→ Next Process
```

Operator Orientation, slice-ing, and slice-done are internal distinctions of Slice. They are not additional core stages.

GyroOS is not an application layer.  
GyroAuth is the application layer built on top of GyroOS.

---

## 🧩 Position in the Stack

```text
Gyro Logic   = Theory Layer
GyroOS       = Execution Layer
GyroAuth     = Application Layer
```

Rules:

```text
Gyro Logic does not depend on GyroOS.
GyroOS implements Gyro Logic.
GyroAuth applies GyroOS.
```

GyroOS must not modify Gyro Logic definitions for implementation convenience.

### System Architecture and Flow

![GyroOS System Architecture and Flow](figures/gyroos_system_architecture_flow_en.svg)

The figure shows the complete bounded flow from the invariant Gyro Logic core through GyroOS Runtime, vNext read-only projection, the POST-only Inspection API, the explicit-reference F-W hierarchy, and the external GyroAuth consumer boundary.

Publication-ready sources:

- English SVG: `figures/gyroos_system_architecture_flow_en.svg`
- Japanese SVG: `figures/gyroos_system_architecture_flow_jp.svg`
- Architecture notes and proposed captions: `docs/292_gyroos_system_architecture_flow_overview.md`

---

## 🔁 Core Principle

The core principle remains:

```text
Structure → Slice → Stability
```

This is the timeless Gyro Unit.

GyroOS implements its runtime reading as a Gyro Process:

```text
Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
```

A Gyro Loop is not a replacement for Structure → Slice → Stability.

A Gyro Loop is the repetition of Gyro Process through Operator Response.

---

## 🧠 Gyro Unit / Process / Loop

### Gyro Unit

```text
Gyro Unit = Structure → Slice → Stability
```

The Gyro Unit is timeless.

Operator Orientation, slice-ing, and slice-done may be read as internal distinctions of Slice. Operator Response, Context Loop, and Dynamic Equivalence remain outside the invariant core sequence.

---

### Gyro Process

```text
Gyro Process
= Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
```

The Gyro Process is one temporal runtime section within continuing trajectory.

Time appears mainly in:

```text
slice-ing
Operator Response
```

---

### Gyro Loop

```text
Gyro Loop = repetition of Gyro Process
```

More precisely:

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

The Loop is controlled by Operator Response, not by Stability directly.

---

## 🧠 Key Concepts

### Structure

Structure is the runtime mode in which an establishment remains possible.

It may appear as a state, relation, field, process condition, or runtime configuration, but it is not limited to an input value or fixed container.

A current Runtime Structure may retain prior transformation while remaining open to the next Slice.

---

### Operator Orientation

Operator Orientation is the directional condition at the entrance and within Slice.

It may express what is being sought, which Difference matters, which direction should be opened, and which granularity or Context is relevant.

It is not an independent core stage and is not Slice itself.

```text
Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
```

---

### Slice

Slice is the runtime process by which a path is opened through Structure toward an establishment.

It may be implemented through computation, transformation, observation, search, selection, or interpretation, but it is not reducible to any one of them.

In GyroOS, the internal runtime reading of Slice is:

```text
Operator Orientation
→ slice-ing
→ slice-done
```

---

### slice-ing

slice-ing is the time-including runtime process through which the path is being opened.

```text
slice-ing = Slice in progress
```

This is where computation, transformation, observation, search, or recognition may occur.

---

### slice-done

slice-done is the state in which Slice has become readable as an established result.

GyroOS may represent this established Slice result as:

```text
slice-done = X + Δ
```

where:

```text
X = representation produced by Slice
Δ = deviation between Structure and Representation
```

GyroOS may store additional runtime fields alongside slice-done:

```text
Boundary
Boundary State
Context
Void
Metadata
```

These are readable or derived relations of the Slice result. They do not change the invariant core.

---

### Δ / Deviation

Deviation is not an error to be eliminated.

```text
Δ = deviation between Structure and Representation
```

GyroOS preserves and evaluates Δ.

---

### Context

Context is inferred surrounding Structure that was not explicitly represented by Slice.

```text
Context = inferred surrounding structure
```

Context is:

```text
operator-relative
slice-dependent
provisional
inferred
```

Context is not Representation.
Context is not Void.

---

### Re-Slice

Re-Slice is a secondary Slice over an existing runtime result, especially Context.

```text
Re-Slice = Slice over Context or prior SliceDone
```

Important:

```text
Re-Slice is selected by Operator Response.
Stability does not directly start Re-Slice.
```

---

### Stability

Stability is the state in which the path opened through Slice becomes readable as an establishment that can continue.

It is not a controller, success flag, termination state, or stop condition.

```text
Stability = continuing established state of the opened path
```

Stability is observed, measured, stored, and passed to Operator Response.

---

### Operator Response

Operator Response is the post-Stability reaction of the Operator.

In GyroOS v4.0+, this is implemented primarily by the Loop Controller.

It may decide:

```text
Continue
Adjust
Stop
Re-Slice Context
Defer Void
Jump
Void handling
```

---

### Void

Void is a region or state that cannot be connected, inferred, or evaluated by the current Slice.

Void does not act by itself.

Operator Response decides how to handle Void.

---

### Jump

Jump is a non-continuous reconstruction of Orientation, Slice, or Structure mapping.

Jump is selected by Operator Response.

---

### Dynamic Equivalence

Dynamic Equivalence is trajectory-based equivalence.

Two states may be statically different but dynamically equivalent if they remain connected through a stability-preserving trajectory.

```text
A ≠ B
but
A ≈_T B
```

Dynamic Equivalence is not simple similarity.

It requires:

```text
Trajectory
Stability preservation
allowed Δ
Context consistency
```

---

## 🏗️ Architecture

For the repository-level architecture overview, see the publication-ready figure above and `docs/292_gyroos_system_architecture_flow_overview.md`.

```text
Runtime Structure
   ↓
Slice Engine {
   Operator Orientation / Slice Policy
      ↓
   slice-ing
      ↓
   SliceDone {
     representation: X,
     deviation: Δ,
     boundary: B,
     boundary_state: BS,
     context: C,
     void: V,
     metadata: M
   }
}
   ↓
Deviation Engine
   ↓
Stability Engine
   ↓
StabilityResult
   ↓
Loop Controller
   ↓
Operator Response
   ├─ Continue
   ├─ Adjust → Update Engine
   ├─ Re-Slice Context → Re-Slice Engine
   ├─ Defer Void
   ├─ Jump → Update Engine
   └─ Stop
   ↓
Next Orientation / Next Process
```

---

## 🔧 Core Runtime Components

### Slice Engine

Applies the runtime representation of Operator Orientation, executes slice-ing, and produces a readable slice-done result.

---

### Context Runtime

Stores inferred surrounding structure alongside SliceDone.

Context may become a future Re-Slice target.

---

### Re-Slice Engine

Executes secondary Slice over Context or prior SliceDone when requested by Operator Response.

---

### Deviation Engine

Extracts and preserves Δ.

---

### Stability Engine

Reads whether the path established in slice-done can continue as an establishment.

It does not control the Loop.

---

### Loop Controller

Implements Operator Response.

It owns the response decision after Stability is available.

Correct relation:

```text
Stability
→ Loop Controller / Operator Response
→ Next Process
```

---

### Update Engine

Applies updates only when requested by Operator Response.

It is not the center of GyroOS.

Correct relation:

```text
Loop Controller / Operator Response
→ Update Engine if needed
→ Next Orientation
```

---

### Dynamic Equivalence Runtime

Evaluates whether two states are equivalent across trajectory without reducing them to static equality.

Output:

```text
equivalent | not_equivalent | undecidable
```

---

## 🔁 GyroOS Runtime Flow

At each process cycle:

```text
1. Read the current Runtime Structure
2. Enter Slice under Operator Orientation / Slice Policy
3. Execute slice-ing
4. Produce a readable SliceDone = X + Δ plus Boundary / Boundary State / Context / Void
5. Read Stability as a continuing establishment
6. Execute Operator Response through Loop Controller
7. Re-Slice Context, Defer Void, Jump, Stop, or Continue as selected
8. Prepare Next Orientation or Next Process
```

---

## 🌐 Priority G Bounded Runtime API

Priority G adds a bounded, persistent Runtime API without changing the invariant Core.

```text
POST /loop/step
GET  /loop/state/{loop_id}
GET  /loop/history/{loop_id}
GET  /trajectory/{trajectory_ref}
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

Runtime persistence is implemented through an atomic SQLite-backed repository boundary:

```text
complete Process result group
→ atomic publication
→ current-scope pointer update
→ immutable Process and Trajectory history
→ typed canonical reconstruction after restart
```

Query surfaces do not execute a new Process, select Operator Response, infer a hidden latest state, or convert repository absence into VOID, DEFER, STOP, or Stability results.

Detailed contracts are recorded in `docs/66_*` through `docs/75_*`.

---

## 🛡️ Priority H Production Hardening

Priority H hardens the Priority G Runtime boundary without changing canonical Gyro Process semantics.

Implemented controls:

```text
development / test / production settings profiles
production configuration fail-fast
Bearer authentication for Runtime endpoints
request-body, rate, and concurrent-request limits
SQLite WAL and bounded lock waiting
retryable repository-busy classification
JSON structured logging and X-Request-ID correlation
database schema compatibility validation
verified SQLite backup and restore
production token quality checks
security response headers
bounded concurrent and sustained load tests
```

The current candidate remains a bounded, single-host, SQLite-backed Runtime with one configured Bearer token.

Public production exposure still requires deployment declarations for TLS, network policy, secret injection, backup storage, logging destination, capacity, rollback, and operator ownership.

Detailed contracts are recorded in `docs/76_*` through `docs/85_*`.

---

## 🧪 vNext Experimental Projection and Inspection

The `/vnext/experimental` surface provides read-only, request-local, non-canonical projection and Inspection contracts.

The Inspection contract family extends from F Receipt through W Comparison Archive using explicit references only. It does not mutate Runtime state, create canonical persistence, infer semantic trends, aggregate risk, or create authentication decisions.

Primary navigation:

- Inspection documentation index: `docs/283_vnext_inspection_documentation_index.md`
- Consolidation completion: `docs/291_vnext_inspection_consolidation_implementation_completion_review.md`
- System architecture figure: `figures/gyroos_system_architecture_flow_en.svg`

---

## 📄 Release and Publication Figure

The system architecture SVG is the primary overview figure for the GyroOS v4.0 release, README presentation, and related publications.

Use the SVG as the master source and derive PDF or PNG only when a publication or platform requires another format.

- English master: `figures/gyroos_system_architecture_flow_en.svg`
- Japanese master: `figures/gyroos_system_architecture_flow_jp.svg`
- Figure usage notes: `docs/292_gyroos_system_architecture_flow_overview.md`
