"""Frame-counter phase scan. Many hazards (flame jets, crushing walls, 'frame rules') are keyed to the game's
frame counter ($1A). A movie made on another ROM/emulator reaches a stage with a different counter value, so its
timing against those hazards is off. A pause shifts the counter by its length without changing anything else.

    python tools/phase_scan.py <state> <movie.inputs.txt> <m> [kmax=64] [frames=2600] [--write logs/x.seg.json]

Plays the movie from the stage state with a pause of k frames (k = 0, 2..kmax) inserted at row 20 and reports how
far each gets. With --write, stores the best k as the first edit of a seg.json for `tools/repair.py --resume`.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import Pool, apply_edit, play  # noqa: E402

args = sys.argv[1:]
write = None
if "--write" in args:
    i = args.index("--write"); write = args[i + 1]; del args[i:i + 2]
state, movie, m = args[0], read_inputs(args[1]), int(args[2])
kmax = int(args[3]) if len(args) > 3 else 64
n = int(args[4]) if len(args) > 4 else 2600
base = [tuple(r) for r in movie[m - 1:m - 1 + n]]
ks = [0] + list(range(2, kmax + 1))


def job(emu, k):
    rows = apply_edit(base, ("P", 20, k)) if k else base
    return play(emu, state, rows, stall=900)


with Pool(4, name="phase") as pool:
    res = pool.map(job, ks)
best = max(zip(ks, res), key=lambda t: (t[1].reason in ("level", "end"), t[1].progress, t[1].frames - t[0]))
for k, r in sorted(zip(ks, res), key=lambda t: (-t[1].progress, t[0]))[:16]:
    print(f"pause {k:3d}: {r}")
print("best:", best[0], best[1])
if write:
    p = Path(write)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"m": m, "done": False, "frames": 0, "rows": [],
                             "edits": [["P", 20, best[0]]] if best[0] else []}), encoding="utf-8")
    print("wrote", p)
