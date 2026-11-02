import sys, json
sys.path.insert(0, 'work/l33')
from sw import *
O1 = "Right*3,A+Right*2,Right*13,-*2,Up+B*2,Left*14,Up+B*2"   # 38 rows; boss 10 by 42
X = Ctx('cB')
wants, meta = [], []
for r1 in range(0, 9):            # Right rows after the W2 throw (39..)
    for gap in range(0, 4):       # blank rows
        for nl in (2, 3, 4):     # Left rows
            for g2 in range(0, 3):
                w = spec(O1) + [('Right',)] * r1 + [()] * gap + [('Left',)] * nl + [()] * g2
                t = len(w) + 1
                if t < 43 or t > 56: continue
                wants.append(w + spec('Up+B*2') + [()] * 14); meta.append((r1, gap, nl, g2, t))
print('cands', len(wants), flush=True)
res = X.run(wants, chunk=48)
X.close()
out = []
for m, r in zip(meta, res):
    t = m[4]; s = r['sts']
    b0 = s[t - 2]['bosshp']
    out.append((b0 - r['boss'], -r['boss'], m, s[t - 1]['x'], s[t - 1]['y'], s[t - 1]['anim'], r['rhit'][:2], r['hits'][3:]))
out.sort(key=lambda o: (-o[0], o[2][4]))
for o in out[:30]: print(o)
