"""Throw grid keeping the bird: from a state at our F0 (lag L), platform jump dj, one Windmill (t1, style), TAS rows to 23,990.
Reports hp, np, bird alive at TAS-eq 23,860 + rel pos, and the first frame with X>=2760 y<=100 (the TAS's 23,905 route).
python work/l51b/thr5.py <mst> F0 <hist> L"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
mst, F0, H, L = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
T1 = F0 + 1 - L; T2 = 23995
ST = {'BUR': {'B', 'Up', 'Right'}, 'BU': {'B', 'Up'}}
cands = []
for dj in (-2, -1, 0):
    for t1 in [0] + list(range(23733, 23800)):
        for s1 in (('BUR', 'BU') if t1 else ('BUR',)):
            m = {23743: {'Right'}, 23778: {'Right'}, 23741: {'Right'}, 23742: {'Right'}}
            m[23741 + dj] = {'A', 'Right'}; m[23742 + dj] = {'A', 'Right'}
            if t1:
                for t in (t1, t1 + 1): m[t] = ST[s1] | (m.get(t, set()) & {'A'})
            rows = enforce(tasleg(T1, T2, m), hist)
            if legal_ok(rows, hist): continue
            cands.append(((dj, t1, s1), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        st = r.states
        k860 = 23860 + L - F0 - 1
        s = st[k860]; X, y = RXY(s); scr = X - s['x86']
        birds = [(scr + s[f'ex{j}'] - X, s[f'ey{j}'] - y) for j in range(8) if s['eact'] >> j & 1 and s[f't{j}'] == 11]
        g = next((F0 + 1 + t for t, q in enumerate(st) if RXY(q)[0] >= 2760 and q['y8a'] <= 100), None)
        dead = any(q['y8a'] >= 232 for q in st)
        hps = [q['hp65'] for q in st]
        res.append((dead, g or 99999, -s['hp65'], k, (X, y), s['hp65'], s['np64'], birds, hps[-1]))
res.sort(key=lambda q: q[:3])
for x in res[:30]: print(x, flush=True)
print('--- bird alive at 23,860, hp >= 12')
for x in [q for q in res if q[7] and q[5] >= 12][:30]: print(x, flush=True)
fc.close()
