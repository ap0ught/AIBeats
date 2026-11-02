"""Kill the #19 bird with a slash near TAS-eq 23,550 and re-spawn it by a camera-left move at screen column 127.
From v2_24070 (lag 530). Rows: TAS rows (tosser-3 jump 23,546-47) with B+Right x2 at b, Left x n at l, then Right...
Reports bird slot info over time + hits."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
hist = [tuple(sorted(r)) for r in C.rows_of('work/l51b/h_v2_24070.inputs.txt')]
fc = core('states/mesen/l51b_v2_24070.mst'); fc.save('b'); fc._ka_slot = 'b'
L = 530
base = {23544: {'Right'}, 23545: {'Right'}, 23546: {'A', 'Right'}, 23547: {'A', 'Right'}}
res = []
cands = []
for b in range(24072, 24096):
    for l in range(b + 2, 24100):
        for n in (2, 3):
            w = tasleg(24071 - L, 23700, base)
            w = [set(x) for x in w]
            i = b - 24071; w[i] |= {'B'}; w[i + 1] |= {'B'}
            j = l - 24071
            w = w[:j] + [{'Left'}] * n + w[j:]
            rows = enforce(w, hist)[:200]
            if legal_ok(rows, hist): continue
            cands.append(((b, l, n), rows))
print('cands', len(cands), flush=True)
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        st = r.states
        # track type-11 occupancy
        t11 = [(24071 + t, RXY(s)[0] - s['x86'] + s[f'ex{j}'], s[f'ey{j}']) for t, s in enumerate(st) for j in range(8) if s['eact'] >> j & 1 and s[f't{j}'] == 11]
        frames = sorted(set(f for f, _, _ in t11))
        gap = [f for f in range(24071, 24071 + len(st)) if f not in set(frames)]
        respawn = None
        if gap:
            after = [x for x in t11 if x[0] > gap[0]]
            respawn = after[0] if after else None
        hits = trackhits(st, 24071)
        res.append((k, 'gap from', gap[0] if gap else None, 'respawn', respawn, 'hits', hits))
for x in res:
    if x[4]: print(x, flush=True)
print('done', len(res))
fc.close()
