"""Platform jump-off + throws from a state at our frame F0 (lag L: TAS frame = ours - L), then TAS rows to TAS 23,860.
python work/l51b/thr4.py <mst> F0 <hist> L"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
mst, F0, H, L = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
T1 = F0 + 1 - L; T2 = 23860
base = {23743: {'Right'}, 23778: {'Right'}}
ST = {'BUR': {'B', 'Up', 'Right'}, 'BU': {'B', 'Up'}, 'none': None}
cands = []
for dj in range(-2, 3):
    for t1 in range(23733, 23752):
        for s1 in ('BUR', 'BU'):
            for t2 in (0, 23770, 23775, 23778, 23781, 23785):
                m = dict(base)
                m[23741] = {'Right'}; m[23742] = {'Right'}
                m[23741 + dj] = {'A', 'Right'}; m[23742 + dj] = {'A', 'Right'}
                for t in (t1, t1 + 1): m[t] = ST[s1] | (m.get(t, set()) & {'A'})
                if t2:
                    for t in (t2, t2 + 1): m[t] = {'B', 'Up', 'Right'}
                rows = enforce(tasleg(T1, T2, m), hist)
                if legal_ok(rows, hist): continue
                cands.append(((dj, t1, s1, t2), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        st = r.states; ev = []; hp = np_ = None
        for j, s in enumerate(st):
            if hp is not None and s['hp65'] != hp: ev.append(f'{F0+1+j-L}:hp{hp}->{s["hp65"]}')
            if np_ is not None and s['np64'] != np_: ev.append(f'{F0+1+j-L}:np{np_}->{s["np64"]}')
            hp = s['hp65']; np_ = s['np64']
        X, y = RXY(st[-1]); dead = any(s['y8a'] >= 232 for s in st)
        res.append((dead, -st[-1]['hp65'], -X, k, (X, y), st[-1]['np64'], ' '.join(ev)))
res.sort(key=lambda q: q[:3])
for x in res[:30]: print(x, flush=True)
fc.close()
