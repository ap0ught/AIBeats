"""NesHawk trace on the TAS path with $BF after the control row = c: stage rows file (row 1 = 22,125) [+ Right to END]; prints
Ryu and enemy slots every STEP frames in [F1, F2].  python work/l51p/nhtrace.py rows c n_rows END F1 F2 STEP"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l51p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import XY
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[1])]
c, n, END, F1, F2, STEP = map(int, sys.argv[2:8])
rows = rows[:n] + [('Right',)] * (END - 22124 - n)
TR = A.tas_rows()
e = C.open_emu('l51p_nhtrace.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/11_4-4_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, 22125)]); e.poke(0xBF, (c - 1) % 256)
    _, rams = e.run_ram(rows)
    for i, m in enumerate(rams):
        f = 22125 + i
        if F1 <= f <= F2 and (f - F1) % STEP == 0:
            X, y = XY(m); scr = X - m[0x86]
            es = [f's{j}t{m[0x400+j]}({scr + m[0x460+j]},{m[0x480+j]}) st{m[0x4A0+j] if False else ""}' for j in range(8) if m[0x73] >> j & 1]
            print(f, 'X', X, 'y', y, 'hp', m[0x65], 'BF', m[0xBF], '|', ' '.join(es))
finally:
    e.close()
