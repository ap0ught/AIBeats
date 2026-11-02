"""Mesen trace of power-on intro + 1-1 rows: per-column first reach vs TAS; dump x/y in a t range.
python work/l11r/trace.py <rows file> [t0 t1]"""
import sys, csv
sys.path.insert(0, '.')
from ng.solve import common as C
from ng import fastcore as F
intro = C.rows_of('logs/a12_intro.inputs.txt')
rows = C.rows_of(sys.argv[1])
fc = F.FastCore(boot_rows=intro)
n, recs, st = fc.step(rows, record='all')
fc.close()
tas = {}
for r in csv.DictReader(open('logs/tas4751.trace.csv')):
    f = int(r['frame'])
    if 174 < f <= 2470:
        tas[f - 175] = {k: int(v) if v.lstrip('-').isdigit() else 0 for k, v in r.items() if k != 'input'}
def cols(seq):
    out = {}
    for t, s in enumerate(seq):
        if s['stage'] != seq[0]['stage']: out.setdefault('exit', t); break
        c = C.abs_x(s) // 64
        out.setdefault(c, t)
    return out
tl = [tas[i] for i in sorted(tas)]
a, b = cols(recs), cols(tl)
for c in sorted(set(a) | set(b), key=str):
    print(c, b.get(c), a.get(c), (a.get(c, 0) - b.get(c, 0)) if c in a and c in b else '')
if len(sys.argv) > 3:
    t0, t1 = int(sys.argv[2]), int(sys.argv[3])
    for t in range(t0, t1):
        s, u = recs[t], tl[t]
        print(t, 'ours', C.abs_x(s), s['y'], s['hp'], s['ninpo'], '| tas', C.abs_x(u), u['y'], u['hp'], u['ninpo'], u['rng'], rows[t])
