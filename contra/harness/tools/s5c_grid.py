"""Grid of route edits tried with the run policy (no repair) from one point of a solved segment, on 3 emulators.

    python tools/s5c_grid.py <stage> <state> <seg.json> <row0> <rows> <python expression giving a list of edit lists>

For each edit list: rows survived (or 'ok'), world X reached, B presses, and the rows on which enemy HP changed.
Example: "[[('fire',t,n,None)] for t in range(140,180,3) for n in (2,7)]"
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Farm, Pad  # noqa: E402
from contra.stages.s1_engine import Route  # noqa: E402


def main():
    a = sys.argv[1:]
    stage, state, seg, row0, n = int(a[0]), a[1], a[2], int(a[3]), int(a[4])
    grid = eval(a[5])                                            # noqa: S307 - my own command line
    if stage == 1:
        from contra.stages import s1 as mod
    else:
        from contra.stages import s5 as mod
    fail = mod.fail_hard if stage == 5 else mod.fail
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text(encoding="utf-8"))["rows"]]
    with Farm(3, name=f"s{stage}c_grid") as farm:
        g = farm.g0
        g.load_file(state, pad=Pad())
        g.run_raw(rows[:row0])
        st = g.save_file(f"tmp/s{stage}c_grid")
        pad = g.pad.copy()

        def ev(gg, edits):
            gg.load_file(st, pad)
            route = Route(mod.JUMPS)
            route.opts["row0"] = row0
            for ed in edits:
                ed = tuple(ed)
                if ed[0] in ("jump+", "jump-", "jumpmove", "opt"):
                    route.apply_edit(ed)
                else:
                    route.apply_edit((ed[0], ed[1] - row0, ed[2], ed[3]))
            t0 = gg.pad.t
            why = "ok"
            for k in range(n):
                gg.step(mod.policy(gg, route))
                w = fail(gg)
                if w:
                    why = f"{w}@{row0 + k + 1}"
                    break
            return why, gg.r.prog, sum(1 for x in gg.pad.starts["B"] if x >= t0)
        res = farm.map(ev, grid)
        for edits, (why, prog, nb) in zip(grid, res):
            print(f"{why:14s} X{prog:5d} B{nb:3d}  {edits}")


if __name__ == "__main__":
    main()
