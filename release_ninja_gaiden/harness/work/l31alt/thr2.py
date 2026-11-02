"""Trace one Star throw at row i of a rows file: star x/y each frame + lanterns.  python work/l31alt/thr2.py rows i n"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
i = int(sys.argv[2]); n = int(sys.argv[3])
want = rows[:i] + [('B', 'Up')] + rows[i + 1:i + n]
lg = legal_after([], want)
fc = core(); fc.step(lg[:i], record='last')
for k in range(i, len(lg)):
    fc.step([lg[k]], record='last'); m = fc.ram()
    sc = X(m) - m[0x86]
    print(F0 + k + 1, '+'.join(lg[k]) or '-', 'ryu', X(m), m[0x8A], 'thr', [(sc + t['x'], t['y']) for t in H.thrown(m)], 'lan', [(sc + l['x'], l['y'], l['item'], l['state']) for l in H.lanterns(m)])
fc.close()
