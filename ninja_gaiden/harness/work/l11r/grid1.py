"""roof climb grid from N=421: RA:2, R:k, -: until j2, L+A at j2 (hold L), R+A at j3, then R."""
import sys, itertools, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l11r')
from lib import *
from ng.solve import fast as FS
N = 421
hist = INTRO + BASE[:N]
wants, keys = [], []
for k, j2, j3 in itertools.product(range(3, 10), range(19, 24), range(6, 26, 2)):
    w = [('A', 'Right')] * 2 + [('Right',)] * k
    w += [()] * max(0, j2 - len(w))
    w = w[:j2]
    w += [('A', 'Left'), ('A', 'Left')] + [('Left',)] * (j3 - 2)
    w += [('A', 'Right'), ('A', 'Right')] + [('Right',)] * 40
    wants.append(w); keys.append((k, j2, j3))
cands = FS.legal_cands(wants, hist)
P = FS.pool(hist)
P.save_all('s')
t0 = time.time()
res = FS.run_chunked(P, 's', cands, chunk=12, record='all', log=print)
P.close()
print('ran', len(cands), time.time() - t0)
best = []
for key, c, r in zip(keys, cands, res):
    hit = None
    for i, s in enumerate(r.states):
        if s['y'] <= 96 and C.abs_x(s) >= 704 and i > 0 and r.states[i-1]['y'] == s['y']:
            hit = i; break
    if hit is not None:
        best.append((hit, -min(s['hp'] for s in r.states[:hit+1]), key, C.abs_x(r.states[hit])))
best.sort()
print(len(best), 'reach roof')
for b in best[:15]:
    print(b)
