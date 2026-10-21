"""Play a planned climb for real (no pokes): delays / firing modes per node until every landing matches the model.

    python tools/s3_climb.py <pools.pkl> <q,xa,xb> [idx=0] [--state dbg/s3_pre] [--save name] [--modes 0,1,2,...]
"""
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.setrecursionlimit(100000)
from contra.stages.s3s8_lib import Game  # noqa: E402
from contra.stages.s3_exec import climb, A_of, MODES  # noqa: E402

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


state = opt("--state", "dbg/s3_pre")
save = opt("--save", "")
modes = [int(x) for x in opt("--modes", "0,1,2,3,4,5,6").split(",")]
pools = pickle.load(open(args[0], "rb"))
key = tuple(int(x) for x in args[1].split(","))
idx = int(args[2]) if len(args) > 2 else 0
path = pools[key][idx].path()
t0 = time.time()
with Game(log_name="s3_climb.log") as g:
    r = g.load(state)
    start = path[0]
    while True:
        want = ()
        if r.pstate == 1 and r.x and r.x < start.X:
            want = ("Right",)
        elif r.pstate == 1 and r.x > start.X:
            want = ("Left",)
        r = g.step(want)
        if r.pstate == 1 and not r.airborne:
            break
    t_land = len(g.rows)
    last, used = climb(g, path, modes=modes)
    r = g.r
    print(f"reached node {last} of {len(path) - 1}: {r.desc()} A={A_of(r)}; rows {len(g.rows)} (from landing "
          f"{len(g.rows) - t_land}, plan {path[last].t}), lag {g.lag}, ignored-pad {g.ignored}, {time.time() - t0:.0f}s")
    print("options used (delay, mode):", used)
    print("enemies:", r.edesc())
    if save:
        g.e.save(save)
        import json
        from contra.stages.s3s8_lib import LOGS_DIR
        (LOGS_DIR / (save.replace("/", "_") + ".rows.json")).write_text(json.dumps(["+".join(x) for x in g.rows]))
        print("saved", save)
