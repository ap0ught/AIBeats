"""NesHawk dumps for 4-3 prep: TAS 4-3 (ref4751/10_4-3_control + TAS rows, 2,460 f) -> work/l43p/tas43_ram.bin;
legal r4_43q_x1 from the same state -> work/l43p/r4q_ram.bin. 2048 B/frame, 4-byte f0 header."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l43p_dumps.log')
def dump(rows, out, st_name='ref4751/10_4-3_control'):
    st = e.load(st_name); f0 = st['frame']
    _, rams = e.run_ram(rows)
    with open(out, 'wb') as f:
        f.write(f0.to_bytes(4, 'little'))
        for m in rams: f.write(m)
    print(out, 'f0', f0, 'frames', len(rams), st, flush=True)
    return f0
try:
    e.tick(TICKS)
    st = e.load('ref4751/10_4-3_control'); f0 = st['frame']; print('state', st, flush=True)
    dump(TR[f0:f0 + 2460], 'work/l43p/tas43_ram.bin')
    rr = C.rows_of('logs/a34/r4_43q_x1.inputs.txt'); print('r4q rows', len(rr), flush=True)
    dump(rr + [()] * 60, 'work/l43p/r4q_ram.bin')
finally:
    e.close()
