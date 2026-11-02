"""Lantern grid on a sync rows file: extra jump A at j (2 rows) + B at b (2 rows) (j None = B only); check np gain and
sync (X, y, hp vs base) at frame CHK. python work/l42a/glan.py <rows> j1 j2 CHK [--jw A+Right]"""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
rows0 = [tuple(r) for r in C.rows_of(sys.argv[1])]; j1, j2, CHK = map(int, sys.argv[2:5])
S = j1 - 3
fc = core(); fc.step(rows0[:S - F0], record='last'); fc.save('b'); fc._ka_slot = 'b'
rb = fc.run_batch('b', [rows0[S - F0:CHK - F0]], record='last')[0].states[-1]
print('base at', CHK, 'X', C.abs_x(rb), 'y', rb['y'], 'hp', rb['hp'], 'np', rb['ninpo'], flush=True)
batch = []; meta = []
for j in list(range(j1, j2 + 1)) + [None]:
    for b in (range(j, j + 24) if j else range(j1, j2 + 24)):
        rows = list(rows0[:CHK - F0])
        for f in ((j, j + 1) if j else ()):
            rows[f - F0 - 1] = tuple(sorted(set(rows[f - F0 - 1]) | {'A'}))
        for f in (b, b + 1):
            rows[f - F0 - 1] = tuple(sorted(set(rows[f - F0 - 1]) | {'B'}))
        if not L.check(rows[S - F0 - 400:], HIST[-1] and []).get('pass'):
            pass
        batch.append(rows[S - F0:]); meta.append((j, b, rows))
res = []
for i in range(0, len(batch), 100):
    rr = fc.run_batch('b', batch[i:i + 100], record='last')
    for (j, b, rows), r in zip(meta[i:i + 100], rr):
        s = r.states[-1]
        if s['ninpo'] > rb['ninpo'] and s['item'] == 133:
            ok = (C.abs_x(s), s['y'], s['hp']) == (C.abs_x(rb), rb['y'], rb['hp'])
            leg = L.check(rows, HIST).get('pass')
            res.append((ok, leg, j, b, C.abs_x(s), s['y'], s['hp'], s['ninpo']))
fc.close()
res.sort(key=lambda t: (not t[0], not t[1]))
for q in res[:25]: print(q)
print(len(res), 'variants gain ninpo;', sum(1 for q in res if q[0] and q[1]), 'in sync + legal')
