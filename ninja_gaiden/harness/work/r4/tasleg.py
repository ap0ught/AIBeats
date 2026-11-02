"""Round 4: legalized TAS rows (Enforcer, retry 0) from a state; report room changes and first divergence vs the TAS.
python work/r4/tasleg.py <state> <tas first frame (row index into tas4751 rows)> <n rows> [history file]"""
import sys
import csv
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa
st, f0, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
hist = list(read_inputs(P / sys.argv[4]))[-1800:] if len(sys.argv) > 4 else []
tas = list(read_inputs(P / "logs/tas4751.inputs.txt"))
trace = {int(r["frame"]): r for r in csv.DictReader(open(P / "logs/tas4751.trace.csv"))}
en = C.Enforcer(hist)
rows = [en.emit(r, retry=0) for r in tas[f0:f0 + n]]
e = C.open_emu("r4_tasleg.log")
try:
    s0 = e.load(st)
    tr = C.play_trace(e, rows)
    first = None
    pr = s0["room"]
    for i, t in enumerate(tr):
        fr = f0 + i + 1
        T = trace.get(fr)
        if T and first is None and (int(T["x"]) != t["x"] or int(T["y"]) != t["y"]):
            first = (fr, "ours", t["x"], t["y"], "tas", T["x"], T["y"])
        if t["room"] != pr:
            print("room", pr, "->", t["room"], "at frame", t["frame"])
            pr = t["room"]
    print("first divergence", first, "end", tr[-1]["frame"], tr[-1]["room"], tr[-1]["x"], tr[-1]["y"], "hp", tr[-1]["hp"])
finally:
    e.close()
