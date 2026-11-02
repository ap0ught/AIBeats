"""Room-40 platform grid (legal U+D+L / L+R replacement), from TAS state 33792 (Ryu at (82,158) after the TAS's B+Left/Left):
A x2 (jump), then a Left/blank duty pattern (Left h, blank r) for n frames (~0.5 px/f like the TAS's U+D+L), blank w, Right t (turn),
A+Right x2, Right ... ; goal = on the y-96 platform at X >= 123 (TAS 33861)."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
F0 = 33792
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
cands = {}
for h, r in ((2, 4), (2, 3), (2, 2), (2, 5), (3, 3), (2, 6)):
    for n in range(14, 36, 2):
        duty = ([('Left',)] * h + [()] * r) * 20
        for w in range(0, 14, 2):
            for t in (0, 2, 3):
                rows = [('A',)] * 2 + duty[:n] + [()] * w + [('Right',)] * t + [('A', 'Right')] * 2 + [('Right',)] * 90
                if legal_ok(rows, hist): continue
                cands[(h, r, n, w, t)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rr = fc.run_batch('b', [cands[k] for k in names[i:i+64]], record='all')
    for k, r_ in zip(names[i:i+64], rr):
        for j, s in enumerate(r_.states):
            X, y = RXY(s)
            if y <= 96 and X >= 123 and s['hp65'] >= 14: res.append((F0 + 1 + j, k)); break
res.sort()
for x in res[:12]: print(x, flush=True)
if not res: print('no goal')
fc.close()
