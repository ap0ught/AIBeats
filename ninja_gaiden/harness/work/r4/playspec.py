"""play <base rows name> + spec from a state; print every k-th frame (wpos, y, anim, hp). python work/r4/playspec.py <state> <base> "<spec>" [k] [--save out]"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa
from jq_play import parse  # noqa
a = sys.argv[1:]
out = None
if "--save" in a:
    i = a.index("--save"); out = a[i + 1]; del a[i:i + 2]
st, basef, spec = a[0], a[1], a[2]
k = int(a[3]) if len(a) > 3 else 2
if basef != "-" and not (P / basef).exists():
    basef = f"logs/r4/{basef}.inputs.txt"
base = list(read_inputs(P / basef)) if basef != "-" else []
en = C.Enforcer(base)
rows = [en.emit(r, retry=0) for r in parse(spec)]
e = C.open_emu("r4_playspec.log")
try:
    e.load(st)
    e.run(base)
    tr = C.play_trace(e, rows)
    def wp(t):
        sc = t["scroll_scr"]; sc = sc - 256 if sc >= 128 else sc
        return sc * 256 + t["scroll"] + t["x"]
    for i, t in enumerate(tr):
        if i % k == 0 or i == len(tr) - 1:
            print(t["frame"], t["room"], wp(t), t["y"], t["anim"], t["hp"], rows[i])
    if out:
        write_inputs(P / "logs" / "r4" / f"{out}.inputs.txt", base + rows, f"{basef} + {spec}")
finally:
    e.close()
