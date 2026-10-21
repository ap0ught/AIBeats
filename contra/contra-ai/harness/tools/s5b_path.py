"""Replay a segment and print Bill's path compactly: every change of ground level / take-off / landing.

    python tools/s5b_path.py <state> <seg.json> [t0 t1]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game  # noqa: E402

state, seg = sys.argv[1], sys.argv[2]
t0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
t1 = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
g = Game(name="s5b_path")
try:
    g.load_file(state)
    prev = None
    for i, row in enumerate(rows[:t1]):
        r = g.step_raw(row)
        if r.lr != 4 or r.auto:
            if r.auto:
                break
            prev = r
            continue
        if prev is not None and i >= t0:
            ev = None
            if bool(prev.air) != bool(r.air):
                ev = ("TAKEOFF " + ("jump" if r.jumping else "fall")) if r.air else "LAND"
            if ev:
                print(f"t={i:5d} prog={r.prog:5d} y={r.y:3d} sub={r.m[0x94]:02x} {ev} in={'+'.join(row)} peak?")
        prev = r
finally:
    g.close()
