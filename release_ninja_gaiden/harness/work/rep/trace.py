"""Mesen trace of power-on rows (history + stage rows) vs the TAS trace in 1-1, fine first-reach table.
    python work/rep/trace.py <history file> <rows file> [--col 16] [--out csv]"""
import csv, sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng import fastcore as F
a = sys.argv[1:]
col = int(a[a.index('--col') + 1]) if '--col' in a else 32
hist = C.rows_of(a[0]); rows = C.rows_of(a[1])
f0 = len(hist)
fc = F.FastCore(boot_rows=hist)
n, recs, st = fc.step(rows, record='all')
fc.close()
T = list(csv.DictReader(open('logs/tas4751.trace.csv')))
def tint(r): return {k: int(v) for k, v in r.items() if k not in ('input',) and v.lstrip('-').isdigit()}
T = [tint(r) for r in T]
tc = 174
tas = {}
for k in range(tc - 1, 2600):
    s = T[k - 1]  # row k at index k-1
    if s['stage'] != 0: break
    key = (s['room'], C.abs_x(s) // col)
    tas.setdefault(key, (s['frame'] - tc, s['y']))
ours = {}
for s in recs:
    if s['stage'] != 0: break
    key = (s['room'], C.abs_x(s) // col)
    ours.setdefault(key, (s['frame'] - f0, s['y'], s['hp'], s['ninpo']))
for k in sorted(ours, key=lambda k: ours[k][0]):
    o = ours[k]; t = tas.get(k)
    print(f"room {k[0]} X {k[1]*col:5d} ours t {o[0]:5d} y {o[1]:3d} hp {o[2]:2d} np {o[3]:2d} | TAS " +
          (f"t {t[0]:5d} y {t[1]:3d} diff {o[0]-t[0]:+d}" if t else '-'))
last = [s for s in recs if s['stage'] == 0][-1]
print('last stage-0 frame', last['frame'], 'rows', n)
for s in recs:
    if s['stage'] != 0:
        print('stage change frame', s['frame']); break
