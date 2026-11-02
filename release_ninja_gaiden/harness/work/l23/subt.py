"""Mesen: does the 2-3 length depend on the timer sub-counter phase at control? Poke $62 at control-1 (after the
pre-control Left row is NOT yet played), play the kill rows + blanks, report the kill row, the timer at the kill,
the first cinematic-script row (= earliest Start; 3-1 control = that + const)."""
import sys
sys.path.insert(0, 'work/l23')
from lib import *
k23 = [tuple(r) for r in C.rows_of(sys.argv[1])][:90] + [()] * 700
vals = [None if v == '-' else int(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 else [None]
fc = core('p'); fc.save('b')
m = fc.ram(); print('at control-1: timer', m[0x63], 'sub', m[0x62])
for v in vals:
    fc.load('b')
    if v is not None: fc.poke(0x62, v)
    _, recs, _ = fc.step([('Left',)] + k23, record='all')
    kill = next(i for i, r in enumerate(recs) if r.get('bosshp', 1) == 0 and r.get('stage') == 4)
    cs = next((i for i, r in enumerate(recs) if r.get('cs')), None)
    print('sub poke', v, 'kill row', kill, 'timer at kill', recs[kill].get('timer'), recs[kill].get('subtimer'),
          'first cs row', cs, flush=True)
fc.close()
