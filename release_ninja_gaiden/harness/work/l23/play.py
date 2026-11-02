"""python work/l23/play.py <rows file> [pre 0/1] [poke BF delta,...] [verbose]
Play 2-3 rows from control (pre=0) or from control-1 (pre=1: first row = the last 2-2 row).
Prints kill row (first row with boss hp $66 == 0) per BF delta."""
import sys
sys.path.insert(0, 'work/l23')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
pre = len(sys.argv) > 2 and sys.argv[2] == '1'
deltas = [int(d) for d in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] != '-' else [0]
verb = len(sys.argv) > 4
fc = core('p' if pre else 'c')
fc.save('b')
res = {}
for d in deltas:
    fc.load('b')
    if d:
        bf = fc.ram()[0xBF]; fc.poke(0xBF, (bf + d) & 255)
    t = trace(fc, rows)
    kill = next((i + 1 for i, s in enumerate(t) if s['bhp'] == 0 and s['st'] == 4), None)
    res[d] = t
    print('delta', d, 'kill row', kill, '(rows counted from', 'control-1' if pre else 'control', ') end hp', t[-1]['hp'], 'np', t[-1]['np'], flush=True)
    if verb:
        for i, s in enumerate(t):
            print(i + 1, '+'.join(rows[i]) or '-', s)
if len(deltas) > 1:
    b = res[deltas[0]]
    for d in deltas[1:]:
        diff = next((i + 1 for i, (p, q) in enumerate(zip(b, res[d])) if {k: v for k, v in p.items() if k != 'bf'} != {k: v for k, v in q.items() if k != 'bf'}), None)
        print('delta', d, 'first non-BF difference at row', diff)
fc.close()
