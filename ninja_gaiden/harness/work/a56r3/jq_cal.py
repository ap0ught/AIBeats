"""Round 3: Jaquio hit-band calibration. Replays the first rows of a jq3 result up to Ryu's first landing on a
pedestal top (y 160), then plays straight jumps (A 2 f, direction tap f for 2 f) back to back with the legal cancel
cycle at phase o, for several (f pattern, o); logs every swing frame (row Down+B): Ryu x/y, facing bit ($84),
Jaquio x, hit (boss_real drop on that frame or the next). Output JSON lines logs/a56r3_jq_cal.jsonl."""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C
from ng.inputs import read_inputs
src = sys.argv[1]
rows0 = list(read_inputs(P / src))
hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
CYC = [("Down",), ("Down", "B"), ("B",), (), ()]
e = C.open_emu("a56r3_jqcal.log")
out = open(P / "logs" / "a56r3_jq_cal.jsonl", "w")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    F = dict(e.fields); F.update(jx=0x467, jy=0x487); e.set_fields(F)
    s0 = e.load("tmp/a56r2_64b_control")
    en0 = C.Enforcer(hist)
    rr = [en0.emit(r, retry=0) for r in rows0]
    tr = C.play_trace(e, rr)
    k = next(i for i, t in enumerate(tr) if t["y"] == 160 and t["anim"] not in (5, 6, 11, 10) and i > 5)
    e.load("tmp/a56r2_64b_control")
    en0 = C.Enforcer(hist)
    pre = [en0.emit(r, retry=0) for r in rows0[:k + 1]]
    s = e.run(pre)
    print("landed", k + 1, "x", s["x"], "y", s["y"], flush=True)
    sid = e.msave()
    for pat in (("Left", "Right"), ("Right", "Left"), ("Left", "Left"), ("Right", "Right")):
        for gap in (0, 4, 9):
            for o in range(5):
                des = []
                j = 0
                while len(des) < 300:
                    f = pat[j % 2]
                    jump = [("A", f), ("A", f)] + [()] * 42 + [()] * gap
                    des += jump
                    j += 1
                des = [tuple(set(r) | set(CYC[(i - o) % 5])) if i >= o else r for i, r in enumerate(des)]
                e.mload(sid); en = en0.copy()
                rows = [en.emit(r, retry=0) for r in des]
                t2 = C.play_trace(e, rows)
                sw = []
                for i in range(1, len(t2) - 1):
                    if "B" in rows[i] and "B" not in rows[i - 1]:
                        hit = int(t2[i]["boss_real"] < t2[i - 1]["boss_real"] or t2[i + 1]["boss_real"] < t2[i]["boss_real"])
                        sw.append([t2[i]["frame"] - s0["frame"], t2[i]["x"], t2[i]["y"], t2[i]["rflags"], t2[i]["jx"], hit, t2[i]["hp"]])
                out.write(json.dumps({"pat": pat, "gap": gap, "o": o, "sw": sw}) + "\n"); out.flush()
finally:
    out.close(); e.close()
