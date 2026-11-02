"""Compose stage rows = prefix rows[:N] + TAS rows (lag 165) with edits; play on Mesen; report hits/items/X.
python work/l31alt/tmod.py <prefix rows> N n --slash r1,r2 --keep r1,r2 (throw rows to keep) [--set r=SPEC,..]
  [--out file] [--every 20]
Rows numbered as stage rows (1 = first row after 3-1 control). Throws not in --keep become Right."""
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
out = opt('--out', ''); every = int(opt('--every', '20'))
rows = [tuple(r) for r in C.rows_of(a[0])]; N = int(a[1]); n = int(a[2])
TR = A.tas_rows()
LAGS = sorted([tuple(map(int, q.split(':'))) for q in opt('--lags', '').split(',') if q])
def lagf(r):
    L_ = 165
    for r0, l0 in LAGS:
        if r >= r0: L_ = l0
    return L_
TT = A.tas_trace()
want = list(rows[:N])
for k in range(N, n):
    w = tuple(TR[F0 + k - lagf(k + 1)])
    if 'Up' in w and 'B' in w and (k + 1) not in keep: w = ('Right',)
    if (k + 1) in sl: w = tuple(sorted(set(w) | {'B'}))
    if (k + 1) in sets: w = sets[k + 1]
    want.append(w)
lg = legal_after([], want)
fc = core(); _, recs, _ = fc.step(lg, record='all'); fc.close()
hp0 = 16; prev = None
for k, (s, r) in enumerate(zip(recs, lg)):
    key = (s['hp'], s['ninpo'], s['item'], s['stage'])
    if k >= N and (k % every == every - 1 or key != prev or r != want[k]):
        t = TT[F0 + k + 1 - lagf(k + 1)]
        print(k + 1, F0 + k + 1, '+'.join(r) or '-', ('(want ' + '+'.join(want[k]) + ')') if r != want[k] else '', 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'], 'st', s['stage'], 'loss_f %.1f' % ((32 + 1.5 * (k + 1) - C.abs_x(s)) / 1.5), '| TAS X', C.abs_x(t), 'y', t['y'])
    prev = key
if out: C.write_inputs(out, lg, f'tmod {" ".join(sys.argv[1:])}')
