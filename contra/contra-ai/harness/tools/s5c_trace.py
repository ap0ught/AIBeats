"""Replay a stage 1 / 5 segment (or its start) from a state and print what is on screen for a range of rows.

    python tools/s5c_trace.py <stage 1|5> <state> <seg.json> <row lo> <row hi> [--every n] [--policy]

Per row: world X, Bill's X / Y, air, the row's buttons, the player's bullets, every live enemy as
slot:type:hp@x,y. With --policy the rows after <row lo> are played by the stage's run policy instead of the
segment (no repair), to see what the rule v2 policy does on its own.
"""
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
    use_policy = "--policy" in a
    if use_policy:
        a.remove("--policy")
    stage, state, seg, lo, hi = int(a[0]), a[1], a[2], int(a[3]), int(a[4])
    if stage == 1:
        from contra.stages import s1 as mod
    else:
        from contra.stages import s5 as mod
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text(encoding="utf-8"))["rows"]]
    g = Game(name=f"s{stage}c_trace")
    try:
        g.load_file(state, pad=Pad())
        route = Route(mod.JUMPS)
        for i in range(min(hi, len(rows))):
            if use_policy and i >= lo:
                row = g.pad.legal(mod.policy(g, route))
                r = g.step_raw(row)
            else:
                row = rows[i]
                r = g.step_raw(row)
            if i >= lo and (i - lo) % every == 0:
                en = " ".join(f"{e[0]}:{e[1]:02x}:{e[3]}@{e[4]},{e[5]}" for e in r.enemies())
                print(f"{i:5d} X{r.prog:5d} x{r.x:3d} y{r.y:3d} {'air' if r.air else '   '} w${r.weapon:02x} "
                      f"{'+'.join(row):16s} b{r.nbullets():2d} | {en}{'  DEAD' if r.dead else ''}{'  LAG' if r.lagged else ''}")
            if r.dead and i >= lo:
                break
    finally:
        g.close()


if __name__ == "__main__":
    main()
