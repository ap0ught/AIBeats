"""3-3 Basaquer structured sweep on Mesen (first-pass kill attempt), from the state BEFORE the last pre-control row.
    python -u work/c5/b33grid.py <hist file> <mesen state> <out rows> [--np 23]
Phase A = the GA's 3-wheel opening (t3 varied), phase B = walk / jump / B every 5 f / wheel 4, swept."""
import itertools
import sys
import time

sys.path.insert(0, '.')
sys.path.insert(0, 'work/c5')
from b33lib import Ctx  # noqa: E402
from ng.solve import common as C  # noqa: E402

hf, mst, out = sys.argv[1:4]
H = 105
R, Lf = ('Right',), ('Left',)


def plan(p):
    w = [()] * H

    def put(i, r):
        if 0 <= i < H:
            w[i] = tuple(sorted(r))
    for i in range(0, 13):
        put(i, R)
    put(3, R + ('A',))
    put(4, R + ('A',))
    put(15, R)
    put(16, R)
    put(18, ('Up', 'B'))
    put(19, ('Up', 'B'))
    put(35, ('Up', 'B'))
    put(36, ('Up', 'B'))
    t3 = p['t3']
    for i in range(37, t3 - 2):
        put(i, R)
    put(t3 - 2, Lf)
    put(t3 - 1, Lf)
    put(t3, ('Up', 'B'))
    put(t3 + 1, ('Up', 'B'))
    b0 = t3 + 2
    d = p['d']
    for i in range(b0, b0 + p['w']):
        put(i, d)
    j = p['j']
    dj = p['dj']
    if j is not None:
        put(j, dj + ('A',))
        put(j + 1, dj + ('A',))
        for i in range(j + 2, j + 2 + p['fl']):
            put(i, dj)
        s = j + p['s0']
    else:
        s = b0 + p['w'] + p['s0']
    k = 0
    while s + 1 < H and k < p['ns']:
        put(s, tuple(set(w[s]) | {'B'}) if 'Up' not in w[s] else w[s])
        put(s + 1, tuple(set(w[s + 1]) | {'B'}) if 'Up' not in w[s + 1] else w[s + 1])
        s += 5
        k += 1
    t4 = p.get('t4')
    if t4 is not None:
        for i in range(t4 - 2, t4):
            if i >= 0 and w[i] and 'B' in w[i]:
                pass
        put(t4, ('Up', 'B'))
        put(t4 + 1, ('Up', 'B'))
    return w


def key(s):
    if s['dead']:
        return (3, 0, 0)
    if s['kill'] is not None:
        return (0, s['kill'], -s['minhp'])
    return (1, s['left'], -s['minhp'])


ctx = Ctx(hf, mst)
t0 = time.time()
grid = []
for t3, d, wl, j, dj, fl, s0 in itertools.product((45, 47, 49), (R, Lf, ()), (0, 4, 8), (None, 56, 60, 64, 68, 72),
                                                    (R, Lf, ()), (0, 6), (1, 3, 5)):
    if j is None and (dj != () or fl):
        continue
    if j is not None and j < t3 + 2 + wl:
        continue
    grid.append(dict(t3=t3, d=d, w=wl, j=j, dj=dj, fl=fl, s0=s0, ns=6))
print(len(grid), "stage-1 plans", flush=True)
res = ctx.run([plan(p) for p in grid], chunk=48, log=lambda s: print(s, flush=True))
sc = sorted(((key(s), i) for i, (_, s) in enumerate(res)))
for k, i in sc[:10]:
    print("S1", k, grid[i], res[i][1]['hits'], flush=True)
print(f"{time.time() - t0:.0f}s", flush=True)
# stage 2: wheel 4 on the top plans
top = []
seenk = set()
for k, i in sc:
    sig = (k, tuple(h for h in res[i][1]['hits']))
    if sig in seenk:
        continue
    seenk.add(sig)
    top.append(grid[i])
    if len(top) >= 40:
        break
g2 = []
for p in top:
    for t4 in range(66, 101, 2):
        for ns in (2, 3, 4, 6):
            g2.append(dict(p, t4=t4, ns=ns))
print(len(g2), "stage-2 plans", flush=True)
res2 = ctx.run([plan(p) for p in g2], chunk=48, log=lambda s: print(s, flush=True))
sc2 = sorted(((key(s), i) for i, (_, s) in enumerate(res2)))
for k, i in sc2[:12]:
    print("S2", k, g2[i], res2[i][1]['hits'], flush=True)
k, i = sc2[0]
legal, s = res2[i]
n = (s['kill'] + 1) if s['kill'] is not None else len(legal)
C.write_inputs(out, legal[:n], f"b33grid best {k} {g2[i]}")
print("saved", out, k, f"{time.time() - t0:.0f}s", flush=True)
ctx.close()
