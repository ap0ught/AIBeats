"""Wall-climb grammar enumeration from a TAS state (Mesen). Earliest frame meeting the goal.
python work/l52p/climb.py F0 'goal' [--pre 'Row*n,Row*n'] [--wall L|R] [--n 160] [--tail 'Left']
  wall L = the wall is on Ryu's LEFT (cling to a right face): away = Right, back = Left.
Families: C(a,b) = [A+away x2, away x a, back x b] repeated (a may be 0), D(b) = [A+back x2, back x b] (jump along the wall),
then after k cycles: tail rows (default: back) to the goal.  Prefix variants: --pre list separated by '|'."""
import sys, itertools
sys.path.insert(0, 'work/l52p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
PRE = opt('--pre', ''); WALL = opt('--wall', 'L'); N = opt('--n', 160); TAIL = opt('--tail', ''); TOP = opt('--top', 12)
KMAX = opt('--kmax', 9)
F0 = int(a[0]); G = compile(a[1], 'g', 'eval')
away, back = ('Right', 'Left') if WALL == 'L' else ('Left', 'Right')
TL = row(TAIL) if TAIL else (back,)
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
pres = [rr(p) for p in PRE.split('|')] if PRE else [[]]
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
AW, BK, AAW, ABK = (away,), (back,), ('A', away), ('A', back)
cands = {}
for pi, pre in enumerate(pres):
    for a_ in (0, 1, 2, 3):
        for b_ in (3, 4, 5, 6, 7, 8):
            cyc = [AAW] * 2 + [AW] * a_ + [BK] * b_
            for k in range(1, KMAX + 1):
                for t in ('tail', 'jtail'):
                    body = pre + cyc * k
                    body += ([tuple(sorted(TL))] * N) if t == 'tail' else ([tuple(sorted(('A',) + TL))] * 2 + [tuple(sorted(TL))] * N)
                    cands[f'p{pi} C{a_}{b_} x{k} {t}'] = body[:N]
    for b_ in (3, 4, 6, 8):
        cyc = [ABK] * 2 + [BK] * b_
        for k in range(1, 6):
            cands[f'p{pi} D{b_} x{k}'] = (pre + cyc * k + [BK] * N)[:N]
    cands[f'p{pi} plain'] = (pre + [tuple(sorted(TL))] * N)[:N]
ok = {k: v for k, v in cands.items() if not legal_ok(v, hist)}
print('cands', len(cands), 'legal', len(ok), flush=True)
names = list(ok); res = []
for i in range(0, len(names), 48):
    rs = fc.run_batch('b', [ok[n] for n in names[i:i+48]], record='all')
    for n, r in zip(names[i:i+48], rs):
        best = (999, None)
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'], it=s['item'], np=s['np64'])):
                res.append((F0 + 1 + k, s['hp65'], n)); break
res.sort()
for x in res[:TOP]: print(x, flush=True)
if not res: print('no goal')
fc.close()
