"""NesHawk: stage rows file from lock_31_ctl with the last k rows set to Right; print state at the end + 3 more Right."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
import os
ST = os.environ.get('ST', 'lock_31_ctl'); F00 = int(os.environ.get('F00', '9993'))
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
e = C.open_emu('l31alt_pretest.log')
try:
    e.tick(TICKS)
    for k in map(int, sys.argv[2:]):
        e.load(ST)
        rr = rows[:len(rows) - k] + [('Right',)] * k
        _, rams = e.run_ram(rr + [('Right',)] * 3)
        for j in range(-5, 0):
            m = rams[j]; f = F00 + len(rams) + j + 1
            print('k', k, 'frame', f, 'stage', m[0x6D], 'x', m[0x86], 'xsub', m[0x85], 'vx', m[0xAD], m[0xAC], '$62', m[0x62], 'rng', m[0xBF])
finally:
    e.close()
