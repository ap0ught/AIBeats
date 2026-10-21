"""Play a stage's run policy without repair (optionally after replaying a segment) and print what is around the
player before the first failure.

    python tools/s5_watch.py <stage 1|5> <state> [--seg logs/x.seg.json] [--rows N] [--every K] [--last M] [--jumps a,b,c]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game, log  # noqa: E402
from contra.stages.s1_engine import Route  # noqa: E402

a = sys.argv[1:]


def opt(name, default):
    if name in a:
        i = a.index(name)
        v = a[i + 1]
        del a[i:i + 2]
        return type(default)(v) if default is not None else v
    return default


seg, nrows, every, last = opt("--seg", None), opt("--rows", 100000), opt("--every", 4), opt("--last", 90)
jumps = opt("--jumps", None)
stage, state = int(a[0]), a[1]
mod = __import__(f"contra.stages.s{stage}", fromlist=["x"])
g = Game(name=f"s{stage}_watch")
try:
    g.load_file(state)
    if seg:
        rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
        g.run_raw(rows[:nrows])
    route = Route(mod.JUMPS if jumps is None else [int(x) for x in jumps.split(",") if x])
    hist = []
    why = None
    while len(hist) < 20000:
        w = mod.policy(g, route)
        r = g.step(w)
        hist.append((len(g.rows), "+".join(g.rows[-1]), r))
        why = mod.fail(g)
        if why or r.lr not in (3, 4):
            break
    log("stopped:", why, g.r.summary())
    for (i, row, r) in hist[-last:]:
        if (len(hist) - i) % every and i != hist[-1][0]:
            continue
        en = [(f"{e[1]:02x}", e[4], e[5], e[3]) for e in r.enemies() if e[1] not in (0x13,)]
        print(f"row {i:5d} prog {r.prog:5d} x={r.x:3d} y={r.y:3d} air={1 if r.air else 0} in={row:16s} fc={r.fc:3d} en={en}")
finally:
    g.close()
