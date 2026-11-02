"""ng.solve.boss - whole-jump boss planner (agent a56's work/a56r2/jplan.py, reused unchanged) for ANY boss state.

    python -m ng.solve.boss <stage> <start state> --history <power-on rows to the start> [--width 4] [--hours 1]
        [--modes slash,throw,throwslash] [--tag t] [--prefix <rows> --prefix-frames N] [--finish]

A step = optional pre-move (walk/wait w frames), a jump (A 2 frames) with an air-direction pattern, and either the
legal slash-cancel cycle `Down | Down+B | B | - | -` (a new sword hit every 5 frames) from offset o, or a sub-weapon
throw (Up+B, no direction: the throw needs Left/Right released) - every row through the a56 Enforcer. Beam over steps,
score = frames + 6 * target HP; Pareto front on (target HP, frame). The step ends on landing / cling / kill.
Boss facts in knowledge/legal_a56_notes.md ("Boss facts"), legal_a34_notes.md ("3-3 Basaquer": path fixed, one Fire
Wheel at a time, jump slashes needed) and legal_a12_notes.md (Barbarian / Bomberhead with Jump & Slash).
Output: states/tmp/a56r2_tk_<stage>_<tag>.inputs.txt (rows from the start state to the kill frame);
--finish then plays to the next control and records the stage (ng.solve.verify.finish).
Jaquio has its own geometric planner (work/a56r3/jq3.py); call it directly.
"""
from __future__ import annotations

import sys

from . import common as C

sys.path.insert(0, str(C.PROJECT / "work" / "a56r2"))
import jplan as JP  # noqa: E402


def plan(stage, start, history, width=4, hours=1.0, modes=("slash",), tag="t", prefix=None, poke=None, **kw):
    nm = C.NAMES[C.stage_index(stage)]
    cfg = f"tk_{nm}"
    JP.CFGS[cfg] = {"start": start, "hist": str(history) if history else None, "pre_hist_blank": 0, "hpw": 6}
    if poke:   # DEBUG research only (RAM poke at the start state): never a deliverable
        JP.CFGS[cfg]["poke"] = poke
    best = JP.run(cfg, width=width, tag=tag, hours=hours, prefix=prefix, modes=modes, **kw)
    return best, C.STATES / "tmp" / f"a56r2_{cfg}_{tag}.inputs.txt"


def main(a):
    def opt(n, d):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return type(d)(v) if d is not None else v
        return d
    hist = opt("--history", None)
    width = opt("--width", 4)
    hours = opt("--hours", 1.0)
    modes = tuple(opt("--modes", "slash").split(","))
    tag = opt("--tag", "t")
    pre = opt("--prefix", None)
    pre_n = opt("--prefix-frames", 0)
    pk = opt("--poke", None)   # DEBUG research: "0x64=0,0xC9=0x85"
    poke = {int(k, 0): int(v, 0) for k, v in (x.split("=") for x in pk.split(","))} if pk else None
    fin = "--finish" in a
    if fin:
        a.remove("--finish")
    stage, start = a[0], a[1]
    prefix = C.rows_of(pre)[:pre_n] if pre else None
    best, path = plan(stage, start, hist, width, hours, modes, tag, prefix, poke=poke)
    print("BEST", None if best is None else best.frame, path, flush=True)
    if fin and best is not None:
        from . import verify as V
        rows = C.rows_of(path)
        print("RESULT", V.finish(stage, start, hist, rows, f"tk_{C.NAMES[C.stage_index(stage)]}_{tag}",
                                 note=f"boss planner modes={modes}", tool="ng.solve.boss"), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
