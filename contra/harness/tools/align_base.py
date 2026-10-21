"""Base stages: which movie alignment clears the first room when the movie expects it?

    python tools/align_base.py <state> <movie.inputs.txt> <m_lo> <m_hi> [frames]

For each m: landing x, frame the room's cores are gone ($86 -> 0), first electrocution, first death, and the
movie's first Up press (its first step forward, which needs the fence to be down).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import Pool  # noqa: E402

state, movie, lo, hi = sys.argv[1], read_inputs(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
n = int(sys.argv[5]) if len(sys.argv) > 5 else 520
F = {"level": 0x30, "pstate": 0x90, "death": 0xB4, "screen": 0x64, "cleared": 0x37, "cores": 0x86, "elec": 0xC8,
     "x": 0x334, "y": 0x31A, "adv": 0xD0, "bossdef": 0x3B}


def job(emu, m):
    emu.load(state)
    emu.set_fields(F)
    emu.trace(True)
    rows = movie[m - 1:m - 1 + n]
    emu.run(rows)
    tr = emu.last_trace
    emu.trace(False)
    out = {"m": m}
    seen1 = False
    for i, s in enumerate(tr):
        if s["cores"]:
            seen1 = True
        if seen1 and s["cores"] == 0 and "cores_gone" not in out:
            out["cores_gone"] = i
        if s["elec"] and "elec" not in out:
            out["elec"] = i
        if (s["death"] & 1) and "death" not in out:
            out["death"] = i
        if s["adv"] and "adv" not in out:
            out["adv"] = i
        if s["y"] >= 160 and "land_x" not in out and i > 5:
            out["land_x"] = s["x"]
    out["first_up"] = next((i for i, r in enumerate(rows) if "Up" in r and i > 100), None)
    out["end"] = (tr[-1]["screen"], tr[-1]["cleared"], tr[-1]["x"])
    return out


ms = list(range(lo, hi + 1))
with Pool(min(4, len(ms)), name="alignbase") as pool:
    for o in pool.map(job, ms):
        print(o)
