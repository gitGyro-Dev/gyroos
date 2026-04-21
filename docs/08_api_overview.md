# 08. API Overview

---

## 1. Overview

GyroOS exposes its execution model through a set of APIs.

These APIs do not operate on static data.

They operate on:

* multi-slice representations
* deviation structures
* stability evaluation
* selection processes

---

## 2. Design Principle

Traditional APIs:

* CRUD-based
* state mutation

GyroOS APIs:

* observation-driven
* evaluation-driven
* selection-driven

---

## 3. Core API Groups

---

### 3.1 Slice

```text id="api-slice"
POST /slice/apply
GET  /slice/config
POST /slice/update
```

Function:

* Generate representations from structure

---

### 3.2 Δ (Deviation)

```text id="api-delta"
POST /delta/compute
GET  /delta/history
GET  /delta/classification
```

Function:

* Compute and track deviation

---

### 3.3 Stability

```text id="api-stability"
POST /stability/evaluate
GET  /stability/history
GET  /stability/band
```

Function:

* Evaluate tolerance under deviation

---

### 3.4 Selection

```text id="api-selection"
POST /select
GET  /select/current
GET  /select/alternatives
```

Function:

* Choose operational representation

---

### 3.5 Jump / Void

```text id="api-jump"
POST /jump/check
POST /jump/execute
GET  /void/state
```

Function:

* Handle instability and reconfiguration

---

### 3.6 Execution

```text id="api-step"
POST /step
```

Function:

* Execute one full cycle

---

## 4. Unified Execution

The main API is:

```text id="api-main"
POST /step
```

Internally performs:

```text
Slice → Δ → Stability → Selection → Jump → Action
```

---

## 5. Example Request

```json
{
  "structure": {...},
  "context": {...},
  "history": {...}
}
```

---

## 6. Example Response

```json
{
  "mode": "continue",
  "selected": {...},
  "stability": {...},
  "delta": {...},
  "void": {...},
  "action": {...}
}
```

---

## 7. Design Philosophy

GyroOS APIs do not return answers.

They return:

* evaluated states
* selected representations
* stability context

---

## 8. Key Insight

The API is not for querying data.

👉 It is for running the system.

---

## 9. One-line Definition

GyroOS API exposes the execution of slice-based, deviation-aware computation.

---
