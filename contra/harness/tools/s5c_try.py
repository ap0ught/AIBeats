"""Play the stage 5 (or 1) run policy from a state with a few route edits and trace it (no repair).

    python tools/s5c_try.py <stage> <state> <seg.json> <row0> <rows> <edits as python, e.g. "[('fire',148,60,None)]"> [--every n]

The segment's rows are replayed up to row0 (history for the pad), then the policy plays `rows` rows.
"""
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game, Pad  # noqa: E402
from contra.stages.s1_engine import Route  # noqa: E402


def main():
    a = sys.argv[1:]
    every = 1
    if "--every" in a:
        i = a.index("--every")
        every = int(a[i + 1])
        del a[i:i + 2]
    stage, state, seg, row0, n, edits = int(a[0]), a[1], a[2], int(a[3]), int(a[4]), ast.literal_eval(a[5])
    if stage == 1:
        from contra.stages import s1 as mod
    else:
        from contra.stages import s5 as mod
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text(encoding="utf-8"))["rows"]]
    g = Game(name=f"s{stage}c_try")
    try:
        g.load_file(state, pad=Pad())
        g.run_raw(rows[:row0])
        route = Route(mod.JUMPS)
        for ed in edits:
            route.apply_edit(tuple(ed))
        for k in range(n):
            i = len(g.rows)
            w = mod.policy(g, route)
            r = g.step(w)
            row = g.rows[-1]
            if k % every == 0 or r.dead:
                en = " ".join(f"{e[0]}:{e[1]:02x}:{e[3]}@{e[4]},{e[5]}" for e in r.enemies())
                print(f"{i:5d} X{r.prog:5d} x{r.x:3d} y{r.y:3d} {'air' if r.air else '   '} {'+'.join(row):16s} b{r.nbullets():2d} | {en}"
                      f"{'  DEAD' if r.dead else ''}{'  LAG' if r.lagged else ''}")
            why = mod.fail_hard(g) if stage == 5 else mod.fail(g)
            if why:
                print("FAIL:", why)
                break
    finally:
        g.close()


if __name__ == "__main__":
    main()
