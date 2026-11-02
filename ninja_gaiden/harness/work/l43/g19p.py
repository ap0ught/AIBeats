"""Room-19 box -> pillar top grid from a Mesen state: rows L*a, R*b, (gap d), A+R*2, R*60; first frame on the pillar
top (y 128, X >= 165) and X >= 212. python work/l43/g19p.py <mst> <frame0> [hist rows file N]"""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
mst, F0 = sys.argv[1], int(sys.argv[2])
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
cands = []; meta = []
for a_ in range(0, 12):
    for b in range(0, 14):
        for d in (0, 1, 2):
            want = [('Left',)] * a_ + [('Right',)] * b + [()] * d + [('A', 'Right')] * 2 + [('Right',)] * 70
            en = A.Enforcer([('Left',)] * 30)
            cands.append([tuple(sorted(en.emit(w))) for w in want]); meta.append((a_, b, d))
res = []
for i in range(0, len(cands), 60):
    for j, r in enumerate(fc.run_batch('b', cands[i:i+60], record='all')):
        top = g = None
        for q, s in enumerate(r.states):
            X_ = C.abs_x(s)
            if top is None and s['y'] == 128 and X_ >= 160: top = F0 + 1 + q
            if g is None and X_ >= 212 and s['y'] <= 128: g = F0 + 1 + q; break
        res.append((g or 99999, top or 99999, meta[i + j], r.states[-1]['hp']))
res.sort()
for q in res[:12]: print(q)
fc.close()
