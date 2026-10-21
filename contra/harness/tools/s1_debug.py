"""Run stage 1's run phase with the policy's decisions logged; print the log around the first failure of a kind.

    python tools/s1_debug.py <start state> <failure prefix, e.g. weapon> [rows of log to print]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s1  # noqa: E402
from contra.stages.s1_common import Farm, log  # noqa: E402
from contra.stages.s1_engine import Repair, Route  # noqa: E402

start, kind = sys.argv[1], sys.argv[2]
nlog = int(sys.argv[3]) if len(sys.argv) > 3 else 160
farm = Farm(3, name="s1_dbg")
try:
    g = farm.g0
    g.load_file(start)
    s1.DEBUG["g"] = g
    hit = []

    def fail(gg):
        why = s1.fail(gg)
        if why and gg is g and why.startswith(kind) and not hit:
            hit.append(why)
            log("FAILURE", why, gg.r.summary())
            for row in s1.DEBUG["log"][-nlog:]:
                print(row)
        return why
    rep = Repair(farm, s1.policy, fail, tag="s1_dbg", plan=s1.plan, mark=s1.mark)
    rep.run(g, Route(s1.JUMPS), lambda gg: bool(hit) or gg.r.prog >= s1.BOSS_FROM, ring_len=50)
finally:
    farm.close()
