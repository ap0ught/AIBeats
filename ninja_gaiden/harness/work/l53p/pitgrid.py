"""Room 27, the record-style way past the pit: walk left k frames under the X-672 column, jump (A), grab its ladder face
('9' at X 672-687, approached from the left), climb with the cycle [A+Left x2, Right x6] n times (or Up m frames), then
A+Left jump-off onto the y-112 platform (X 448-639), run Left to its end and drop to the floor.
Goal: first frame with X <= 440 and y >= 200 (TAS: X 440 on 26776, y 208 on ~26788). From TAS state 26607 (control row 26608 = first row).
python work/l53p/pitgrid.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core(tas_mst(26607)); fc.save('b'); fc._ka_slot = 'b'
L, R, A, AL, U = ('Left',), ('Right',), ('A',), ('A', 'Left'), ('Up',)
cands = []; meta = []
for k in range(0, 16):
    for jump in ('A', 'AR'):
        for mode in ('cyc', 'up'):
            for n in (range(3, 11) if mode == 'cyc' else range(40, 100, 6)):
                rows = [L] * k + ([A, A] if jump == 'A' else [('A','Right')] * 2)
                rows += [()] * 3
                rows += ([AL, AL] + [R] * 6) * n if mode == 'cyc' else [U] * n
                rows += [(), (), AL, AL] + [L] * 260
                cands.append(rows[:330]); meta.append((k, jump, mode, n))
best = []
for i in range(0, len(cands), 48):
    rr = fc.run_batch('b', cands[i:i+48], record='all')
    for m, r in zip(meta[i:i+48], rr):
        g = None; ymin = 999
        for j, s in enumerate(r.states):
            X, y = RXY(s); ymin = min(ymin, y)
            if X <= 440 and y >= 200 and s['hp65'] > 0: g = 26608 + j; break
        e = r.states[min(j, len(r.states)-1)]
        best.append((g or 99999, m, e['hp65'], ymin, RXY(e)))
best.sort()
for b in best[:25]: print(b)
fc.close()
