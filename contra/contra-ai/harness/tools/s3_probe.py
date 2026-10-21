"""Probe: load a state, hold buttons, print one line per frame (or every k frames) with the player and enemies.

    python tools/s3_probe.py <state> <buttons|-> <frames> [every] [--shots prefix]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots"); shots = args[i + 1]; del args[i:i + 2]
state, btn, n = args[0], args[1], int(args[2])
every = int(args[3]) if len(args) > 3 else 1
btn = () if btn == "-" else tuple(btn.split("+"))
with Game(log_name="s3_probe.log") as g:
    r = g.load(state)
    print(r.desc(), r.edesc())
    t0 = time.time()
    for i in range(n):
        r = g.step(btn)
        if i % every == 0 or r.dead:
            print(i, r.desc(), "lag" if r.lagged else "", r.edesc())
            if shots:
                g.e.screenshot(f"{shots}_{i:05d}")
        if r.dead:
            print("DEAD")
            break
    print(f"{n / (time.time() - t0):.0f} frames/s; ignored pad frames {g.ignored}; lag {g.lag}")
