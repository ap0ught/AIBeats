"""Run the ledge search of contra/stages/s3_plan.py between two rows and save the pools.

    python tools/s3_search.py <out.pkl> <q_end> [--start X,Y,sub,A[,t]]... [--from pools.pkl:q] [--keep 30]
                              [--procs 6] [--slack 30]

Default start = the drop-in: standing on row 12 at Y 180, $94 = $1d, A 0, any X 26..86 (drifting during the fall).
"""
import pickle
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3_plan import Planner, Node, search, _winit  # noqa: E402


def main():
    args = sys.argv[1:]

    def opt(name, default, many=False):
        vals = []
        while name in args:
            i = args.index(name)
            vals.append(args[i + 1])
            del args[i:i + 2]
        if many:
            return vals
        return type(default)(vals[-1]) if vals else default
    keep = opt("--keep", 30)
    procs = opt("--procs", 6)
    slack = opt("--slack", 30)
    starts_s = opt("--start", "", many=True)
    out, q_end = args[0], int(args[1])
    starts = []
    for s in starts_s:
        v = [int(x, 0) for x in s.split(",")]
        starts.append(Node(v[4] if len(v) > 4 else 0, v[0], v[1], v[2], v[3]))
    if not starts:
        starts = [Node(0, x, 180, 0x1D, 0) for x in range(26, 88, 2)]
    pl = Planner()
    t0 = time.time()
    with Pool(procs, initializer=_winit) as pool:
        pools = search(pl, starts, q_end, keep=keep, slack=slack, pool=pool,
                       log=lambda m: print(f"{time.time() - t0:6.1f}s {m}", flush=True))
    sys.setrecursionlimit(100000)
    with open(out, "wb") as f:
        pickle.dump(pools, f)
    for key in sorted(pools):
        if key[0] <= q_end + 6:
            print(key, len(pools[key]), pools[key][0])


if __name__ == "__main__":
    main()
