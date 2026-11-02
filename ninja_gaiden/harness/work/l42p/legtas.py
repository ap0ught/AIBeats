"""Legal TAS 4-2 rows: U+D dropped (-> Right), one-frame A/B extended to 2 frames (press frame + next); rows[0] = control
row 16,682. python work/l42p/legtas.py <to frame> <out> [beam file to append after frame S]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
import a56_common as A
TO = int(sys.argv[1]); out = sys.argv[2]
TR = A.tas_rows()
rows = []
for f in range(16682, TO + 1):
    r = set(TR[f - 1])
    if 'Up' in r and 'Down' in r: r -= {'Up', 'Down'}
    rows.append(r)
for i in range(1, len(rows)):
    for b in ('A', 'B'):
        if b in rows[i] and b not in rows[i - 1] and (i + 1 >= len(rows) or b not in rows[i + 1]):
            if i + 1 < len(rows): rows[i + 1].add(b)
rows = [tuple(sorted(r)) for r in rows]
if len(sys.argv) > 3:
    bm = C.rows_of(sys.argv[3]); rows = rows[:17440 - 16681] + [tuple(r) for r in bm[17440 - 16681:]]
from ng.solve.legality import check
print('legal', check(rows, [()] * 300)['pass'], len(rows))
C.write_inputs(out, rows, 'legalized TAS 4-2 rows (U+D dropped, A/B 2 f)' + (f' + {sys.argv[3]} after 17,440' if len(sys.argv) > 3 else ''))
