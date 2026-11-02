"""Round 3: 6-2 room 37 camera fix. Room 37 scrolls left only after Ryu has reached screen x ~127 once
(scroll_flags $4C bit 0: TAS and record both walk RIGHT first; round 1 went left at once, the camera stayed at
768 and the screen's left edge stopped Ryu at abs x 783 = the "wall"). Builds the prefix: round-1 rows to N0, then
Right until $4C bit 0 is set (+ extra Right frames E), writes states/tmp/a56r3_62_pre<N0>.inputs.txt and reports.
    python work/a56r3/mk62pre.py N0 [E]
"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa

N0 = int(sys.argv[1])
E = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rows0 = list(read_inputs(P / "states/tmp/a56_best_6-2_snap.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_mk62pre.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.load("tmp/a56_6-1_c8_next")
    en = C.Enforcer(hist)
    rows = [en.emit(r, retry=0) for r in rows0[:N0]]
    e.run(rows)
    k = 0
    while k < 120:
        r = en.emit(("Right",), retry=0)
        rows.append(r)
        s = e.run([r])
        k += 1
        if s["scroll_flags"] & 1:
            break
    for _ in range(E):
        r = en.emit(("Right",), retry=0)
        rows.append(r)
        s = e.run([r])
    print("N0", N0, "right frames", k, "+", E, "frame", s["frame"], "ax", C.abs_x(s), "x", s["x"], "y", s["y"],
          "flags", s["scroll_flags"], "scroll", s["scroll"], s["scroll_scr"])
    # check the camera follows when going left
    tr = C.play_trace(e, [("Left",)] * 40)
    print("left40", [(C.abs_x(t), t["x"], t["y"], t["scroll"], t["scroll_flags"]) for t in tr[::8]])
    C.save_rows(P / "states" / "tmp" / f"a56r3_62_pre{N0}.inputs.txt", rows,
                f"6-2 prefix: round-1 rows to {N0} + Right {k + E} (camera engaged), from tmp/a56_6-1_c8_next")
    print("rows", len(rows))
finally:
    e.close()
