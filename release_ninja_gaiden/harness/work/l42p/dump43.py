"""NesHawk: TAS 4-3 + legal r4_43q_x1 from ref4751/10_4-3_control -> ninpo/item/hp events."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l42p_d43.log')
def ev(tag, rams, f0):
    prev = None
    for i, m in enumerate(rams):
        s = (m[0x64], m[0xC9], m[0x65], m[0x6E], m[0x6D])
        if prev and s != prev:
            X = m[0x52]*256 + m[0x51] + m[0x86]
            print(tag, f0 + 1 + i, 'np/item/hp/room/stage', prev, '->', s, 'X', X, 'y', m[0x8A], 'pad', m[0x2A], flush=True)
        prev = s
try:
    e.tick(TICKS)
    st = e.load('ref4751/10_4-3_control'); f0 = st['frame']; print('4-3 state', f0, 'np', st['ninpo'], 'item', st['item'], 'hp', st['hp'])
    _, rams = e.run_ram(TR[f0:f0 + 2420]); ev('TAS', rams, f0)
    st = e.load('ref4751/10_4-3_control')
    _, rams = e.run_ram(C.rows_of('logs/a34/r4_43q_x1.inputs.txt')); ev('r4q', rams, f0)
finally:
    e.close()
