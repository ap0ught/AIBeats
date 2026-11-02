"""Compose 4-2 stage rows = prefix rows[:N] + TAS rows (lag 316 default, --lags row:lag,..) with edits; play on Mesen.
python work/l42a/tmod.py <prefix rows|-> N n [--slash r1,..] [--keep r1,..] [--set r=SPEC,..] [--out f] [--every 20]
Stage row 1 = frame 16,998 (control row). TAS U+D dropped, L+R -> R. Throws (Up+B) not in --keep become Right."""
import sys
sys.path.insert(0, 'work/l42a')
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
out = opt('--out', ''); every = int(opt('--every', '20')); mst = opt('--mst', MST)
LAGS = sorted([tuple(map(int, q.split(':'))) for q in opt('--lags', '').split(',') if q])
rows = [tuple(r) for r in C.rows_of(a[0])] if a[0] != '-' else []; N = int(a[1]); n = int(a[2])
def lagf(r):
    L_ = LAG0
    for r0, l0 in LAGS:
        if r >= r0: L_ = l0
    return L_
def compose(sl, sets):
    want = list(rows[:N])
    for k in range(N, n):
        w = unud(TR[F0 + k - lagf(k + 1)])
        if 'Up' in w and 'B' in w and (k + 1) not in keep: w = ('Right',)
        if (k + 1) in sl: w = tuple(sorted(set(w) | {'B'}))
        if (k + 1) in sets: w = sets[k + 1]
        want.append(w)
    return want
if __name__ == '__main__':
    want = compose(sl, sets)
    lg = legal_after([], want)
    fc = core(mst); _, recs, _ = fc.step(lg, record='all'); fc.close()
    prev = None
    for k, (s, r) in enumerate(zip(recs, lg)):
        key = (s['hp'], s['ninpo'], s['item'], s['stage'], s['room'])
        if k >= N and (k % every == every - 1 or key != prev or r != want[k]):
            t = TT[F0 + k + 1 - lagf(k + 1)]
            print(k + 1, F0 + k + 1, '+'.join(r) or '-', ('(want ' + '+'.join(want[k]) + ')') if r != want[k] else '', 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'], 'st', s['stage'], 'rm', s['room'], '| TAS X', C.abs_x(t), 'y', t['y'], 'd', C.abs_x(t) - C.abs_x(s))
        prev = key
    if out: C.write_inputs(out, lg, f'tmod {" ".join(sys.argv[1:])}')
