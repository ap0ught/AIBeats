"""Round 3: 6-2 room 37 entry wall (Ryu clings at screen x 91, y 231, wall on his RIGHT): sweep legal climb cycles
[Left+A x h, Right x m, none x n] (+ final Right) and report min y / max x / camera flag ($4C bit 0)."""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C
from ng.inputs import read_inputs
rows0 = list(read_inputs(P / "states/tmp/a56_best_6-2_snap.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_sweep62.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.load("tmp/a56_6-1_c8_next")
    en0 = C.Enforcer(hist)
    e.run([en0.emit(r, retry=0) for r in rows0[:1085]])
    sid = e.msave()
    res = []
    for h in (2, 3, 4, 6, 8):
        for m in range(0, 11):
            for n in range(0, 4):
                for back in ("Right", None):
                    cyc = [("Left", "A")] * h + [(back,) if back else ()] * m + [()] * n
                    if len(cyc) < 5:
                        continue
                    des = (cyc * 30)[:140] + [("Right",)] * 40
                    e.mload(sid); en = en0.copy()
                    tr = C.play_trace(e, [en.emit(r, retry=0) for r in des])
                    k = next((i for i, t in enumerate(tr) if t["scroll_flags"] & 1), None)
                    res.append((k if k is not None else 999, min(t["y"] for t in tr), max(t["x"] for t in tr), h, m, n, back,
                                tr[-1]["y"], tr[-1]["hp"]))
    res.sort(key=lambda r: (r[0], r[1]))
    for r in res[:25]:
        print("RES", r, flush=True)
finally:
    e.close()
