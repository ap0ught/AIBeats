"""End scan: base rows file (stage rows) [:N], then TAS rows at lag L, with one edit row (B add / spec) at j in [lo,hi]
(optionally removing the TAS B at --drop r). Report first hp loss, X at row n, stage change.
python work/l32a/escan.py <rows> N n lo hi [--lag 188] [--spec S] [--drop r1,r2] [--width 2]"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
LAG = opt('--lag', 188); spec = opt('--spec', ''); drop = [int(q) for q in opt('--drop', '').split(',') if q]; wid = opt('--width', 2)
rows = [tuple(r) for r in C.rows_of(a[0])]; N, n, lo, hi = map(int, a[1:5])
def comp(j):
    want = list(rows[:N])
    for k in range(N, n):
        w = tuple(TR[F0 + k - LAG])
        if (k + 1) in drop: w = tuple(x for x in w if x != 'B')
        if j is not None and j <= k + 1 < j + wid:
            w = row(spec) if spec else tuple(sorted(set(w) | {'B'}))
        want.append(w)
    return legal_after([], want)
fc = core(); P0 = max(0, lo - 8); base = comp(None); fc.step(base[:P0], record='last'); fc.save('p')
hp0 = fc.ram()[0x65]
for j in [None] + list(range(lo, hi + 1)):
    lg = comp(j); fc.load('p'); _, recs, _ = fc.step(lg[P0:], record='all')
    hit = next((P0 + k + 1 for k, s in enumerate(recs) if s['hp'] < hp0), None)
    stc = next((P0 + k + 1 for k, s in enumerate(recs) if s['stage'] != 6), None)
    s = recs[-1]
    print('edit', j, 'hit', hit, 'stage change row', stc, 'end X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], flush=True)
fc.close()
