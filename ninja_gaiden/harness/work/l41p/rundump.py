"""NesHawk: from a ref4751 state, play a rows file, dump per-frame RAM (2048 B/frame, 4-byte f0 header).
python work/l41p/rundump.py <state> <rows file> <out.bin> [bf poke at the state]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
st_name, rf, out = sys.argv[1], sys.argv[2], sys.argv[3]
bf = int(sys.argv[4]) if len(sys.argv) > 4 else None
rows = C.rows_of(rf)
e = C.open_emu('l41p_rd.log')
try:
    e.tick(TICKS)
    st = e.load(st_name); f0 = st['frame']
    if bf is not None: e.poke(0xBF, bf)
    _, rams = e.run_ram(rows)
finally:
    e.close()
with open(out, 'wb') as f:
    f.write(f0.to_bytes(4, 'little'))
    for m in rams: f.write(m)
print('f0', f0, 'frames', len(rams))
