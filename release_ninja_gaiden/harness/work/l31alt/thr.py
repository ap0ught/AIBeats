"""Sweep a single Star throw (Up+B replacing row i) over a range of rows of a stage-rows file; report whether the
FW lantern (item 10) / +10 (item 1) breaks and when.  python work/l31alt/thr.py <rows> i0 i1 [n after]"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
i0, i1 = int(sys.argv[2]), int(sys.argv[3]); na = int(sys.argv[4]) if len(sys.argv) > 4 else 60
fc = core()
fc.step(rows[:i0], record='last'); fc.save('p')
for i in range(i0, i1):
    want = rows[i0:i - 4] + [('Right',)] * 4 + [('B', 'Up')] + rows[i + 1:i + na]
    lg = legal_after(rows[:i0], want)
    fc.load('p')
    res = []
    for k, r in enumerate(lg):
        fc.step([r], record='last'); m = fc.ram()
        if k == i - i0: thr = (X(m), m[0x8A], m[0x64])
        for l in H.lanterns(m):
            if l['item'] in (10, 1) and l['state'] & 4 and (l['item'], ) not in [q[:1] for q in res]:
                res.append((l['item'], F0 + i0 + k + 1))
    print('throw row', i, 'frame', F0 + i + 1, 'at X,y,np', thr, 'breaks', res, 'legal', lg[i - i0])
fc.close()
