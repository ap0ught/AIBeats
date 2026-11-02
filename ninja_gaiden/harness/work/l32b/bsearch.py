import sys
sys.path.insert(0, 'work/l32b')
from bmodel import sim
x0, sp0, scr0, X0 = 240 + 176/256, 0.0, 1185.5, 1313
H = 420
def run(stops):
    d = []
    for t in range(H):
        d.append(0.0 if any(a <= t < a + k for a, k in stops) else 1.5)
    out, gone = sim(x0, sp0, scr0, d)
    X = X0; ev = []; prev = None
    for (i, x, sp), dd in zip(out, d):
        X += dd
        if prev is not None and (prev < 128) != (x < 128):
            ev.append(('LR' if x >= 128 else 'RL', i, round(X)))
        prev = x
    return gone, ev
print('pure', run([]))
res = []
for t1 in range(0, 330, 2):
    for k in range(1, 25):
        g, ev = run([(t1, k)])
        if g is not None and g < 380: continue
        for e in ev:
            if e[0] == 'LR' and 1790 <= e[2] <= 1860:
                res.append((k, t1, e, ev))
res.sort()
for r in res[:30]: print(r)
print('survivors:')
seen = 0
for k in range(1, 40):
    for t1 in range(0, 330, 2):
        g, ev = run([(t1, k)])
        if g is None:
            print(k, t1, ev); seen += 1
            break
    if seen > 12: break
