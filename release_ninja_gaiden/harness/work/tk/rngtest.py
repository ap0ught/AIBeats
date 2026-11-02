"""DEBUG research (RAM poke, never a deliverable): does a boss's motion depend on $BF / arrival time?
    python work/tk/rngtest.py <state> <rows file|-> <n> <slot>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C
from ng.mode import TICKS
st, rf, n, slot = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows = C.rows_of(rf)[:n] if rf != '-' else [()] * n
e = C.open_emu('tk_rng.log')
out = {}
try:
    e.tick(TICKS)
    for d in (0, 37, 101):
        e.load(st)
        if d:
            e.poke(0xBF, (e.ram(0xBF, 1)[0] + d) & 255)
        _, rams = e.run_ram(rows)
        out[d] = [(r[0x460 + slot], r[0x480 + slot], r[0x66]) for r in rams]
finally:
    e.close()
for d in (37, 101):
    diff = next((i for i, (a, b) in enumerate(zip(out[0], out[d])) if a != b), None)
    print('delta', d, 'first diff row', diff, out[0][diff] if diff is not None else '', out[d][diff] if diff is not None else '')
