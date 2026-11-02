"""X 2,336 (np 0): jump A at j (2 rows, replaces the TAS's 18,479), slashes B at b1 (and optional b2) - TAS rows after
(s1763). Report hits to END and X at END vs TAS."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
END = int(sys.argv[1]); B2 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
r = [tuple(x) for x in C.rows_of('work/l42a/s1763.txt')]
S = 18465
fc = core(); fc.step(r[:S - F0], record='last'); fc.save('b'); fc._ka_slot = 'b'
def clean(rows, lo, hi, btn):
    for f in range(lo, hi + 1):
        rows[f - F0 - 1] = tuple(x for x in rows[f - F0 - 1] if x != btn) or ('Right',)
batch = []; meta = []
for j in range(int(sys.argv[2]), int(sys.argv[3])):
    for b1 in [None] + list(range(j + 2, 18530)):
        for b2 in ([None] + list(range(b1 + 5, b1 + 25, 2))) if (b1 and B2) else [None]:
            rows = list(r[:END - F0])
            clean(rows, 18470, 18530, 'A'); clean(rows, 18470, 18545, 'B')
            for f in (j, j + 1): rows[f - F0 - 1] = ('A', 'Right')
            for bb in (b1, b2):
                if bb:
                    for f in (bb, bb + 1): rows[f - F0 - 1] = tuple(sorted(set(rows[f - F0 - 1]) | {'B'}))
            batch.append(rows[S - F0:]); meta.append((j, b1, b2, rows))
print(len(batch), flush=True)
res = []
for i in range(0, len(batch), 25):
    rr = fc.run_batch('b', batch[i:i + 25], record='all')
    for (j, b1, b2, rows), q in zip(meta[i:i + 25], rr):
        st = q.states
        hits = [S + 1 + k for k, s in enumerate(st) if k and s['hp'] < st[k - 1]['hp']]
        e = st[-1]
        res.append((len(hits), -C.abs_x(e), j, b1, b2, hits[:3], C.abs_x(e), e['y'], e['hp']))
fc.close()
res.sort(key=lambda q: (q[0], q[1]))
for q in res[:20]: print(q)
print('TAS X at END', C.abs_x(TT[END - 316]))
