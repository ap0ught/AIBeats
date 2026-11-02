"""Round 3: Jaquio hit-geometry probe. Plays many simple legal policies from the 6-4b control state (walk w frames
right, then straight-up jumps every J frames facing F, legal cancel cycle from phase o) and logs every frame:
Ryu x, y, facing ($84), anim, Jaquio x/y, boss_real; output JSON lines for an offline fit.
    python work/a56r3/jq_geom.py [start] > logs/a56r3_jq_geom.jsonl
"""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa

START = sys.argv[1] if len(sys.argv) > 1 else "tmp/a56r2_64b_control"
HIST = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
CYC = [("Down",), ("Down", "B"), ("B",), (), ()]


def policy(w, per, face, o, n=330):
    rows = []
    for i in range(n):
        r = set()
        if i < w:
            r.add("Right")
        else:
            k = i - w
            if k % per in (0, 1):
                r.add("A")
            if face and k % per in (2, 3):
                r.add(face)
            if k >= o:
                r |= set(CYC[(k - o) % 5])
        rows.append(tuple(r))
    return rows


e = C.open_emu("a56r3_geom.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    F = dict(e.fields)
    F.update(jx=0x467, jy=0x487, jid=0x407)
    e.set_fields(F)
    s0 = e.load(START)
    sid = e.msave()
    pols = []
    for w in (40, 50, 58, 66, 74, 82, 90):
        for per in (40, 47, 55):
            for face in (None, "Left", "Right"):
                pols.append((w, per, face, 2))
    for p in pols:
        e.mload(sid)
        en = C.Enforcer(HIST)
        rows = [en.emit(r, retry=0) for r in policy(*p)]
        tr = C.play_trace(e, rows)
        out = []
        for i, t in enumerate(tr):
            out.append([t["frame"] - s0["frame"], t["x"], t["y"], t["rflags"], t["anim"], t["jx"], t["jy"],
                        t["boss_real"], t["bosshp"], t["hp"], "+".join(rows[i])])
        print(json.dumps({"pol": p, "f0": s0["frame"], "tr": out}), flush=True)
finally:
    e.close()
