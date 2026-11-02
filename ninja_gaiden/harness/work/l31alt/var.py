"""Try spec variants after a prefix (rows file + N rows); print X/y/hp/np/item at the end + first hp loss.
python work/l31alt/var.py <rows> N n_total "<spec>" ...   (spec in wlib syntax; padded with Right to n_total rows)"""
import sys
sys.path.insert(0, 'work/l31alt'); sys.path.insert(0, 'work/w21')
from lib import *
from wlib import spec
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
N = int(sys.argv[2]); NT = int(sys.argv[3])
fc = core(); fc.step(rows[:N], record='last'); fc.save('p'); m = fc.ram(); hp0 = m[0x65]
for sp in sys.argv[4:]:
    want = spec(sp); want += [('Right',)] * (NT - len(want))
    lg = legal_after(rows[:N], want)
    fc.load('p'); _, recs, _ = fc.step(lg, record='all')
    hit = next((i for i, s in enumerate(recs) if s['hp'] < hp0), None)
    s = recs[-1]
    print(f'{sp:40s} end f {F0+N+NT} X {C.abs_x(s)} y {s["y"]} hp {s["hp"]} np {s["ninpo"]} it {s["item"]} first-hit row {hit}' + (f' X {C.abs_x(recs[hit])}' if hit is not None else ''))
fc.close()
