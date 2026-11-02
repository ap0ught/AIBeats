"""Scan pillar jump row j1 (A+Right x h) [and optional 2nd jump j2] from base rows[:k0], Right otherwise;
report the tosser-1 hit (frame, X, y, knockback dir) and the knockback peak / wall cling.
python work/l32a/bscan2.py rows k0 j1lo j1hi [--j2 lo:hi] [--n 90] [--left r1-r2]"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
n = opt('--n', 90); j2s = opt('--j2', ''); lf = opt('--left', ''); hh = opt('--h', 2)
rows = [tuple(r) for r in C.rows_of(a[0])]; k0, lo, hi = int(a[1]), int(a[2]), int(a[3])
J2 = [None] if not j2s else list(range(int(j2s.split(':')[0]), int(j2s.split(':')[1]) + 1))
LF = set()
if lf:
    p, q = map(int, lf.split('-')); LF = set(range(p, q + 1))
fc = core(); fc.step(rows[:k0], record='last'); fc.save('p')
for j in range(lo, hi + 1):
    for j2 in J2:
        if j2 is not None and j2 <= j + 3: continue
        want = []
        for k in range(k0, k0 + n):
            r = ('Right',)
            if (k + 1) in LF: r = ('Left',)
            if j <= k + 1 < j + hh or (j2 is not None and j2 <= k + 1 < j2 + hh): r = ('A', 'Right')
            want.append(r)
        lg = legal_after(rows[:k0], want)
        fc.load('p'); _, recs, _ = fc.step(lg, record='all')
        hit = next((i for i, s in enumerate(recs) if s['hp'] < 16), None)
        if hit is None:
            print('j', j, 'j2', j2, 'no hit; end', C.abs_x(recs[-1]), recs[-1]['y'], recs[-1]['anim']); continue
        hs = recs[hit]; nx = recs[min(hit + 6, len(recs) - 1)]
        d = 'R' if C.abs_x(nx) > C.abs_x(hs) else 'L'
        cl = next((i for i in range(hit + 1, len(recs)) if recs[i]['anim'] == 10), None)
        pk = min(s['y'] for s in recs[hit:hit + 25])
        print('j', j, 'j2', j2, 'hit f', F0 + k0 + hit + 1, 'X', C.abs_x(hs), 'y', hs['y'], 'dir', d, 'peak', pk,
              'cling', (F0 + k0 + cl + 1, C.abs_x(recs[cl]), recs[cl]['y']) if cl is not None else None)
fc.close()
