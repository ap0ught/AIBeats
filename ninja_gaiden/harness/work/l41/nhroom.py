"""NesHawk: from a state, play each rows file for N frames; print first frame of each room/stage change + min y.
python work/l41/nhroom.py <state> <N> <rows...>"""
import sys, time
sys.path.insert(0, 'work/l41')
from lib import *
from ng.mode import TICKS
stn = sys.argv[1]; N = int(sys.argv[2]); files = sys.argv[3:]
e = C.open_emu('l41_nhr.log')
try:
    e.tick(TICKS)
    for fn in files:
        rows = C.rows_of(fn)
        st = e.load(stn); f0 = st['frame']
        _, rams = e.run_ram(rows[f0 - F0:f0 - F0 + N])
        ev = []; prev = None
        for j, m in enumerate(rams):
            k = (m[0x6D], m[0x6E], m[0x65])
            if k != prev: ev.append((f0 + j + 1, k, X(m), m[0x8A]))
            prev = k
        print(fn, ev, 'last', X(rams[-1]), rams[-1][0x8A], flush=True)
finally:
    e.close()
