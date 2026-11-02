"""Kill grid from a 4-4 pre-control state (rows start at the control row = stage row 1).
Candidates: control-row input c0, jump press row j (A held ha rows) with air direction d, B press row b (held 2) with dir db.
Every candidate is legalized by the Enforcer after the power-on history (judge semantics). Reports the kill row (boss HP 0)
distribution and the best rows.   python work/l44p/grid.py [--mst m] [--poke 0xBF=v,...] [--hist powerfile] [--n 60]"""
import sys, itertools, collections
sys.path.insert(0, 'work/l44p')
from lib import *
from ng.solve import legality as L
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
mst = opt('--mst', PRE); pk = opt('--poke', None); hist = opt('--hist', None); N = int(opt('--n', '30'))
pokes = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in pk.split(','))} if pk else {}
H = C.rows_of(hist)[-1900:] if hist else [()] * 300
def legal(want):
    en = L.Enforcer(list(H))
    return [tuple(sorted(en.emit(w))) for w in want]
cands, meta = [], []
for c0 in ('Left', '', 'A+Left'):
    for j in range(1, 5):
        for ha in (2, 6):
            for d in ('', 'Left', 'Right'):
                for b in range(j + 1, j + 9):
                    for db in ('', 'Right'):
                        w = [row(c0)] + [()] * (N - 1)
                        for k in range(j, min(N, j + ha)):
                            w[k - 1] = tuple(sorted(set(w[k - 1]) | {'A'} | ({d} if d else set())))
                        for k in range(j + ha, N):
                            if d: w[k - 1] = tuple(sorted(set(w[k - 1]) | {d}))
                        for k in (b, b + 1):
                            w[k - 1] = tuple(sorted((set(w[k - 1]) - {'Left', 'Right'}) | {'B'} | ({db} if db else set())))
                        if c0.startswith('A') and j == 1: pass
                        w = legal(w)
                        cands.append(w); meta.append((c0, j, ha, d, b, db))
# dedupe
seen = {}
for w, m in zip(cands, meta):
    seen.setdefault(tuple(w), m)
cands = list(seen); meta = [seen[w] for w in cands]
print('candidates', len(cands), flush=True)
fc = core(mst)
for k, v in pokes.items(): fc.poke(k, v)
fc.save('g'); fc._ka_slot = 'g'
res = []
for k in range(0, len(cands), 40):
    res += fc.run_batch('g', cands[k:k + 40], stops=[(0x66, '==', 0)])
    print('done', k, flush=True) if k % 1000 == 0 else None
fc.close()
dist = collections.Counter()
best = []
for w, m, r in zip(cands, meta, res):
    kill = r.rows_played if r.status == 1 else None
    dist[kill] += 1
    best.append((kill or 999, m, w))
print('kill row distribution (stage row; control row = 1):', sorted(dist.items(), key=lambda q: (q[0] is None, q[0] or 0)))
best.sort(key=lambda q: q[0])
for k, m, w in best[:12]:
    print(k, m, ' '.join(P(x) for x in w[:k]))
