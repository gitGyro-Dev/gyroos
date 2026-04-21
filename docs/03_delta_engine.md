# 03. Δ Engine

---

## 1. Overview

Δ Engine computes deviation between representations.

Deviation is fundamental.
It is not an error.

---

## 2. Definition

```text
Δ_ij = D(X_i, X_j)
```

---

## 3. Role

* Measure inconsistency
* Track deviation over time
* Classify deviation

---

## 4. Structure of Δ

```text
Δ = (magnitude, direction, type, time)
```

---

## 5. Types of Δ

* Noise
* Systematic bias
* Model mismatch
* Structural inconsistency

---

## 6. Temporal Δ

```text
Δ_t = D(X_t, X_{t-1})
```

---

## 7. API Design

```text
POST /delta/compute
GET  /delta/history
GET  /delta/classification
```

---

## 8. Pseudocode

```python
def compute_delta(slice_results):
    delta_map = {}
    for i in slice_results:
        for j in slice_results:
            if i < j:
                delta_map[(i,j)] = distance(slice_results[i], slice_results[j])
    return delta_map
```

---

## 9. Key Insight

Δ is not noise.
Δ is information.

---

## 10. One-line Definition

Δ Engine makes inconsistency explicit and usable.

---
