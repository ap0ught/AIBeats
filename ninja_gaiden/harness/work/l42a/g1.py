"""Grid at the TAS L+R spot (TAS 18065-18108 = our 18381-18424): kill the trailing type-13 walker with a LEFT air slash.
Base rows work/l42a/t1380.txt (rows to 1380 = frame 18377). Variants: ground Left turn rows (p,p+1) or none; jump A+Right
from j (2 rows); in the air Left on q,q+1 (B on q+bo,q+bo+1); Right elsewhere. Score: X at 18470, hp."""
import sys, itertools
sys.path.insert(0, 'work/l42a')
from lib import *
base = [tuple(r) for r in C.rows_of('work/l42a/t1380.txt')][:1380]
END = 18470
fc = core(); fc.step(base, record='last'); fc.save('b'); fc._ka_slot = 'b'
en0 = L.Enforcer((HIST + base)[-1900:])
res = []
batch = []; meta = []
for p in (None, 18379, 18380, 18381):
    for j in range(18381, 18388):
        if p and j < p + 2: continue
        for q in list(range(j + 1, j + 30)) + [None]:
            for bo in ((0, 1, 2) if q else (None,)):
                want = []
                for f in range(18378, END + 1):
                    w = {'Right'}
                    if p and f in (p, p + 1): w = {'Left'}
                    if f in (j, j + 1): w = {'A', 'Right'}
                    if q and f in (q, q + 1): w = (w - {'Right'}) | {'Left'}
                    if q is not None and f in (q + bo, q + bo + 1): w = w | {'B'}
                    want.append(tuple(sorted(w)))
                e = en0.copy(); lg = [tuple(sorted(e.emit(w))) for w in want]
                batch.append(lg); meta.append((p, j, q, bo))
print(len(batch), 'variants', flush=True)
for i in range(0, len(batch), 200):
    rr = fc.run_batch('b', batch[i:i + 200], record='last')
    for m, r in zip(meta[i:i + 200], rr):
        s = r.states[-1]
        res.append((C.abs_x(s), s['hp'], s['y'], s['item'], m))
res.sort(key=lambda t: (-(t[0] - 4 * (16 - t[1])),))
for t in res[:25]: print(t)
print('best hp16:', [t for t in res if t[1] == 16][:10])
fc.close()
