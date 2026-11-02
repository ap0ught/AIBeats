"""Wait k frames (blank rows) at frame p on the s1763 line, then legal TAS rows at lag 316+k. Report hits/X to END."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
END = int(sys.argv[1]) if len(sys.argv) > 1 else 18700
r = [tuple(x) for x in C.rows_of('work/l42a/s1763.txt')]
S = 18420
fc = core(); fc.step(r[:S - F0], record='last'); fc.save('b'); fc._ka_slot = 'b'
batch = []; meta = []
for k in (1, 2, 3, 4):
    for p in range(S + 1, 18480):
        want = list(r[S - F0:p - F0 - 1]) + [()] * k
        f = p + k
        while f <= END:
            w = set(unud(TR[f - 316 - k - 1]))
            if 'Up' in w and 'B' in w: w = {'Right'}
            want.append(tuple(sorted(w))); f += 1
        lg = legal_after(r[:S - F0], want)
        batch.append(lg); meta.append((k, p))
res = []
for i in range(0, len(batch), 25):
    rr = fc.run_batch('b', batch[i:i + 25], record='all')
    for (k, p), q in zip(meta[i:i + 25], rr):
        st = q.states
        hits = [S + 1 + j for j, s in enumerate(st) if j and s['hp'] < st[j - 1]['hp']]
        e = st[-1]
        res.append((len(hits), -C.abs_x(e), k, p, hits[:3], C.abs_x(e), e['y'], e['hp']))
fc.close()
res.sort(key=lambda q: (q[0], q[1]))
for q in res[:15]: print(q)
print('TAS X at END', C.abs_x(TT[END - 316]))
