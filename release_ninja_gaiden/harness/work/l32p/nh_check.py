"""NesHawk check: TAS state 12054 (from ref4751/06_3-2_control + TAS rows), poke $BF, play rows; print key frames.
python work/l32p/nh_check.py <rows file from 12054> <bf at 12054> [bf2 ...]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
rows = C.rows_of(sys.argv[1]); bfs = [int(v) for v in sys.argv[2:]]
e = C.open_emu('l32p_nh.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/06_3-2_control'); f0 = st['frame']
    e.run(TR[f0:12054]); s = e.state(); print('at', s['frame'], 'x', s['x'], 'y', s['y'], 'rng', s['rng'])
    sid = e.msave()
    for bf in bfs:
        e.mload(sid); e.poke(0xBF, bf)
        sts, rams = e.run_ram(rows)
        top = x1252 = None; hp = 16
        for i, m in enumerate(rams):
            f = 12055 + i; X = m[0x52]*256 + m[0x51] + m[0x86]
            if top is None and X >= 1100 and m[0x8A] <= 96: top = f
            if x1252 is None and X >= 1252 and m[0x8A] <= 96: x1252 = f
            hp = min(hp, m[0x65])
        print('bf@12054', bf, 'tosser BF_s', (bf + 1) & 255, 'top', top, 'X1252', x1252, 'min hp', hp, flush=True)
finally:
    e.close()
