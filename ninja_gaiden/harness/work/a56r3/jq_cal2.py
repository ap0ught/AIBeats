"""Round 3: Jaquio calibration with Jaquio on Ryu's LEFT. From the left-pedestal landing (row 27 of the q3 partial),
hop right to the middle pedestal (search w, k), then straight jumps facing LEFT (2-frame Left tap) with the cancel
cycle at phase o; logs swings (t, x, y, rflags, Jaquio x, hit) -> logs/a56r3_jq_cal2.jsonl"""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C
from ng.inputs import read_inputs
rows0 = list(read_inputs(P / "states/tmp/a56r3_jaq_q3_partial.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
CYC = [("Down",), ("Down", "B"), ("B",), (), ()]
e = C.open_emu("a56r3_jqcal2.log")
out = open(P / "logs" / "a56r3_jq_cal2.jsonl", "w")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    F = dict(e.fields); F.update(jx=0x467, jy=0x487); e.set_fields(F)
    s0 = e.load("tmp/a56r2_64b_control")
    en0 = C.Enforcer(hist)
    pre = [en0.emit(r, retry=0) for r in rows0[:27]]
    e.run(pre)
    sid0 = e.msave()
    plates = []
    for w in (0, 6, 12, 20, 30, 40, 50):
        for k in range(12, 44, 3):
            des = [()] * w + [("A", "Right"), ("A", "Right")] + [("Right",)] * (k - 2) + [()] * 50
            e.mload(sid0); en = en0.copy()
            rr = [en.emit(r, retry=0) for r in des]
            tr = C.play_trace(e, rr)
            land = next((i for i, t in enumerate(tr) if i > w + 8 and t["y"] == 160 and t["anim"] not in (5, 6, 10, 11)), None)
            if land is not None and tr[land]["x"] >= 85:
                plates.append((tr[land]["frame"] - s0["frame"], tr[land]["x"], w, k, rr[:land + 1]))
    plates.sort(key=lambda p: p[0])
    print("plates", [(p[0], p[1], p[2], p[3]) for p in plates[:12]], flush=True)
    for t0, x, w, k, rr0 in plates[:4]:
        e.mload(sid0); en1 = en0.copy()
        rr = [en1.emit(r, retry=0) for r in rr0]
        e.run(rr)
        sid = e.msave()
        for face in ("Left", "Right"):
            for gap in (0, 5):
                for o in range(5):
                    des = []
                    while len(des) < 260:
                        des += [("A", face), ("A", face)] + [()] * 42 + [()] * gap
                    des = [tuple(set(r) | set(CYC[(i - o) % 5])) if i >= o else r for i, r in enumerate(des)]
                    e.mload(sid); en = en1.copy()
                    rows = [en.emit(r, retry=0) for r in des]
                    t2 = C.play_trace(e, rows)
                    sw = []
                    for i in range(1, len(t2) - 1):
                        if "B" in rows[i] and "B" not in rows[i - 1]:
                            hit = int(t2[i]["boss_real"] < t2[i - 1]["boss_real"] or t2[i + 1]["boss_real"] < t2[i]["boss_real"])
                            sw.append([t2[i]["frame"] - s0["frame"], t2[i]["x"], t2[i]["y"], t2[i]["rflags"], t2[i]["jx"], hit, t2[i]["hp"]])
                    out.write(json.dumps({"plate": [t0, x, w, k], "face": face, "gap": gap, "o": o, "sw": sw}) + "\n"); out.flush()
finally:
    out.close(); e.close()
