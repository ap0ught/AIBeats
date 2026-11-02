"""Tail variants of a kill line: shift the jump (rows J,J+1) and the last wheel (rows T,T+1) by small amounts; report M.
    python work/l33/tail.py <tag> <rows> <J> <T> """
import sys, itertools
sys.path.insert(0, 'work/l33')
from sw import Ctx, C
tag, rf, J, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
base = [tuple(sorted(r)) for r in C.rows_of(rf)]
n0 = J - 1
pre = base[:n0]
seg = base[n0:]
jr = base[J - 1]; tr = base[T - 1]
wants, meta = [], []
for dj in range(-3, 5):
    for dt in range(-3, 6):
        for gap in ((), ('Right',), ('Left',)):
            w = [gap] * max(0, dj) + list(seg)
            # rebuild: jump at J+dj, throw at T+dt (relative)
            w = []
            L = 60
            for i in range(L):
                r = J + i
                w.append(())
            jj = max(0, dj) if dj >= 0 else 0
            w = [gap] * (dj if dj > 0 else 0)
            w += [jr, jr]
            k = len(w)
            tt = (T - J) + dt - (0 if dj > 0 else -dj) + (dj if dj > 0 else 0)
            while len(w) < tt: w.append(())
            w += [tr, tr]
            w += [()] * 40
            wants.append(w); meta.append((dj, dt, gap))
pre2 = pre if True else None
X = Ctx(tag)
res = X.run_from(pre, wants)
X.close()
out = sorted([(r['M'] or 9999, r['kill'], m) for r, m in zip(res, meta)], key=lambda q: q[0])
for q in out[:15]: print(q)
best = min(zip(res, meta), key=lambda q: (q[0]['M'] or 9999, q[1][0] != 0 or q[1][2] != ()))
r, m = best
print('chosen', m, 'kill', r['kill'], 'M', r['M'])
C.write_inputs(sys.argv[5] if len(sys.argv) > 5 else 'work/l33/tail_best.txt', list(r['rows'][:r['kill']]), f'tail variant {m} of {rf}: kill {r["kill"]} M {r["M"]}')
