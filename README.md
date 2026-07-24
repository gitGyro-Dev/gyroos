# GyroOS

**Execution Architecture for Gyro Process, Operator Response, Context-aware Runtime, and Dynamic Equivalence**

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

Detailed contracts are recorded in `docs/66_*` through `docs/74_*`.

---

## ❌ What GyroOS Does Not Do

GyroOS does not:

```text
redefine Structure → Slice → Stability
treat Stability as a controller
erase Δ
collapse slice-ing and slice-done
make Update Engine the loop owner
treat Context as Representation
treat Void as an actor
automatically trigger Re-Slice from Context or Stability
reduce Dynamic Equivalence to similarity
mix GyroAuth authentication logic into GyroOS
```

---

## ⭕ What GyroOS Does

GyroOS:

```text
implements Gyro Process
preserves Δ
stores Context and Void as runtime fields
measures Stability
implements Operator Response
manages Gyro Loop and Context Loop repetition
supports Re-Slice / Defer / Jump handling
supports Dynamic Equivalence runtime checks
prepares the next Orientation
```

---

## 📦 Repository Structure

```text
gyroos/
  docs/
    11_loop_controller.md
    12_update_engine.md
    13_slice_policy.md
    14_api_design.md
    15_context_runtime.md
    16_reslice_engine.md
    17_context_loop_controller.md
    18_void_defer_jump.md
    19_dynamic_equivalence_runtime.md
    66_priority_g1_sqlite_persistence.md
    67_priority_g2_repository_schema.md
    68_priority_g3_type_safe_reconstruction.md
    69_priority_g4_atomic_publication.md
    70_priority_g5_current_scope_query_endpoint.md
    71_priority_g6_process_history_query_endpoint.md
    72_priority_g7_trajectory_query_endpoint.md
    73_priority_g8_memory_record_retrieval_and_type_safe_reconstruction.md
    74_priority_g9_restart_and_recovery_tests.md
  app/
    main.py
    models.py
    repositories.py
    repository_errors.py
    runtime.py
    sqlite_repository.py
  tests/
    test_bounded_api.py
    test_priority_f_poc.py
    test_sqlite_repository.py
    test_restart_recovery.py
```

---

## 🧭 Roadmap

GyroOS evolves by progressively implementing Gyro Logic as a runtime system.

### Phase 4 — Gyro Process / Operator Response Execution

```text
Gyro Processₙ
→ Operator Responseₙ
→ Gyro Processₙ₊₁
```

### Priority G — Persistent Runtime Boundary

```text
G-1 through G-9
= implemented and verified

G-10
= cross-document review and refinement
```

---

## 📄 License

See the repository license file for applicable terms.
