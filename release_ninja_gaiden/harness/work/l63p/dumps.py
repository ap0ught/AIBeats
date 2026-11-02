"""NesHawk TAS dump for 6-3 / 6-4 prep: from ref4751/16_6-1_control? no: from ref4751/18_6-3_control + TAS rows to past END -> work/l63p/tas63_ram.bin.
2048 B/frame, 4-byte f0 header (RAM after row f0+1+i). Also the pad byte list."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
print('tas rows', len(TR), flush=True)
e = C.open_emu('l63p_dumps.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/18_6-3_control'); f0 = st['frame']; print('state', st, flush=True)
    N = 39700 - f0
    rows = [tuple(TR[f]) if f < len(TR) else () for f in range(f0, f0 + N)]
    _, rams = e.run_ram(rows)
    with open('work/l63p/tas63_ram.bin', 'wb') as f:
        f.write(f0.to_bytes(4, 'little'))
        for m in rams: f.write(m)
    print('f0', f0, 'frames', len(rams), flush=True)
finally:
    e.close()
