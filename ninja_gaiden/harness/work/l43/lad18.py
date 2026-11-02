"""Room-18 entry: ladder cycle on the box's left face (X 96 column) vs r4q's ledge jumps.
Grid: wait d frames after 19,447, then a 5-frame ladder cycle (rotation k) repeated, then Right+jump variations;
report the first frame X >= 150 with y == 160 and the frame X >= 237."""
import sys, itertools
sys.path.insert(0, 'work/l43')
from lib import *
pre = rows_file('work/l43p/pre2_19599.txt')[:150]
fc = core(); fc.step(pre, record='last'); fc.save('b'); fc._ka_slot = 'b'
CYC = [('Right',), ('Right', 'Up'), ('Right', 'Up'), ('A', 'Left', 'Up'), ('A', 'Left')]
cands = []; meta = []
for d in range(0, 8):
    for k in range(5):
        for ncyc in range(4, 12):
            for tail in ('R', 'AR'):
                want = [()] * d
                cyc = CYC[k:] + CYC[:k]
                want += cyc * ncyc
                want += [('A', 'Right')] * 2 + [('Right',)] * 200 if tail == 'AR' else [('Right',)] * 202
                en = enforcer(pre)
                rows = [tuple(sorted(en.emit(w))) for w in want][:220]
                cands.append(rows); meta.append((d, k, ncyc, tail))
print(len(cands), 'candidates', flush=True)
res = []
B = 40
for i in range(0, len(cands), B):
    rr = fc.run_batch('b', cands[i:i + B], record='all')
    for j, r in enumerate(rr):
        f150 = f237 = None; top = None
        for q, s in enumerate(r.states):
            f = CTL + 150 + q
            X_ = C.abs_x(s)
            if top is None and s['y'] <= 160 and X_ >= 96: top = f
            if f150 is None and X_ >= 150 and s['room'] == 18: f150 = f
            if f237 is None and X_ >= 237 and s['room'] == 18: f237 = (f, s['y'], s['hp'])
        res.append((f237[0] if f237 else 99999, f150 or 99999, top, f237, meta[i + j]))
res.sort(key=lambda q: (q[0], q[1]))
import json; json.dump([[q[0], q[1], q[4]] for q in res[:40]], open('work/l43/lad18.json', 'w'))
for q in res[:25]: print(q)
fc.close()
