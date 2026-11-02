"""Pillar climb, per-cycle Right lengths: Right x j, A+Right x2, Right x wait, [A+Left x2, Right x b_i] for b in bs, A+Right x2."""
import sys, itertools; sys.path.insert(0, 'work/l51a')
from lib import *
MST = 'states/mesen/l51a_v2e4_24404.mst'; F0 = 24404
H = [tuple(sorted(r)) for r in C.rows_of('work/l51a/h_v2e4_24404.inputs.txt')]
fc = core(MST)
R, AR, AL = {'Right'}, {'A', 'Right'}, {'A', 'Left'}
res = []
for j in range(int(sys.argv[1]), int(sys.argv[2])):
    for wait in range(14, 26, 2):
        for bs in itertools.product(range(4, 10), repeat=3):
            for n_extra in (0, 1):
                cyc = []
                for b in bs: cyc += [AL] * 2 + [R] * b
                if n_extra: cyc += [AL] * 2 + [R] * 5
                ww = [R] * j + [AR] * 2 + [R] * wait + cyc + [AR] * 2 + [R] * 40
                en = A.Enforcer(H[-1900:]); rows = [tuple(sorted(en.emit(x))) for x in ww]
                fc.load('s'); _, recs, _ = fc.step(rows, record='all')
                hp = recs[0]['hp65']; g = None; hit = 0
                for i, s in enumerate(recs):
                    X, y = RXY(s)
                    if s['hp65'] < hp: hit = 1
                    if y >= 232: break
                    if X >= 2694 and y <= 128: g = F0 + 1 + i; break
                if g: res.append((g, hit, j, wait, bs, n_extra))
    res.sort(); print('j', j, res[:3], flush=True)
res.sort()
for r in res[:10]: print(r)
