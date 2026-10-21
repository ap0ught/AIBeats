"""Find inputs during the boss auto-scroll that give the UFO another X, save states at its creation, and run the
planned fight (ufo_fight4) + the exit search from them. Experiment only.

    python tools/s5b_ufox.py <boss state, e.g. s5/d0v3_boss>
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Farm, fire, log  # noqa: E402

state = sys.argv[1]
with Farm(3, name="s5b_ufox") as farm:
    g = farm.g0
    found = {}
    for v in range(12):
        g.load_file(state)
        k = 0
        while s5.ufo(g.r) is None and k < 300:
            w = {"Right"}
            if k % 7 < v % 7 or (v >= 7 and k % 11 == 3):
                fire(g.pad, w)
            g.step(w)
            k += 1
        n0 = len(g.rows)
        tok = g.snap()
        for _ in range(8):
            g.step(set())
        ux = s5.ufo(g.r)[4]
        g.restore(tok)
        if ux not in found:
            found[ux] = v
            g.save_file(f"tmp/ufox_{ux}")
            log(f"variant {v}: UFO X {ux}")
        if len(found) == 3:
            break
    for ux in sorted(found):
        g.load_file(f"tmp/ufox_{ux}")
        t0 = time.time()
        rows = s5.ufo_fight4(farm, g, tag=f"ufox{ux}")
        if rows is None:
            log(f"UFO X {ux}: ufo_fight4 failed")
            continue
        n = len(rows)
        best = s5.exit_search(farm, g, tag=f"ufox{ux}")
        log(f"UFO X {ux}: HP 0 after {n} rows from its creation ({n - 102} after hittable); exit {best}; {time.time() - t0:.0f} s")
