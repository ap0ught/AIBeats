"""Replay rows from a state; print rows where Ryu stands (rflags bit2 clear) in a box.
    python work/tk/scan.py <state> <rows> room xlo xhi ylo yhi"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
st, rf = sys.argv[1], sys.argv[2]; room, xlo, xhi, ylo, yhi = map(int, sys.argv[3:8])
e = C.open_emu('tk_scan.log')
try:
    e.tick(TICKS); e.load(st); tr = A.play_trace(e, C.rows_of(rf))
finally:
    e.close()
for i, s in enumerate(tr):
    X = C.abs_x(s)
    if s['room'] == room and xlo <= X <= xhi and ylo <= s['y'] <= yhi and not (s['rflags'] & 4):
        print('row', i + 1, 'frame', s['frame'], 'X', X, 'y', s['y'], 'hp', s['hp'], 'coll', hex(s['coll']))
