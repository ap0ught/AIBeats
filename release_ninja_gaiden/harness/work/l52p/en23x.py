"""Room-23 exit, legal: from TAS 24,820 (J&S just taken, Ryu on the X-96 wall's right face area), C8 cycles
[A+Right x2, Right x a, Left x b] x k, then a jump AWAY from the wall (A+Right x h, Right x r: the wall flags are only
updated while y >= 72, $E677) and Left until the room changes.  python work/l52p/en23x.py [F0]"""
import sys, itertools
sys.path.insert(0, 'work/l52p')
from lib import *
F0 = int(sys.argv[1]) if len(sys.argv) > 1 else 24820; N = 150
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
L, R, AL, AR, Z = ('Left',), ('Right',), ('A', 'Left'), ('A', 'Right'), ()
cands = {}
for w in (0, 2, 4, 6):
    for a_ in (0, 2):
        for b_ in (4, 6, 8):
            for k in range(0, 7):
                for h in (2, 4, 8, 14):
                    for r in (0, 2, 4, 8):
                        for tail in ('L', 'AL'):
                            rows = [L] * w + ([AR] * 2 + [R] * a_ + [L] * b_) * k + [AR] * h + [R] * r
                            rows += ([L] * N) if tail == 'L' else ([AL] * 2 + [L] * N)
                            cands[(w, a_, b_, k, h, r, tail)] = rows[:N]
ok = {k: v for k, v in cands.items() if not legal_ok(v, hist)}
print('cands', len(cands), 'legal', len(ok), flush=True)
names = list(ok); res = []; near = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [ok[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rs):
        bx = 999
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if s['room6e'] == 24: res.append((F0 + 1 + k, s['hp65'], n)); break
            if s['room6e'] == 23 and s['hp65'] > 0: bx = min(bx, X)
        else: near.append((bx, n))
res.sort(); near.sort()
for x in res[:12]: print('EXIT', x, flush=True)
print('no exit; best X reached:', near[:5])
fc.close()
