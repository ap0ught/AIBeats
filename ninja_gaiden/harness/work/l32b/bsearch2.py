import sys, itertools
sys.path.insert(0, 'work/l32b')
from bmodel import sim
x0, sp0, scr0, X0 = 240 + 176/256, 0.0, 1185.5, 1313
H = 480
def run(stops):
    d = [0.0 if any(a <= t < a + k for a, k in stops) else 1.5 for t in range(H)]
    out, gone = sim(x0, sp0, scr0, d)
    X = X0; ev = []; prev = None
    for (i, x, sp), dd in zip(out, d):
        X += dd
        if prev is not None and (prev < 128) != (x < 128):
            ev.append(('LR' if x >= 128 else 'RL', i, round(X)))
        prev = x
    return gone, ev
if __name__ != "__main__": raise SystemExit
best = {}
for t1 in range(0, 300, 3):
    for k1 in range(1, 16):
        for t2 in range(t1 + k1 + 3, 330, 6):
            for k2 in range(0, 16, 1):
                g, ev = run([(t1, k1), (t2, k2)] if k2 else [(t1, k1)])
                for e in ev:
                    if 1780 <= e[2] <= 1850 and (g is None or g > e[1]):
                        key = (e[0], e[2] // 10)
                        c = k1 + k2
                        if key not in best or best[key][0] > c:
                            best[key] = (c, t1, k1, t2, k2, e, g)
for k in sorted(best): print(k, best[k])
