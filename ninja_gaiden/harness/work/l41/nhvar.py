"""NesHawk: try several stage-rows files from one saved state (each must share the rows before the state's frame).
python work/l41/nhvar.py <state> <rows1> [<rows2> ...]  -> per file: stage-9 frame, hp/np/item at the end, eaten edges"""
import sys, time
sys.path.insert(0, 'work/l41')
from lib import *
from ng.mode import TICKS
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
def mask(r): return sum(BITS[b] for b in r)
stn = sys.argv[1]; files = sys.argv[2:]
e = C.open_emu('l41_nhv.log')
try:
    e.tick(TICKS)
    for fn in files:
        t = time.time()
        rows = C.rows_of(fn)
        st = e.load(stn); f0 = st['frame']
        _, rams = e.run_ram(rows[f0 - F0:])
        end = next((f0 + j + 1 for j, m in enumerate(rams) if m[0x6D] == 9), None)
        confs = [f0 + j + 1 for j, m in enumerate(rams) if m[0x2A] != mask(rows[f0 - F0 + j])
                 and rows[f0 - F0 + j] != rows[f0 - F0 + j - 1]]
        m = rams[-1]
        rm = max(m2[0x6E] for m2 in rams if m2[0x6D] == 8) if any(m2[0x6D] == 8 for m2 in rams) else None
        last8 = [m2 for m2 in rams if m2[0x6D] == 8][-1]
        print(fn, 'stage9', end, 'last room', rm, 'X', X(last8), 'y', last8[0x8A], 'hp', last8[0x65], 'np', last8[0x64], 'item', last8[0xC9], 'eaten', confs[:8], f'{time.time()-t:.0f}s', flush=True)
finally:
    e.close()
