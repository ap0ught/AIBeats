"""Re-fit one stage of a foreign TAS to this emulator (see contra/resync.py: repair_stage).

    python tools/repair.py <stage state> <movie.inputs.txt> <m> <out name> [--W 240] [--H 900] [--K 12] [--seed 1]
                           [--cap 7500] [--par 4] [--resume] [--kinds B+,B+,P,P]

<stage state>: savestate one frame before the stage's first playable frame (level routine 4).
<m>: the movie's (1-based) frame that is applied on that first frame.
Writes logs/<out>.seg.json (the edits, in order, and the final per-frame rows really sent).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import Pool, repair_stage  # noqa: E402


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        if isinstance(default, bool):
            del args[i]
            return True
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    W, H, K = opt(args, "--W", 240), opt(args, "--H", 900), opt(args, "--K", 12)
    seed, cap, par = opt(args, "--seed", 1), opt(args, "--cap", 7500), opt(args, "--par", 4)
    resume = opt(args, "--resume", False)
    kinds = opt(args, "--kinds", "B+,B+,B+,P,P,P").split(",")
    state, movie_path, m, out = args[0], args[1], int(args[2]), args[3]
    movie = read_inputs(movie_path)
    prior = None
    segp = LOGS_DIR / f"{out}.seg.json"
    if resume and segp.exists():
        prior = json.loads(segp.read_text(encoding="utf-8")).get("edits")
    with Pool(par, name=f"repair_{out.replace('/', '_')}") as pool:
        done, rows, edits = repair_stage(pool, state, movie[m - 1:m - 1 + cap], out, W=W, H=H, K=K, seed=seed,
                                         edits=prior, kinds0=tuple(kinds),
                                         meta={"m": m, "movie": str(movie_path)}, log=log)
    log("finished" if done else "NOT finished", len(rows), "rows", len(edits), "edits")
