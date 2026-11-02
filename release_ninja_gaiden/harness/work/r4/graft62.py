"""6-2 round 4: legal TAS rows (from tmp/a56_6-1_c8_next) to frame F + donor rows[a:b] -> camera check, saves logs/r4/<out>"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa
F, donor, a, b, out = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1800:]
tas = list(read_inputs(P / "logs/tas4751.inputs.txt"))
D = list(read_inputs(P / donor))
en = C.Enforcer(hist)
rows = [en.emit(r, retry=0) for r in tas[31637:F]] + [en.emit(r, retry=0) for r in D[a:b]]
e = C.open_emu("r4_graft62.log")
try:
    e.load("tmp/a56_6-1_c8_next")
    tr = C.play_trace(e, rows)
    cam = None
    for i, t in enumerate(tr):
        if t["frame"] >= F and i % 3 == 0:
            print(t["frame"], t["room"], t["x"], t["y"], t["anim"], t["scroll_flags"], t["scroll"], t["hp"])
        if cam is None and t["room"] == 37 and t["scroll_flags"] & 1 and t["frame"] > F:
            cam = t["frame"]
    print("camera", cam, "end", tr[-1]["frame"], tr[-1]["x"], tr[-1]["y"], "hp", tr[-1]["hp"])
    write_inputs(P / "logs" / "r4" / f"{out}.inputs.txt", rows, f"6-2: legal TAS rows to {F} + {donor}[{a}:{b}] from tmp/a56_6-1_c8_next")
finally:
    e.close()
