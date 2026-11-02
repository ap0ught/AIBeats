"""Round 3: 6-2 room 37 pillar probe. Replays round-1 rows (states/tmp/a56_best_6-2_snap) from tmp/a56_6-1_c8_next
to row N, logs the position trace, then sweeps legal single-wall climb cycles (wall on Ryu's left = the pillar's
RIGHT face: [Right+A x2, Left x m, - x n]; and the mirror) followed by an exit move (hold Left / Left+A), and reports
the best by (room change, min y, min abs x).
    python work/a56r3/pillar62.py N
"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1150
rows0 = list(read_inputs(P / "states/tmp/a56_best_6-2_snap.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_pillar.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    s0 = e.load("tmp/a56_6-1_c8_next")
    en0 = C.Enforcer(hist)
    pre = [en0.emit(r, retry=0) for r in rows0[:N]]
    tr = C.play_trace(e, pre)
    for i, t in enumerate(tr):
        if i >= N - 200 and i % 4 == 0:
            print("pre", i + 1, t["frame"], "room", t["room"], "ax", C.abs_x(t), "y", t["y"], "anim", t["anim"],
                  "hp", t["hp"], "+".join(pre[i]))
    sid = e.msave()
    res = []
    for side, away, back in (("Lwall", "Right", "Left"), ("Rwall", "Left", "Right")):
        for m in range(2, 9):
            for n in range(0, 4):
                for pre_w in (0, 3, 6):
                    for ex in (0, 1, 2):
                        cyc = [(away, "A"), (away, "A")] + [(back,)] * m + [()] * n
                        des = [(back,)] * pre_w + cyc * 20
                        des = des[:160]
                        if ex == 1:
                            des += [("Left",)] * 60
                        elif ex == 2:
                            des += [("Left", "A")] * 2 + [("Left",)] * 58
                        e.mload(sid)
                        en = en0.copy()
                        rr = [en.emit(r, retry=0) for r in des]
                        t2 = C.play_trace(e, rr)
                        miny = min(t["y"] for t in t2)
                        minx = min(C.abs_x(t) for t in t2 if t["room"] == 37) if any(t["room"] == 37 for t in t2) else 0
                        rc = next((i for i, t in enumerate(t2) if t["room"] != 37), None)
                        dead = any(t["hp"] == 0 for t in t2)
                        fy = next((i for i, t in enumerate(t2) if t["y"] <= 40), None)
                        res.append((rc is None, rc or 0, miny, minx, side, m, n, pre_w, ex, fy, dead, t2[-1]["hp"]))
    res.sort()
    for r in res[:40]:
        print("RES", r)
finally:
    e.close()
