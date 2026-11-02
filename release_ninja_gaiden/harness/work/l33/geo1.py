import sys, json
sys.path.insert(0, 'work/l33')
from sw import *
OPEN = "Right*3,A+Right*2,Right*13,-*2,Up+B*2,Left*14,Up+B*2,Right*8"
X = Ctx('cB')
wants, meta = [], []
for d in ('Left', 'Right'):
    for k in range(0, 16, 3):
        if d == 'Right' and k == 0: continue
        base = spec(OPEN) + spec('Left*2')            # rows 47-48: turn left
        mv = [(d,)] * k + ([('Left',), ('Left',)] if d == 'Right' and k else [])
        pre = base + mv
        t0 = len(pre)
        for t in range(max(t0 + 1, 49), 74):
            w = pre + [()] * (t - 1 - len(pre)) + spec('Up+B*2') + [()] * 20
            wants.append(w); meta.append(('G', d, k, t, 0))
        for J in range(max(t0 + 1, 49), 72):
            for o in range(2, 13):
                w = pre + [()] * (J - 1 - len(pre)) + spec('A*2') + [()] * (o - 2)
                tt = len(w) + 1
                w += spec('Up+B*2') + [()] * 16
                wants.append(w); meta.append(('J', d, k, tt, J))
print('cands', len(wants), flush=True)
res = X.run(wants, chunk=48, log=True)
X.close()
out = []
for m, r in zip(meta, res):
    t = m[3]
    s = r['sts']
    b0 = s[t - 2]['bosshp'] if len(s) >= t - 1 else None
    b1 = r['boss']
    hit = [h for h in r['rhit']]
    xs = s[t - 1]['x'] if len(s) >= t else None; ys = s[t - 1]['y'] if len(s) >= t else None
    nps = s[t - 1]['ninpo'] if len(s) >= t else None
    out.append(dict(m=m, dmg=(b0 - b1) if b0 is not None else None, x=xs, y=ys, np=nps, rhit=hit, hits=r['hits']))
json.dump(out, open('logs/l33/geo1.json', 'w'))
best = sorted(out, key=lambda o: (-(o['dmg'] or 0), o['m'][3]))
for o in best[:40]: print(o['m'], 'dmg', o['dmg'], 'x', o['x'], 'y', o['y'], 'np', o['np'], 'rhit', o['rhit'][:3], 'hits', o['hits'][-4:])
