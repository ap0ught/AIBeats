"""ng.solve.astar - macro A* over stable states (agent a34's ng/stages/a34r2_astar.py, reused unchanged) for ANY stage,
with our own file locations.

    python -m ng.solve.astar <stage> <start state> <prefix rows file|-> <goal> <out> [--hist <power-on rows to start>]
        [--w 1.3] [--max-exp 600] [--only C8,J,R,..] [--fine] [--hmax] [--switch] [--throw] [--airrun] [--enemykey]

Goal: "pos:<room>:<wpos>:<y>:<tol>" (standing within tol) or "room:<room>[:<exit wpos>:<exit y>]".
Macros (a34r2_astar.macros()): C8/C8m single-wall climb `A+away x2, back x6` (1.54 px/f, the legal climb),
C9/C7 variants, JO* wall jump-offs, runs R/L n, jumps with held / switched direction, J*S jump + air slash, waits W*,
TH throws (--throw); all legalized against the node's own history (a34_core.Legal = check_inputs semantics).
f = t + w * h, h = |dx|/1.5 (+|climb|/2.4; --hmax: max of the two). --w > 1 = weighted (faster, not optimal).
Files: prefix / history may be any path (copied to logs/tk/astar/ for a34_core's loader); output rows
logs/tk/astar/<out>.inputs.txt (= prefix + found rows, from the start state), state states/tmp/a34r2_x/<out>.State.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from . import common as C

OUT = C.LOGS / "tk" / "astar"


def _stage_file(p, tag):
    """a34_core loads rows by NAME from its OUT_DIR; copy any file there under a tk_ name."""
    if p in ("-", "", None):
        return p
    src = Path(p)
    if not src.suffix:
        src = OUT / f"{p}.inputs.txt"
    if src.parent.resolve() == OUT.resolve():
        return src.name.replace(".inputs.txt", "")
    nm = f"tk_{tag}_{src.name.replace('.inputs.txt', '')}"
    shutil.copyfile(src, OUT / f"{nm}.inputs.txt")
    return nm


def main(a):
    flags = {"--fine": "A34_FINE", "--hmax": "A34_HMAX", "--switch": "A34_SWITCH", "--throw": "A34_THROW",
             "--airrun": "A34_AIRRUN", "--enemykey": "A34_ENEMYKEY"}
    for f, env in flags.items():
        if f in a:
            a.remove(f)
            os.environ[env] = "1"
    OUT.mkdir(parents=True, exist_ok=True)
    if "--hist" in a:
        i = a.index("--hist")
        a[i + 1] = _stage_file(a[i + 1], "h")
    a[2] = _stage_file(a[2], "p")
    import a34_core as K  # noqa: E402
    K.OUT_DIR = OUT
    K.BY_NAME = {n: i for i, n in enumerate(C.NAMES)}
    import a34r2_astar as AS  # noqa: E402  (reads the A34_* env flags at import)
    sys.argv = ["a34r2_astar.py"] + a
    AS.main()


if __name__ == "__main__":
    main(sys.argv[1:])
