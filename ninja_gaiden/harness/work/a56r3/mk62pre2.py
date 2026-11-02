"""Round 3: 6-2 room 37 entry search: from round-1 rows[:N0] (Ryu clinging at the entry, screen x 91, y 231),
wait w, Left+A x2, Left x m, then Right until the camera engages ($4C bit 0); keeps the fastest; writes
states/tmp/a56r3_62_pre.inputs.txt.   python work/a56r3/mk62pre2.py N0"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa
N0 = int(sys.argv[1])
rows0 = list(read_inputs(P / "states/tmp/a56_best_6-2_snap.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_mk62pre2.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.load("tmp/a56_6-1_c8_next")
    en0 = C.Enforcer(hist)
    pre = [en0.emit(r, retry=0) for r in rows0[:N0]]
    s = e.run(pre)
    print("at N0", s["frame"], "ax", C.abs_x(s), "x", s["x"], "y", s["y"], "anim", s["anim"], flush=True)
    sid = e.msave()
    best = None
    for w in range(0, 8):
        for d in ("Left", "Right"):
            for m in range(0, 30, 2):
                des = [()] * w + [(d, "A")] * 2 + [(d,)] * m + [("Right",)] * 110
                e.mload(sid)
                en = en0.copy()
                rr = [en.emit(r, retry=0) for r in des]
                tr = C.play_trace(e, rr)
                k = next((i for i, t in enumerate(tr) if t["scroll_flags"] & 1), None)
                if k is not None and (best is None or k < best[0]):
                    best = (k, w, d, m, rr[:k + 1])
                    print("best", k, w, d, m, "ax", C.abs_x(tr[k]), "y", tr[k]["y"], flush=True)
    if best:
        C.save_rows(P / "states" / "tmp" / "a56r3_62_pre.inputs.txt", pre + best[4],
                    f"6-2 prefix: round-1 rows to {N0} + entry {best[1:4]} until camera engaged; from tmp/a56_6-1_c8_next")
        print("rows", len(pre) + len(best[4]))
finally:
    e.close()
