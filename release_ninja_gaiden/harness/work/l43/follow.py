"""Append legalized TAS rows to stage rows and trace vs the TAS.
python work/l43/follow.py <stage rows> N <tas_t1> <tas_t2> <out|-> [--step 4]
rows[:N] then TAS rows t1..t2 (L+R -> R, U+D -> none, 1-f A/B extended by the Enforcer against the real history).
Prints our X/y/hp vs the TAS at lag (N-th row frame + 1 - t1)."""
import sys
sys.path.insert(0, 'work/l43')
from lib import *
a = sys.argv[1:]
st = 4
if '--step' in a:
    i = a.index('--step'); st = int(a[i + 1]); del a[i:i + 2]
pre = rows_file(a[0])[:int(a[1])]; t1, t2 = int(a[2]), int(a[3]); out = a[4]
TR0 = A.tas_rows()
want = []
for t in range(t1, t2 + 1):
    w = set(TR0[t - 1])
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    want.append(tuple(sorted(w)))
en = enforcer(pre)
add = [tuple(sorted(en.emit(w))) for w in want]
rows = pre + add
print('legal:', legal_ok(rows, hist_chain()) or 'PASS')
fc = core()
_, recs, _ = fc.step(rows, record='all')
lag = CTL + len(pre) - t1
first = None
for i in range(len(pre), len(rows)):
    s = recs[i]; f = CTL + i; t = f - lag
    same = (C.abs_x(s), s['y'], s['room']) == (TX.get(t), TY.get(t), TRM.get(t))
    if not same and first is None: first = f
    if (i - len(pre)) % st == 0 or i == len(rows) - 1 or (not same and first == f):
        print(f, P(rows[i]), 'rm', s['room'], 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], '| TAS', t, TRM.get(t), TX.get(t), TY.get(t),
              '' if same else 'DIFF', ' '.join(f's{j}t{tt}@{x},{y}' for j, tt, x, y in enemies_s(s)))
print('lag', lag, 'first divergence', first)
if out != '-': write_rows(out, rows, f'follow TAS {t1}-{t2} lag {lag}'); print('wrote', out)
fc.close()
