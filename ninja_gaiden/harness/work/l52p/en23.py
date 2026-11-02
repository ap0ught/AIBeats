"""enumerate small legal grammars from a TAS state; earliest frame meeting a goal. python work/l52p/en23.py F0 goal"""
import sys, itertools
sys.path.insert(0, 'work/l52p')
from lib import *
F0 = int(sys.argv[1]); G = compile(sys.argv[2], 'g', 'eval'); N = 90
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
L, R, AL, AR, Z = ('Left',), ('Right',), ('A', 'Left'), ('A', 'Right'), ()
cands = {}
for w1 in range(0, 16):
    for first in ('L', 'Z'):
        p0 = [L if first == 'L' else Z] * w1
        for r in range(0, 8):
            for jb in ('AR', 'AL', 'A'):
                j = {'AR': AR, 'AL': AL, 'A': ('A',)}[jb]
                for hold in (2, 3, 4, 6, 10):
                    rows = p0 + [j] * hold + [R] * r + [L] * N
                    cands[f'{first}{w1} {jb}x{hold} R{r}'] = rows[:N]
ok = {k: v for k, v in cands.items() if not legal_ok(v, hist)}
print('cands', len(cands), 'legal', len(ok), flush=True)
names = list(ok); res = []
for i in range(0, len(names), 64):
    rr = fc.run_batch('b', [ok[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rr):
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'])):
                res.append((F0 + 1 + k, s['hp65'], n)); break
res.sort()
for x in res[:15]: print(x)
fc.close()
