import sys, itertools, subprocess
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.')
import xp
from ng.solve import common as C, legality as L
from ng import fastcore as F
mst, hf, rf, n = 'states/mesen/l32b_c2_13540.mst', 'work/l32b/h_c2_13540.inputs.txt', 'work/l32b/c2_t2.txt', 125
H = C.rows_of(hf); f0 = len(H); base = C.rows_of(rf)[:n]
R = ('Right',); def_ = lambda: [R] * n
specs = []
for j in range(13553, 13564):
    for a in range(13582, 13602, 2):
        for b in [None] + list(range(a + 6, a + 24, 3)):
            want = def_()
            for f in (j, j + 1): want[f - f0 - 1] = ('A', 'Right')
            for f in (a, a + 1): want[f - f0 - 1] = ('B', 'Right')
            if b:
                for f in (b, b + 1): want[f - f0 - 1] = ('B', 'Right')
            specs.append(((j, a, b), want))
cands = []
for k, w in specs:
    en = L.Enforcer(H[-1900:]); cands.append([tuple(sorted(en.emit(x))) for x in w])
fc = F.FastCore(boot_rows=None, ticks=True, fields=xp.FLD); fc.put('s', open(mst, 'rb').read()); fc.load('s')
out = []
for i in range(0, len(cands), 48):
    rr = fc.run_batch('s', cands[i:i+48], record='last')
    for (k, w), r in zip(specs[i:i+48], rr):
        s = r.states[-1]; ok = all(q['y'] <= 200 for q in r.states); out.append((ok and s['hp'] == 16, ok, C.abs_x(s), s['y'], k, s['hp'], s['stage']))
fc.close()
out.sort(key=lambda q: (-q[0], -q[1], -q[2]))
for q in out[:15]: print(q)
