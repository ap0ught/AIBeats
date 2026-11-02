"""roof approach grid from N=378 without the TAS jump: run, jump at j, slash at j+s, land on sign, walk w, LA, climb, RA."""
import sys, itertools, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l11r')
from lib import *
from ng.solve import fast as FS
N = 378
hist = INTRO + BASE[:N]
wants, keys = [], []
for j, s, w, c in itertools.product(range(14, 34), range(4, 18, 2), range(0, 16, 2), (10, 12, 14)):
    sp = f"R:{j} RA:2 R:{s-2} RB:2 R:{30-s+w} LA:2 L:{c} RA:2 L:6 RA:2 R:40"
    wants.append(spec_rows(sp)[:150]); keys.append(sp)
L0 = max(len(x) for x in wants)
wants = [x + [('Right',)] * (L0 - len(x)) for x in wants]
cands = FS.legal_cands(wants, hist)
P = FS.pool(hist)
P.save_all('s')
t0 = time.time()
res = run_all(P, cands, record='all')
P.close()
print('ran', len(cands), time.time() - t0)
best = []
for key, c, r in zip(keys, cands, res):
    if r is None: continue
    hit = None
    for i, s in enumerate(r.states):
        if s['y'] <= 96 and C.abs_x(s) >= 720:
            hit = i; break
    if hit is not None:
        sts = r.states[:hit + 1]
        best.append((hit + N + 1, -min(q['hp'] for q in sts), -sts[-1]['ninpo'], key))
best.sort(key=lambda b: (b[1] > -16, b[2] > -20, b[0]))
print(len(best), 'reach')
for b in best[:15]:
    print(b)
