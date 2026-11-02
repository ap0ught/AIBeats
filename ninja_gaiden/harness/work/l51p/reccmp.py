"""record 5-1 trace vs TAS: first t at each 32-px X bucket (t after control) + y; python work/l51p/reccmp.py [step]"""
import json, sys
sys.path.insert(0, 'work/l51p')
from lib0 import *
step = int(sys.argv[1]) if len(sys.argv) > 1 else 32
rec = json.load(open('work/a56r2/rec/r51.json'))
rq = [(r['t'], r['scroll'] + r['sx'] - 2, r['sy'] + 9) for r in rec['rows'] if r['sx'] is not None and r['t'] >= 0 and r['n'] >= 12 and r['room'] == 0]
tq = []
for f in range(CTL + 1, CTL + 2151):
    X, y = XY(TM(f)); tq.append((f - CTL, X, y))
def firsts(q):
    out = {}; mx = -1
    for t, x, y in q:
        if x > mx:
            for b in range(mx // step + 1 if mx >= 0 else 0, x // step + 1): out.setdefault(b, (t, y))
            mx = x
    return out
A, B = firsts(tq), firsts(rq)
prev = 0
for b in sorted(A):
    if b in B:
        d = B[b][0] - A[b][0]
        print(f'X {b*step:5d}  TAS t {A[b][0]:5d} y {A[b][1]:3d} | rec t {B[b][0]:7.1f} y {B[b][1]:3d} | rec-TAS {d:6.1f}  (sect {d-prev:+6.1f})')
        prev = d
