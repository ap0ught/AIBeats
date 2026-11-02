"""Pre-control Right at 4-1 (Mesen TAS state 14560): k blank rows then Right; print x per frame 14565-14575 and
the frame Ryu reaches abs X 100 / 300."""
import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14560.mst', 'rb').read())
for first in (14569, 14568, 14567, 14566, 14565, 14563):
    rows = [() if 14561 + i < first else ('Right',) for i in range(300)]
    st = fc.run_batch('s', [rows], record='all')[0].states
    xs = {14561 + i: C.abs_x(s) for i, s in enumerate(st)}
    x100 = next(f for f, x in xs.items() if x >= 100); x300 = next((f for f, x in xs.items() if x >= 200), max(xs.values()))
    print('first Right', first, [xs[f] for f in range(14565, 14576)], 'X100', x100, 'X200', x300)
fc.close()
