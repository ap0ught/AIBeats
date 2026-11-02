"""+5 X 784 y 160 lantern grid on the sync line (s1499): extra jump A at j (2 rows), B at b (2 rows) before the TAS jump
at 17,490; check np and sync (X,y vs base) at 17,560 and 17,700."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
base = [tuple(r) for r in C.rows_of('work/l42a/s1499.txt')]
fc = core(); _, rb, _ = fc.step(base[:17700 - F0], record='all'); fc.close()
fc = core(); fc.step(base[:17400 - F0], record='last'); fc.save('b'); fc._ka_slot = 'b'
batch = []; meta = []
for j in list(range(17405, 17488)) + [None]:
    for b in (range(j, j + 26) if j else range(17460, 17492)):
        rows = list(base[17400 - F0:17700 - F0])
        for f in (j, j + 1) if j else ():
            rows[f - 17401] = tuple(sorted(set(rows[f - 17401]) | {'A'}))
        for f in (b, b + 1):
            rows[f - 17401] = tuple(sorted(set(rows[f - 17401]) | {'B'}))
        if not L.check(base[:17400 - F0] + rows, HIST).get('pass'): continue
        batch.append(rows); meta.append((j, b))
print(len(batch), flush=True)
res = []
for i in range(0, len(batch), 150):
    rr = fc.run_batch('b', batch[i:i+150], record='all')
    for m, r in zip(meta[i:i+150], rr):
        st = r.states
        s1 = st[17560 - 17401]; s2 = st[-1]; t1 = rb[17560 - F0 - 1]; t2 = rb[-1]
        ok1 = (C.abs_x(s1), s1['y'], s1['hp']) == (C.abs_x(t1), t1['y'], t1['hp'])
        ok2 = (C.abs_x(s2), s2['y'], s2['hp']) == (C.abs_x(t2), t2['y'], t2['hp'])
        if s2['ninpo'] > t2['ninpo'] or (ok2 and s1['ninpo'] > t1['ninpo']): res.append((m, ok1, ok2, s1['ninpo'], s2['ninpo'], C.abs_x(s2), s2['y'], s2['hp'], s2['item']))
fc.close()
for q in res[:60]: print(q)
print('base', C.abs_x(rb[-1]), rb[-1]['y'], rb[-1]['ninpo'])
