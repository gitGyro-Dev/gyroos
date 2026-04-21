# 06. Jump and Void

---

## 1. Overview

Jump and Void define when the system must change how it observes the world.

They are not errors.
They are structural signals.

---

## 2. Void Definition

```text id="void-def"
Void = region where deviation cannot be evaluated
```

---

## 3. Void Properties

* Not noise
* Not absence
* Not failure

Void represents:

* unknown structure
* unresolved representation
* observation limit

---

## 4. Void Role

* Trigger re-observation
* Indicate model insufficiency
* Expand exploration

---

## 5. Void Handling

```text id="void-handling"
Void →
  keep
  ignore
  expand
```

---

## 6. Jump Definition

```text id="jump-def"
Jump = change of Slice configuration
```

---

## 7. Jump Trigger

Jump occurs when:

```text id="jump-trigger"
Stability < θ
OR
Void > threshold
OR
Δ unresolved
```

---

## 8. Jump Role

* Change observation space
* Replace model assumptions
* Enable new interpretations

---

## 9. Jump Process

```text id="jump-process"
current Slice → invalid
↓
Void / Δ accumulation
↓
new Slice generation
↓
re-observation
```

---

## 10. API Design

```text id="jump-api"
POST /jump/check
POST /jump/execute
GET  /void/state
```

---

## 11. Pseudocode

```python id="jump-pseudo"
def should_jump(stability, void_state, delta):

    if stability < threshold:
        return True

    if void_state.level > void_threshold:
        return True

    if delta.unresolved():
        return True

    return False
```

---

## 12. Key Insight

Jump changes the world by changing how it is observed.

---

## 13. One-line Definition

Jump and Void govern when the system must change its way of seeing.

---
