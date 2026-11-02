import sys
sys.path.insert(0, 'work/l33')
from sw import Ctx, C, spec
pre = [tuple(sorted(r)) for r in C.rows_of('work/l33/preR104.txt')]   # x 141 at 104
X = Ctx('cB')
wants, meta = [], []
for k in range(0, 30, 2):           # more Right rows after 104
    for st in range(0, 16, 3):      # stand
        for mode in ('gB', 'jB', 'jDB'):
            for o in range(0, 12, 2):
                w = [('Right',)] * k + [()] * st
                t = 104 + len(w)
                if t > 150: continue
                if mode == 'gB':
                    w += [()] * o + (spec('B*2,-*14') * 3)
                else:
                    w += [()] * o + spec('A*2') + ((spec('B*2,-*3') if mode == 'jB' else spec('Down+B*2,-*3')) * 8)
                w += [()] * 10
                wants.append(w); meta.append((k, st, mode, o))
res = X.run_from(pre, wants)
X.close()
out = []
for r, m in zip(res, meta):
    hs = [h for h in r['hits'] if 130 <= h[0] <= 160]
    out.append((len(hs), m, hs[:6], r['rhit'][:2]))
out.sort(key=lambda q: -q[0])
for q in out[:15]: print(q)
