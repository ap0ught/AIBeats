"""NesHawk: 2-2 control state + 2-2 stage rows (file) -> states/<out>.State at 2-3 control.
python work/l23/mkctl.py <2-2 start state name> <stage rows file> <out name>"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
st, rf, out = sys.argv[1:4]
rows = C.rows_of(rf)
e = C.open_emu('l23_mkctl.log')
try:
    e.tick(TICKS)
    s0 = e.load(st)
    e.run(rows)
    s = e.state()
    e.save(out)
    print('start frame', s0['frame'], 'end frame', s['frame'], {k: s.get(k) for k in ('stage', 'gm', 'x', 'y', 'hp', 'ninpo', 'item', 'rng')})
finally:
    e.close()
