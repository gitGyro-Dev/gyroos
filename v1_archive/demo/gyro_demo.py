import numpy as np

state = np.array([0.2, -0.1, 0.4])
frame = np.array([0.5, 0.3, 0.1])
target = np.array([1.0, 1.0, 1.0])

def stability(s, f):
    return -np.linalg.norm(s - target) + np.dot(s, f)

def grad(s, f, eps=1e-5):
    g = np.zeros_like(s)
    for i in range(len(s)):
        sp, sm = s.copy(), s.copy()
        sp[i]+=eps; sm[i]-=eps
        g[i]=(stability(sp,f)-stability(sm,f))/(2*eps)
    return g

for step in range(20):
    state = state + 0.1 * grad(state, frame)
    print("step", step, "state", state, "score", stability(state, frame))
