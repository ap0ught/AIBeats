"""Scan one extra edit row (B slash, or --spec SPEC) over [lo, hi] on the tmod composition; report first hit / end.
python work/l31alt/tscan.py <prefix rows> N n --slash .. --keep .. [--set ..] lo hi [--spec 'B+Right'] [--width 1]"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return v
    return d
sl = {int(q) for q in opt('--slash', '').split(',') if q}
keep = {int(q) for q in opt('--keep', '').split(',') if q}
sets = {}
for q in opt('--set', '').split(','):
    if q:
        k, v = q.split('='); sets[int(k)] = row(v)
spec = opt('--spec', ''); wid = int(opt('--width', '1'))
rows = [tuple(r) for r in C.rows_of(a[0])]; N = int(a[1]); n = int(a[2]); lo, hi = int(a[3]), int(a[4])
TR = A.tas_rows()
LAGS = sorted([tuple(map(int, q.split(':'))) for q in opt('--lags', '').split(',') if q])
def lagf(r):
    L_ = 165
    for r0, l0 in LAGS:
        if r >= r0: L_ = l0
    return L_
def compose(sl, sets):
    want = list(rows[:N])
    for k in range(N, n):
        w = tuple(TR[F0 + k - lagf(k + 1)])
        if 'Up' in w and 'B' in w and (k + 1) not in keep: w = ('Right',)
        if (k + 1) in sl: w = tuple(sorted(set(w) | {'B'}))
        if (k + 1) in sets: w = sets[k + 1]
        want.append(w)
    return legal_after([], want)
fc = core()
P0 = min([lo] + list(sl) + list(sets)) - 6
base = compose(sl, sets)
fc.step(base[:P0], record='last'); fc.save('p')
for j in [None] + list(range(lo, hi + 1)):
    s2 = dict(sets); sl2 = set(sl)
    if j is not None:
        for d in range(wid):
            if spec: s2[j + d] = row(spec)
            else: sl2.add(j + d)
    lg = compose(sl2, s2)
    fc.load('p'); _, recs, _ = fc.step(lg[P0:], record='all')
    hit = next((P0 + k + 1 for k, s in enumerate(recs) if s['hp'] < 16), None)
    s = recs[-1]
    print('edit', j, 'first hit row', hit, 'end X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'], 'loss_f %.1f' % ((32 + 1.5 * n - C.abs_x(s)) / 1.5))
fc.close()
