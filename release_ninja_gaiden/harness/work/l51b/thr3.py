"""Throw grid (clean): TAS 23,700 state (c = 78 + lag), legal TAS rows with the TAS throws removed, throws at t1/t2 (2 f,
style BUR = Up+B+Right, BU = Up+B with Right released). python work/l51b/thr3.py lag"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
L = int(sys.argv[1]); c = 78 + L
S = 23700; N = 23990
hist = enforce(tasleg(S - 300, S), [()] * 30)
fc = core(tas_mst(S)); fc.poke(0xBF, (c + S - 22125) % 256); fc.save('b'); fc._ka_slot = 'b'
base = {23743: {'Right'}, 23778: {'Right'}}
cands = []
ST = {'BUR': {'B', 'Up', 'Right'}, 'BU': {'B', 'Up'}}
for t1 in range(23738, 23753):
    for t2 in list(range(t1 + 5, 23801)) + [0]:
        for s1 in ST:
            for s2 in ST:
                if t2 == 0 and s2 == 'BU': continue
                m = dict(base); m[t1] = m[t1 + 1] = ST[s1]
                if t2: m[t2] = m[t2 + 1] = ST[s2]
                rows = enforce(tasleg(S + 1, N, m), hist)
                cands.append(((t1, s1, t2, s2), rows))
print('cands', len(cands), flush=True)
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i + 100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        recs = r.states; ev = []; hp = np_ = None
        for j, s in enumerate(recs):
            if hp is not None and s['hp65'] != hp: ev.append(f'{S+1+j}:hp{hp}->{s["hp65"]}')
            if np_ is not None and s['np64'] != np_: ev.append(f'{S+1+j}:np{np_}->{s["np64"]}')
            hp = s['hp65']; np_ = s['np64']
        g = next((S + 1 + j for j, s in enumerate(recs) if RXY(s)[0] >= 2760 and s['y8a'] <= 100), None)
        x850 = RXY(recs[23850 - S - 1])
        res.append(((g or 99999), -recs[-1]['hp65'], -x850[0], k, x850, recs[-1]['hp65'], recs[-1]['np64'], ' '.join(ev)))
res.sort()
for r in res[:40]: print(r, flush=True)
# best by x at 23850 among hp-final >= 12 with health picked
print('--- by X@23850 with hp pickup')
r2 = sorted([r for r in res if 'hp9->15' in r[7] or 'hp8->14' in r[7]], key=lambda q: (q[2], q[0]))
for r in r2[:30]: print(r, flush=True)
fc.close()
