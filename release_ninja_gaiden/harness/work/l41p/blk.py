"""15700-block high route grid (Mesen). From r2c state at K0 (=TAS sync), rows: Right; A held h frames from j;
optional slash (B or Down+B, 2 frames) at k. Goal: first frame standing (y 128) at X >= 1761 (TAS 15732, r2c ~15742).
python work/l41p/blk.py"""
import sys, time, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
K0 = 15580
fc.run_batch('s', [bytes(pads[:K0 - 14569])], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'
R, A_, B_, D_ = 1, 128, 64, 4
N = 190
def cand(j, h, k, sm, j2=None, h2=0):
    p = [R] * N
    for f in range(j, j + h): p[f - K0 - 1] |= A_
    if j2:
        for f in range(j2, j2 + h2): p[f - K0 - 1] |= A_
    if k:
        for f in (k, k + 1): p[f - K0 - 1] |= sm
    return bytes(p)
def score(st):
    for i, s in enumerate(st):
        if s['y'] == 128 and C.abs_x(s) >= 1761 and (s['anim'] in (0, 1)): return K0 + 1 + i, s['hp'], s['ninpo']
    return None, st[-1]['hp'], st[-1]['ninpo']
t = time.time()
cands = []; meta = []
for j in range(15581, 15606, 1):
    for h in (2, 4, 6, 8, 12, 16, 20):
        for k, sm in [(0, 0)] + [(kk, m) for kk in range(j + 4, j + 50, 3) for m in (B_, B_ | D_)]:
            cands.append(cand(j, h, k, sm)); meta.append((j, h, k, sm))
print('cands', len(cands), flush=True)
res = []
for i in range(0, len(cands), 50):
    rr = fc.run_batch('k1', cands[i:i+50], record='all')
    for m, r in zip(meta[i:i+50], rr):
        res.append((score(r.states), m))
print('time', time.time() - t, flush=True)
ok = [r for r in res if r[0][0]]
ok.sort(key=lambda r: (r[0][0], -r[0][1]))
for r in ok[:25]: print(r)
fc.close()
