"""Pillar (X 2,656 left face, top y 128) climb enumeration from the floor state 24,404 (X 2,596).
Rows: Right to jump frame j, A+Right x2, Right until cling, then n x [A+Left x a, Right x b], then Right/A+Right.
Score: first frame with X >= XG and y <= YG (default: on/above the pillar top past its middle)."""
import sys, itertools; sys.path.insert(0, 'work/l51a')
from lib import *
MST = 'states/mesen/l51a_v2e4_24404.mst'; F0 = 24404
H = [tuple(sorted(r)) for r in C.rows_of('work/l51a/h_v2e4_24404.inputs.txt')]
XG = int(sys.argv[1]) if len(sys.argv) > 1 else 2694; YG = int(sys.argv[2]) if len(sys.argv) > 2 else 128
fc = core(MST)
R, AR, AL, L = ('Right',), ('A', 'Right'), ('A', 'Left'), ('Left',)
res = []
for j in range(14, 40):
    for a, b, n, fin in itertools.product((2, 3), range(3, 10), range(1, 5), ('R', 'AR')):
        w = [set(R)] * j + [set(AR)] * 2
        cyc = [set(AL)] * a + [set(R)] * b
        for wait in (6, 10, 14):
            ww = w + [set(R)] * wait + cyc * n + ([set(AR)] * 2 if fin == 'AR' else []) + [set(R)] * 40
            en = A.Enforcer(H[-1900:]); rows = [tuple(sorted(en.emit(x))) for x in ww]
            fc.load('s'); _, recs, _ = fc.step(rows, record='all')
            hit = None; g = None; hp = recs[0]['hp65']
            for i, s in enumerate(recs):
                X, y = RXY(s)
                if s['hp65'] < hp and hit is None: hit = F0 + 1 + i
                if y >= 232: break
                if X >= XG and y <= YG: g = F0 + 1 + i; break
            if g: res.append((g, hit or 0, j, a, b, n, fin, wait))
    res.sort()
    print('j', j, 'best so far', res[:3], flush=True)
res.sort()
for r in res[:15]: print(r)
