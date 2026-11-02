import sys; sys.path.insert(0,'.')
from ng.solve import common as C
from ng.mode import TICKS
e=C.open_emu('tk_l12_mkstate_emu.log')
try:
    e.reset(); e.tick(TICKS)
    rows=C.rows_of(sys.argv[1]); e.run(rows)
    s=e.state(); print('frame',s['frame'],'x',s['x'],'hp',s['hp'],'np',s['ninpo'],'rng',s.get('rng'))
    e.save(sys.argv[2])
finally: e.close()
