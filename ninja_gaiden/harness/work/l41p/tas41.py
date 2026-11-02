"""NesHawk: TAS 4-1 from ref4751/08_4-1_control; dump per-frame RAM to work/l41p/tas41_ram.bin (2048 B/frame).
python work/l32p/tas32.py [n frames]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
n = int(sys.argv[1]) if len(sys.argv) > 1 else 2400
TR = A.tas_rows()
e = C.open_emu('l41p_tas41.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/08_4-1_control')
    f0 = st['frame']
    print('TAS 4-1 control state frame', f0)
    rows = TR[f0:f0 + n]
    _, rams = e.run_ram(rows)
finally:
    e.close()
with open('work/l41p/tas41_ram.bin', 'wb') as f:
    f.write(f0.to_bytes(4, 'little'))
    for m in rams: f.write(m)
print('frames', len(rams))
