"""NesHawk dump for 6-1/6-2 prep: TAS from ref4751/15_5-4_control + TAS rows, to past the 6-3 control -> work/l61p/tas61_ram.bin.
2048 B/frame, 4-byte f0 header (RAM after row f0+1+i)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l61p_dumps.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/15_5-4_control'); f0 = st['frame']; print('state', st, flush=True)
    rows = TR[f0:f0 + 5500]
    _, rams = e.run_ram(rows)
    with open('work/l61p/tas61_ram.bin', 'wb') as f:
        f.write(f0.to_bytes(4, 'little'))
        for m in rams: f.write(m)
    print('f0', f0, 'frames', len(rams), flush=True)
finally:
    e.close()
