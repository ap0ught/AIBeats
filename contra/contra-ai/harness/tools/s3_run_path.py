"""Play a planned climb (a node of a pools pickle) in the emulator and report where it leaves the model.

    python tools/s3_run_path.py <pools.pkl> <q,xa,xb> [idx=0] [--state dbg/s3_pre] [--inv] [--mode k] [--save name]
                                [--shots prefix]

--inv   DEBUG: pokes the new-life invincibility timer every frame (for checking the model/plan only)
--mode  firing mode index into s3_exec.MODES for every node (default 0 = no firing)
"""
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.setrecursionlimit(100000)
from contra.stages.s3s8_lib import Game  # noqa: E402
from contra.stages.s3_exec import play_node, A_of, MODES  # noqa: E402

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


inv = "--inv" in args
if inv:
    args.remove("--inv")
state = opt("--state", "dbg/s3_pre")
mode = MODES[opt("--mode", 0)]
save = opt("--save", "")
shots = opt("--shots", "")
pools = pickle.load(open(args[0], "rb"))
key = tuple(int(x) for x in args[1].split(","))
idx = int(args[2]) if len(args) > 2 else 0
node = pools[key][idx]
path = node.path()
print("target", node, "nodes", len(path))
with Game(log_name="s3_run_path.log") as g:
    r = g.load(state)
    start = path[0]
    # drop-in: drift to the start X during the fall
    n = 0
    while True:
        want = ()
        if r.pstate == 1 and r.x and r.x < start.X:
            want = ("Right",)
        elif r.pstate == 1 and r.x > start.X:
            want = ("Left",)
        if inv:
            g.e.poke(0xAE, 100)
        r = g.step(want)
        n += 1
        if r.pstate == 1 and not r.airborne:
            break
    print(f"landed after {n} rows: {r.desc()} A={A_of(r)} (plan start X={start.X} Y={start.Y} sub={start.sub:02x})")
    t_land = len(g.rows)
    for k, nd in enumerate(path[1:], 1):
        before = len(g.rows)
        st, r = play_node(g, nd, mode, weapon=0x13, poke_inv=inv)
        used = len(g.rows) - before
        plan = nd.t - nd.parent.t
        flag = "" if (st == "ok" and used == plan) else f"  <-- {st}, rows {used} vs plan {plan}"
        print(f"{k:3d} t={nd.t:5d} rows={len(g.rows) - t_land:5d} q={nd.q:4d} walk={nd.walk:4d} "
              f"X={r.x:3d} Y={r.y:3d} sub={r.sub:02x} A={A_of(r):4d} lag={g.lag} ign={g.ignored}{flag}")
        if shots:
            g.e.screenshot(f"{shots}_{k:03d}")
        if st != "ok":
            print("   model:", nd, " emu:", r.desc(), r.edesc())
            break
    print(f"total rows {len(g.rows)} (from landing {len(g.rows) - t_land}), lag {g.lag}, ignored-pad {g.ignored}")
    if save:
        g.e.save(save)
        print("saved", save)
