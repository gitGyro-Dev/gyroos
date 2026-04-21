import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# Gyro Conflict Demo
# -----------------------------
# Idea:
# - One behavior state
# - Two competing frames
# - Each frame pulls the state in a different direction
# - Conflict bends the inference trajectory
# -----------------------------


target_a = np.array([1.8, 1.2], dtype=float)
target_b = np.array([-1.6, 1.4], dtype=float)

state = np.array([0.0, -1.4], dtype=float)
frame_a = np.array([1.0, 0.2], dtype=float)
frame_b = np.array([-1.0, 0.2], dtype=float)

state_lr = 0.08
frame_lr = 0.04
conflict_lambda = 0.35
steps = 70

state_history = []
score_a_history = []
score_b_history = []
total_score_history = []
conflict_history = []
frame_a_history = []
frame_b_history = []


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v.copy()
    return v / n


def stability(state: np.ndarray, frame: np.ndarray, target: np.ndarray) -> float:
    # Higher when state is close to target and aligned with frame
    dist_term = -np.linalg.norm(state - target)
    align_term = np.dot(normalize(state + 1e-8), normalize(frame))
    return 1.2 * dist_term + 0.8 * align_term


def conflict(frame1: np.ndarray, frame2: np.ndarray) -> float:
    return np.linalg.norm(frame1 - frame2)


def finite_grad_state(fn, state: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    grad = np.zeros_like(state)
    for i in range(len(state)):
        sp = state.copy()
        sm = state.copy()
        sp[i] += eps
        sm[i] -= eps
        grad[i] = (fn(sp) - fn(sm)) / (2 * eps)
    return grad


def finite_grad_frame(fn, frame: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    grad = np.zeros_like(frame)
    for i in range(len(frame)):
        fp = frame.copy()
        fm = frame.copy()
        fp[i] += eps
        fm[i] -= eps
        grad[i] = (fn(fp) - fn(fm)) / (2 * eps)
    return grad


for _ in range(steps):
    s_a = stability(state, frame_a, target_a)
    s_b = stability(state, frame_b, target_b)
    c = conflict(frame_a, frame_b)
    total = 0.5 * s_a + 0.5 * s_b - conflict_lambda * c

    state_history.append(state.copy())
    score_a_history.append(s_a)
    score_b_history.append(s_b)
    total_score_history.append(total)
    conflict_history.append(c)
    frame_a_history.append(frame_a.copy())
    frame_b_history.append(frame_b.copy())

    # Behavior update: optimize the joint objective
    def joint_objective_for_state(s):
        sa = stability(s, frame_a, target_a)
        sb = stability(s, frame_b, target_b)
        return 0.5 * sa + 0.5 * sb - conflict_lambda * conflict(frame_a, frame_b)

    grad_s = finite_grad_state(joint_objective_for_state, state)
    state = state + state_lr * grad_s

    # Frame A update
    def objective_for_frame_a(fa):
        sa = stability(state, fa, target_a)
        return 0.5 * sa + 0.5 * stability(state, frame_b, target_b) - conflict_lambda * conflict(fa, frame_b)

    grad_fa = finite_grad_frame(objective_for_frame_a, frame_a)
    frame_a = frame_a + frame_lr * grad_fa

    # Frame B update
    def objective_for_frame_b(fb):
        sb = stability(state, fb, target_b)
        return 0.5 * stability(state, frame_a, target_a) + 0.5 * sb - conflict_lambda * conflict(frame_a, fb)

    grad_fb = finite_grad_frame(objective_for_frame_b, frame_b)
    frame_b = frame_b + frame_lr * grad_fb

    # keep frames normalized for interpretability
    frame_a = normalize(frame_a)
    frame_b = normalize(frame_b)

state_history = np.array(state_history)
frame_a_history = np.array(frame_a_history)
frame_b_history = np.array(frame_b_history)

print("Final state:", state)
print("Final frame A:", frame_a)
print("Final frame B:", frame_b)
print("Final total score:", total_score_history[-1])
print("Final conflict:", conflict_history[-1])

# -----------------------------
# Plot 1: trajectory in state space
# -----------------------------
plt.figure(figsize=(8, 6))
plt.plot(state_history[:, 0], state_history[:, 1], linewidth=2)
plt.scatter(state_history[0, 0], state_history[0, 1], s=80, label="initial state")
plt.scatter(target_a[0], target_a[1], s=100, marker="x", label="target A")
plt.scatter(target_b[0], target_b[1], s=100, marker="x", label="target B")
plt.title("Gyro Conflict Demo: Inference Trajectory")
plt.xlabel("state x")
plt.ylabel("state y")
plt.legend()
plt.grid(True)
plt.show()

# -----------------------------
# Plot 2: score evolution
# -----------------------------
plt.figure(figsize=(8, 6))
plt.plot(score_a_history, label="stability A")
plt.plot(score_b_history, label="stability B")
plt.plot(total_score_history, label="total score")
plt.title("Stability Under Competing Frames")
plt.xlabel("step")
plt.ylabel("score")
plt.legend()
plt.grid(True)
plt.show()

# -----------------------------
# Plot 3: conflict evolution
# -----------------------------
plt.figure(figsize=(8, 6))
plt.plot(conflict_history)
plt.title("Frame Conflict Over Time")
plt.xlabel("step")
plt.ylabel("conflict")
plt.grid(True)
plt.show()
