"""Print x/y of the player for the first frames of a movie segment at several alignments.

    python tools/align_probe.py <state> <movie.inputs.txt> <m_lo> <m_hi> [frames]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import Pool, play  # noqa: E402

state, movie, lo, hi = sys.argv[1], read_inputs(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
n = int(sys.argv[5]) if len(sys.argv) > 5 else 70
ms = list(range(lo, hi + 1))
with Pool(min(4, len(ms)), name="align") as pool:
    res = pool.map(lambda emu, m: play(emu, state, movie[m - 1:m - 1 + n], keep_trace=True), ms)
for m, r in zip(ms, res):
    print(f"m={m}")
    print("   " + " ".join(f"{s['frame']}:{s['x']},{s['y']},{s['screen']*256+s['scroll']}" + ("*" if movie[m - 1 + i] else "")
                           for i, s in enumerate(r.trace)))
