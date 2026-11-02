"""play a row spec from the 6-4b control state (tmp/a56r2_64b_control) through the Enforcer and print the trace.
spec: comma list of <buttons>*<n> (buttons joined by +, '-' = none). Example: "A*2,-*30,Right*20"
python work/r4/jq_play.py "<spec>" [every]"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa


def parse(spec):
    rows = []
    for part in spec.split(","):
        b, _, n = part.partition("*")
        r = () if b in ("-", "") else tuple(b.split("+"))
        rows += [r] * int(n or 1)
    return rows


if __name__ == "__main__":
    rows = parse(sys.argv[1])
    ev = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
    e = C.open_emu("r4_jqplay.log")
    try:
        from ng.mode import TICKS
        e.tick(TICKS)
        F = dict(e.fields)
        F.update(jx=0x467, jy=0x487, a83=0x83, yrad=0x90)
        e.set_fields(F)
        s0 = e.load("tmp/a56r2_64b_control")
        en = C.Enforcer(hist)
        rr = [en.emit(r, retry=0) for r in rows]
        tr = C.play_trace(e, rr)
        for i, t in enumerate(tr):
            if i % ev == 0 or t["boss_real"] != (tr[i - 1]["boss_real"] if i else 16):
                print(i + 1, "R", t["x"], t["xsub"], t["y"], "a83", t["a83"], "anim", t["anim"], "f84", hex(t["rflags"]), "coll", hex(t["coll"]),
                      "J", t["jx"], "bhp", t["boss_real"], "hp", t["hp"], rr[i])
    finally:
        e.close()
