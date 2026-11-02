"""block parametric search: from 15870 (v_16477 prefix), Right + jump at j (A 2 f) + optional air B at k (2 f)
+ optional neutral pulse (t, d). metric: first frame X>=1767 and y==128 (r2c 16040)."""
import sys
sys.path.insert(0, 'work/l41')
from psearch import *
base = list(C.rows_of('work/l41/c3b.txt'))
D = F0 - 14866   # frames below are on the p4t axis; D shifts them to the current F0
S = 15870 + D; E = 16080 + D
pre = base[:S - F0]
cands = []; desc = []
def mk(j, k, t, d, kb='B'):
    r = [('Right',)] * (E - S)
    def setf(f, v):
        if S < f <= E: r[f - S - 1] = v
    if t:
        for f in range(t, t + d): setf(f, ())
    for f in (j, j + 1): setf(f, ('A', 'Right') if r[f - S - 1] else ('A',))
    if k:
        for f in (k, k + 1): setf(f, tuple(sorted(set(r[f - S - 1]) | {'B'})))
    return r
mode = sys.argv[1] if len(sys.argv) > 1 else 'a'
JR = range(15876, 15914) if mode == 'a' else range(15889, 15898)
for j in (q + D for q in JR):
    ks = [0] + list(range(j + 2, j + 52, 2))
    ts = [(0, 0)] if mode == 'a' else [(0, 0)] + [(t, d) for t in range(j + 4, j + 70, 3) for d in (2, 4, 7, 11, 16)]
    for k in (ks if mode == 'a' else [0]):
        for t, d in ts:
            r = mk(j, k, t, d)
            if legal(pre, r): cands.append(r); desc.append((j, k, t, d))
print('cands', len(cands), flush=True)
def metric(st, i):
    for s in st:
        if s['hp'] == 0 or s['item'] != 133: return None
        if C.abs_x(s) >= 1767 and s['y'] == 128 and s['room'] == 13: return s['frame'] - D
    return None
t = time.time()
res = run(cands, pre, metric)
print('time', round(time.time() - t), flush=True)
for v, i in res[:25]: print(v, desc[i], flush=True)
import json; json.dump([(v, desc[i]) for v, i in res if v], open(f'work/l41/blkp_{mode}.json', 'w'))
close()
