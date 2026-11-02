"""Kill the trailing type-13 (slot 7) at the L+R spot with a left-facing air slash. Base s1499 rows 1-1380, jump
A+Right at j; Left on q..q+nl-1, B on q+o, q+o+1; Right elsewhere to 18,470. Report: slot-7 t13 alive at 18,430?, X/hp at 18,470."""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
base = [tuple(r) for r in C.rows_of('work/l42a/s1499.txt')][:1380]
fc = core(); fc.step(base, record='last'); fc.save('b'); fc._ka_slot = 'b'
en0 = L.Enforcer((HIST + base)[-1900:])
batch = []; meta = []
for j in (18381, 18382, 18383):
    for q in range(j + 1, j + 30):
        for nl in (2, 3, 4):
            for o in range(0, nl + 1):
                want = []
                for f in range(18378, 18471):
                    w = {'Right'}
                    if f in (j, j + 1): w = {'A', 'Right'}
                    if q <= f < q + nl: w = (w - {'Right'}) | {'Left'}
                    if f in (q + o, q + o + 1): w = w | {'B'}
                    want.append(tuple(sorted(w)))
                e = en0.copy(); lg = [tuple(sorted(e.emit(w))) for w in want]
                batch.append(lg); meta.append((j, q, nl, o))
res = []
for i in range(0, len(batch), 150):
    rr = fc.run_batch('b', batch[i:i + 150], record='all')
    for m, r in zip(meta[i:i + 150], rr):
        st = r.states
        s = st[18430 - 18378]; e = st[-1]
        res.append((C.abs_x(e), e['hp'], e['y'], int(s['t7'] == 13 and (s['eact'] >> 7) & 1), m))
fc.close()
dead = [q for q in res if q[3] == 0]
dead.sort(key=lambda t: (-t[1], -t[0]))
print(len(res), 'variants', len(dead), 'kill slot 7')
for q in dead[:30]: print(q)
