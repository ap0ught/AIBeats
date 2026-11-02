"""NesHawk check of work/l52p/pre52_24625.txt: ref4751/13_5-2_control is AFTER row 24,428, so start from
ref4751/12_5-1_control + TAS rows to 24,426, then the prefix rows (row 1 = 24,427); compare with the TAS dump; also with $BF poked."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l52p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import *
TR = A.tas_rows()
rows = [tuple(l.strip().split('+')) if l.strip() != '-' else () for l in open('work/l52p/pre52_24625.txt') if l.strip() and not l.startswith('#')]
e = C.open_emu('l52p_nhpre.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/12_5-1_control')
    e.run_ram([tuple(TR[f - 1]) for f in range(st['frame'] + 1, 24427)]); base = e.msave()
    for bf in (None, 0, 100, 200):
        e.mload(base)
        if bf is not None: e.cmd(f'poke 191 {bf}') if False else None
        _, rams = e.run_ram(rows)
        div = next((24427 + i for i, m in enumerate(rams) if XY(m) != XY(TM(24427 + i)) or m[0x65] != TM(24427 + i)[0x65]), None)
        m = rams[-1]
        print('NesHawk prefix: first divergence', div, 'end X,y', XY(m), 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], flush=True)
        break
finally:
    e.close()
