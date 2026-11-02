"""NesHawk dumps for 4-2 prep: TAS 4-2 (ref4751/09_4-2_control + TAS rows, 2,330 f) -> work/l42p/tas42_ram.bin;
legal 4-2_r2d from the same state -> work/l42p/r2d_ram.bin. 2048 B/frame, 4-byte f0 header."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l42p_dumps.log')
def dump(rows, out, st_name='ref4751/09_4-2_control'):
    st = e.load(st_name); f0 = st['frame']
    _, rams = e.run_ram(rows)
    with open(out, 'wb') as f:
        f.write(f0.to_bytes(4, 'little'))
        for m in rams: f.write(m)
    print(out, 'f0', f0, 'frames', len(rams), flush=True)
    return f0
try:
    e.tick(TICKS)
    st = e.load('ref4751/09_4-2_control'); f0 = st['frame']; print('state', st, flush=True)
    dump(TR[f0:f0 + 2330], 'work/l42p/tas42_ram.bin')
    rr = C.rows_of('logs/a34/4-2_r2d.inputs.txt'); print('r2d rows', len(rr), flush=True)
    dump(rr + [()] * 200, 'work/l42p/r2d_ram.bin')
finally:
    e.close()
