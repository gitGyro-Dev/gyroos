# 02. Slice Engine

---

## 1. Overview

Slice Engine is responsible for reconstructing structure into multiple representations.

Slice is not a read operation.
It is a transformation.

---

## 2. Definition

```text
X_i = O_i(S)
```

* `S`: Structure
* `O_i`: Slice operator
* `X_i`: Representation

---

## 3. Role

* Generate multiple views of the same structure
* Control observation resolution
* Enable deviation computation

---

## 4. Properties

* Partial
* Context-dependent
* Frame-dependent
* Non-unique

---

## 5. Multi-Slice Model

```text
S → {O1, O2, O3} → {X1, X2, X3}
```

---

## 6. Slice Types

* Spatial Slice
* Temporal Slice
* Feature Slice
* Relational Slice
* Probabilistic Slice

---

## 7. API Design

```text
POST /slice/apply
GET  /slice/config
POST /slice/update
```

---

## 8. Pseudocode

```python
def apply_slices(structure, slice_configs):
    results = {}
    for config in slice_configs:
        results[config.id] = config.operator(structure)
    return results
```

---

## 9. Key Insight

Slice defines reality.

---

## 10. One-line Definition

Slice Engine reconstructs structure into multiple observable forms.

---
