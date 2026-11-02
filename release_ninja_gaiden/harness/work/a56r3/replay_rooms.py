"""print room / position changes while replaying a rows file from a state:  replay_rooms.py <state> <rows> [every]"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C
from ng.inputs import read_inputs
e = C.open_emu("a56r3_replay.log")
try:
    s0 = e.load(sys.argv[1])
    rows = list(read_inputs(P / sys.argv[2]))
    ev = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    tr = C.play_trace(e, rows)
    pr = None
    for i, t in enumerate(tr):
        if t["room"] != pr or i % ev == 0:
            print(i + 1, t["frame"], "room", t["room"], "ax", C.abs_x(t), "y", t["y"], "hp", t["hp"], "item", t["item"], "np", t["ninpo"])
            pr = t["room"]
finally:
    e.close()
