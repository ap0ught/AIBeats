"""Room 19: replace the TAS spin #2 (our 20,423) by a spin that breaks +5 X 480 y 144 (net 0) and still clears the
type-6 pair: base s_m19 with B removed at 20,423-24; add an extra jump j (A+R 2 f) and B at b (2 f).
Report np/hp/X/y at 20,480 (TAS line: X 593 y 165, np 0)."""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
base = rows_file('work/l43/s_m19.txt')
J0 = 20350
fc = core(); fc.step(base[:J0 - CTL + 1], record='last'); fc.save('b'); fc._ka_slot = 'b'
cands = []; meta = []
for j in [None] + list(range(20360, 20420)):
    for b in range(0, 30):
        want = [set(r) for r in base[J0 - CTL + 1:]]
        for f in (20423, 20424): want[f - J0 - 1].discard('B')
        if j is not None:
            for f in (j, j + 1): want[f - J0 - 1] |= {'A', 'Right'}
            bb = j + 3 + b
        else:
            bb = 20380 + b
        for f in (bb, bb + 1):
            if f - J0 - 1 < len(want): want[f - J0 - 1] |= {'B'}
        en = enforcer(base[:J0 - CTL + 1])
        cands.append([tuple(sorted(en.emit(tuple(sorted(w))))) for w in want]); meta.append((j, bb))
print(len(cands), flush=True)
res = []
for i in range(0, len(cands), 80):
    for m, r in zip(meta[i:i + 80], fc.run_batch('b', cands[i:i + 80], record='all')):
        s = r.states[20480 - J0 - 1]
        res.append((-s['ninpo'], s['hp'] < 15, abs(C.abs_x(s) - 593) + abs(s['y'] - 165), str(m), s['hp'], C.abs_x(s), s['y'], s['ninpo']))
res.sort()
for q in res[:15]: print(q)
fc.close()
