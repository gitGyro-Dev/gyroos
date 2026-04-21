# 05. Selection Engine

---

## 1. Overview

Selection Engine determines which representation is used operationally.

Selection is not truth.
It is a decision.

---

## 2. Definition

```text id="selection-def-v2"
X* = Select({X_i}, Stability, Context)
```

---

## 3. Role

* Choose representation under uncertainty
* Balance multiple stability scores
* Enable system action

---

## 4. Properties

* Context-dependent
* Time-dependent
* Non-absolute
* Reversible

---

## 5. Selection Strategies

### 5.1 Max Stability

```text id="max-stab"
X* = argmax(Stab(X_i))
```

---

### 5.2 Weighted Selection

```text id="weighted"
P(X_i) ∝ Stab(X_i)
```

---

### 5.3 Multi-Selection

* Keep top-k representations
* Used in uncertain environments

---

### 5.4 Contextual Selection

```text id="contextual"
Score = αStab + βTaskFit + γHistoryFit
```

---

## 6. Selection Output

```text id="selection-output"
selected = {
  representation: X*
  score: Stab*
  confidence: value
  alternatives: [X_j...]
}
```

---

## 7. API Design

```text id="selection-api"
POST /select
GET  /select/current
GET  /select/alternatives
```

---

## 8. Pseudocode

```python id="selection-pseudo"
def select(slice_results, stability_map, context):

    best = None
    best_score = -inf

    for sid, x in slice_results.items():
        score = compute_score(x, stability_map[sid], context)

        if score > best_score:
            best = x
            best_score = score

    return best
```

---

## 9. Key Insight

Selection defines action.

---

## 10. One-line Definition

Selection Engine chooses the operational representation under deviation.

---
