"""edit stage rows by frame: python work/l41/ed.py <in> <out> "f=A+Left,f2-f3=Right,..." [--trunc f]
(row for frame f = rows[f - (F0 + 1)]); also checks legality (history + rows)."""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
a = sys.argv[1:]
rows = list(C.rows_of(a[0])); out = a[1]; spec = a[2] if len(a) > 2 else ''
for q in spec.split(','):
    if not q: continue
    k, v = q.split('=')
    lo, hi = (k.split('-') + [k])[:2] if '-' in k else (k, k)
    for f in range(int(lo), int(hi) + 1):
        i = f - (F0 + 1)
        while len(rows) <= i: rows.append(())
        rows[i] = row(v)
if '--trunc' in a: rows = rows[:int(a[a.index('--trunc') + 1]) - F0]
chk = L.check(rows, hist_ctl())
C.write_inputs(out, rows, f'edit of {a[0]}: {spec}')
print('rows', len(rows), 'legal', chk['pass'], '' if chk['pass'] else str(chk)[:300])
