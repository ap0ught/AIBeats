"""Follow legalized TAS rows from a Mesen TAS state (Enforcer: 1-f -> 2-f, period 5); compare with the TAS.
python work/l63p/tf.py F0 F1 [--lr R|L] [--ud keep|drop] [--ov 'a-b=Row;c=Row'] [--every k] [--rows file] [--bf v]
  F0 = Mesen TAS state frame (l53p_tas<F0>.mst), rows F0+1..F1. --rows: use a rows file instead (one row per line).
Prints divergences (first frame where X,y differ), hp / np / item changes, and Ryu every k frames."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
LR = opt('--lr', 'R'); UD = opt('--ud', 'drop'); OV = opt('--ov', ''); EV = opt('--every', 0); RF = opt('--rows', ''); BF = opt('--bf', -1)
OUT = opt('--out', '')
F0, F1 = int(a[0]), int(a[1])
ov = {}
for part in [p for p in OV.split(';') if p]:
    k, v = part.split('=')
    if '-' in k: x, y = map(int, k.split('-'))
    else: x = y = int(k)
    for f in range(x, y + 1): ov[f] = set(row(v))
def want(f):
    if f in ov: return ov[f]
    w = set(T(f))
    if 'Up' in w and 'Down' in w and UD == 'drop': w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= ({'Left'} if LR == 'R' else {'Right'})
    return w
hist = [tuple(sorted(want(f) - ({'Left'} if {'Left','Right'} <= want(f) else set()) - ({'Up','Down'} if {'Up','Down'} <= want(f) else set()))) for f in range(F0 - 150, F0 + 1)]
if RF:
    rows = [row(l.strip()) for l in open(RF) if l.strip()]
else:
    en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(tuple(sorted(want(f)))))) for f in range(F0 + 1, F1 + 1)]
bad = legal_ok(rows, hist)
print('legal:', bad or 'ok', flush=True)
fc = core_at(F0)
if BF >= 0: fc.poke(0xBF, BF)
_, st, _ = fc.step(rows, record='all')
fc.close()
first = None; prev = None
for i, s in enumerate(st):
    f = F0 + 1 + i; X, y = RXY(s); tX, ty = tas_xy(f); m = TM(f)
    ev = []
    if (X, y) != (tX, ty) and first is None: first = f; ev.append(f'FIRST DIVERGENCE (TAS {tX},{ty})')
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    if ev or (EV and f % EV == 0):
        print(f, P(rows[i]), f'X {X} y {y} | TAS {tX},{ty} | hp {s["hp65"]} np {s["np64"]} it {s["item"]} rm {s["room6e"]} BF {s["bf"]}', ' '.join(ev))
    prev = s
if OUT:
    open(OUT, 'w').write('\n'.join(P(r) for r in rows) + '\n')
