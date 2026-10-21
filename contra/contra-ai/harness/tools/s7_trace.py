"""Replay a stage 7 segment open-loop and dump a compact per-row trace (+ optional screenshots).

    python tools/s7_trace.py <state> <inputs name in logs/s7> [shot_every_cam_px]

Writes logs/s7/<name>.trace.json: one list per row [cam, x, y, fc, lagged, pause, barrier, nbullets, nenemies,
stop, auto, weapon]. Screenshots (if asked) go to shots/s7cmp/<name>_cam<cam>_row<row>.png, one each time the
camera has moved another shot_every px (and at the end of the scroll).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.inputs import read_inputs  # noqa: E402
from contra.stages.s6lib import Sim  # noqa: E402


def main():
    state, name = sys.argv[1], sys.argv[2]
    every = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = read_inputs(ROOT / "logs" / "s7" / f"{name}.inputs.txt")
    out = []
    with Sim(f"s7_trace_{name}") as sim:
        sim.load(state)
        nxt = 0
        i = 0
        while i < len(rows):
            n = 1 if every else 500
            tr = sim.run(rows[i:i + n])
            for f in tr:
                out.append([f.cam, f["x"], f["y"], f["fc"], f["lagged"], f["pause"], f["barrier"], f.nbullets(),
                            len(f.enemies()), f["stop"], f["auto"], f["weapon"], f["bossdef"], f["lroutine"]])
            if every:
                f = tr[-1]
                if f.cam >= nxt and f["lroutine"] == 4:
                    sim.e.screenshot(f"s7cmp/{name}_cam{f.cam:04d}_row{i:04d}")
                    nxt = (f.cam // every + 1) * every
            i += n
    p = ROOT / "logs" / "s7" / f"{name}.trace.json"
    p.write_text(json.dumps(out), encoding="utf-8")
    print("rows", len(out), "lag", sum(r[4] for r in out), "->", p)


if __name__ == "__main__":
    main()
