"""+5 X 480 (room 19) grid on s_m19: replace rows from frame j with A+Right x2, B at b (2 f), keep the rest of the
TAS-lag rows; report np / X / y at frame 20480 and later TAS sync."""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
base = rows_file('work/l43/s_m19.txt')
J0 = 20360
fc = core(); fc.step(base[:J0 - CTL + 1], record='last'); fc.save('b'); fc._ka_slot = 'b'
cands = []; meta = []
for j in list(range(20361, 20412)) + [None]:
    for b in range(0, 26, 1):
        if j is None and b: continue
        want = [set(r) for r in base[J0 - CTL + 1:]]
        if j is not None:
            k = j - J0 - 1
            want[k] |= {'A', 'Right'}; want[k + 1] |= {'A', 'Right'}
            for q in (k + 4 + b, k + 5 + b):
                if q < len(want): want[q] |= {'B'}
        en = enforcer(base[:J0 - CTL + 1])
        cands.append([tuple(sorted(en.emit(tuple(sorted(w))))) for w in want]); meta.append((j, b))
res = []
for i in range(0, len(cands), 80):
    for m, r in zip(meta[i:i + 80], fc.run_batch('b', cands[i:i + 80], record='all')):
        s = r.states[20480 - J0 - 1]
        ok = (C.abs_x(s), s['y']) == (593, 165)
        res.append((-s["ninpo"], -ok, -C.abs_x(s), str(m), s['hp'], C.abs_x(s), s['y'], s['ninpo']))
res.sort()
for q in res[:15]: print(q)
fc.close()
