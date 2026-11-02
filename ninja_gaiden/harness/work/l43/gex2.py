"""Room-19 exit: jump j, air slash b (2 f, B+Right), Right otherwise. Report first frame X >= 1176 and y there, hp."""
import sys, json; sys.path.insert(0, 'work/l43')
from lib import *
rows = rows_file('work/l43/b_q19_last.txt'); N = 1534; pre = rows[:N]   # after frame 20830
fc = core(); fc.step(pre, record='last'); fc.save('b'); fc._ka_slot = 'b'
cands = []; meta = []
for j in range(20836, 20850):
    for b in [None] + list(range(j + 3, j + 50)):
        want = []
        for f in range(20831, 20960):
            w = {'Right'}
            if f in (j, j + 1): w.add('A')
            if b and f in (b, b + 1): w.add('B')
            want.append(tuple(sorted(w)))
        en = enforcer(pre); cands.append([tuple(sorted(en.emit(w))) for w in want]); meta.append((j, b))
res = []
for i in range(0, len(cands), 80):
    for mt, r in zip(meta[i:i + 80], fc.run_batch('b', cands[i:i + 80], record='all')):
        g = None
        for q, s in enumerate(r.states):
            if C.abs_x(s) >= 1176: g = (20831 + q, s['y'], s['hp'], hex(s['coll'])); break
        res.append(((g[0] + (g[1] - 79) / 1.8) if g else 99999, str(mt), g))
res.sort()
for q in res[:15]: print(q)
fc.close()
