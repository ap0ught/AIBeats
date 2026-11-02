"""6-2 room 37 entry (round 4): legalized TAS rows from tmp/a56_6-1_c8_next to frame F, then a spec; prints when the
leftward camera starts ($4C 128 -> 129) and Ryu's path. python work/r4/try62e.py <F> "<spec>" """
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa
from jq_play import parse  # noqa
F = int(sys.argv[1])
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1800:]
tas = list(read_inputs(P / "logs/tas4751.inputs.txt"))
en = C.Enforcer(hist)
rows = [en.emit(r, retry=0) for r in tas[31637:F]] + [en.emit(r, retry=0) for r in parse(sys.argv[2])]
e = C.open_emu("r4_try62e.log")
try:
    e.load("tmp/a56_6-1_c8_next")
    tr = C.play_trace(e, rows)
    cam = None
    for i, t in enumerate(tr):
        if t["frame"] > F - 3 and (i % 2 == 0):
            print(t["frame"], t["room"], t["x"], t["y"], t["anim"], t["scroll_flags"], t["scroll"], rows[i])
        if cam is None and t["room"] == 37 and t["scroll_flags"] == 129:
            cam = t["frame"]
    print("camera start", cam)
    if len(sys.argv) > 3:
        write_inputs(P / "logs" / "r4" / f"{sys.argv[3]}.inputs.txt", rows, f"6-2: legal TAS rows to {F} + {sys.argv[2]} from tmp/a56_6-1_c8_next")
finally:
    e.close()
