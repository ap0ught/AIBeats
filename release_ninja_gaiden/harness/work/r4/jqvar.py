"""Round 4: emulator check of plan variants (first floor jump / first pedestal jump changed, rest of the plan kept).
python work/r4/jqvar.py <plan json> -> prints kill row ($66 == 0) per variant"""
import json
import sys
import itertools
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
import jqrows  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa
plan = json.loads(Path(sys.argv[1]).read_text())
steps0 = plan["steps"]
hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
e = C.open_emu("r4_jqvar.log")
best = None
try:
    e.load("tmp/a56r2_64b_control")
    sid = e.msave()
    for Tf, k, T1, holdend in itertools.product((1, 2), range(14, 20), range(23, 29), (43, 41, 39)):
        st = [list(s) for s in steps0]
        st[0] = ["floorjump", Tf, 32, 1, k]
        land = 32 + 1.5 * k
        X1 = land + 1.5 * max(0, T1 - (Tf + 19))
        if X1 > 67:
            continue
        st[1] = ["jump", T1, X1, 1, ["F", 1, holdend], 2, 0]
        try:
            want, sw = jqrows.plan_rows(st, end_extra=20)
        except Exception as ex:
            continue
        want = [set(r) for r in want]
        # extra swing at the end (the kill may need it)
        en = C.Enforcer(hist)
        rr = [en.emit(tuple(r), retry=0) for r in want]
        e.mload(sid)
        tr = C.play_trace(e, rr)
        kill = next((i + 1 for i, t in enumerate(tr) if t["bosshp"] == 0), None)
        hits = 16 - min(t["bosshp"] for t in tr)
        print(Tf, k, T1, holdend, "hits", hits, "kill", kill, flush=True)
        if kill and (best is None or kill < best[0]):
            best = (kill, Tf, k, T1, holdend)
            write_inputs(P / "states/tmp/r4_jqvar_best.inputs.txt", rr[:kill], f"jqvar {best}")
finally:
    e.close()
print("BEST", best)
