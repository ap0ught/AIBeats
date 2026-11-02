"""NesHawk dump for 5-1 prep: TAS 5-1 (ref4751/12_5-1_control + TAS rows, to past the 5-2 control) -> work/l51p/tas51_ram.bin.
2048 B/frame, 4-byte f0 header (RAM after row f0+1+i)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l51p_dumps.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/12_5-1_control'); f0 = st['frame']; print('state', st, flush=True)
    rows = TR[f0:f0 + 2400]
    _, rams = e.run_ram(rows)
    with open('work/l51p/tas51_ram.bin', 'wb') as f:
        f.write(f0.to_bytes(4, 'little'))
        for m in rams: f.write(m)
    print('f0', f0, 'frames', len(rams), flush=True)
finally:
    e.close()
