
import numpy as np
import matplotlib.pyplot as plt

state = np.array([0.2, -0.1, 0.4], dtype=float)
frame = np.array([0.5, 0.3, 0.1], dtype=float)
target = np.array([1.0, 1.0, 1.0], dtype=float)

history = []

def stability(s, f):
    return -np.linalg.norm(s - target) + np.dot(s, f)

def grad(s, f, eps=1e-5):
    g = np.zeros_like(s)
    for i in range(len(s)):
        sp, sm = s.copy(), s.copy()
        sp[i]+=eps; sm[i]-=eps
        g[i]=(stability(sp,f)-stability(sm,f))/(2*eps)
    return g

def grad_frame(s, f, eps=1e-5):
    g = np.zeros_like(f)
    for i in range(len(f)):
        fp, fm = f.copy(), f.copy()
        fp[i]+=eps; fm[i]-=eps
        g[i]=(stability(s,fp)-stability(s,fm))/(2*eps)
    return g

for step in range(40):
    history.append(stability(state, frame))

    state = state + 0.1 * grad(state, frame)
    frame = frame + 0.05 * grad_frame(state, frame)

print("Final state:", state)
print("Final frame:", frame)

# plot
plt.plot(history)
plt.title("Stability over time")
plt.xlabel("step")
plt.ylabel("stability")
plt.show()
