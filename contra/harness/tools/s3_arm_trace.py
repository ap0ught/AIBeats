"""Replay a stage 3 segment and print the dragon's parts while waiting for the mouth.

    python tools/s3_arm_trace.py <seg.json> <from row> <to row> [every=20] [--shots prefix:r1,r2]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots"); shots = args[i + 1]; del args[i:i + 2]
seg = json.loads(Path(args[0]).read_text())
a, b = int(args[1]), int(args[2])
every = int(args[3]) if len(args) > 3 else 20
rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
shot_at = set()
if shots:
    pre, lst = shots.split(":")
    shot_at = set(int(x) for x in lst.split(","))
with Game(log_name="s3_arm_trace.log") as g:
    g.load(seg["state"])
    g.run(rows[:a])
    prev = g.r
    for i in range(a, min(b, len(rows))):
        g.e.cmd("stepx " + f"{to_mask(rows[i]):02x}")
        r = g.read()
        if i in shot_at:
            g.e.screenshot(f"{pre}_{i:05d}")
        m = r.m
        ev = []
        for s in range(16):
            if m[0x4B8 + s] and m[0x528 + s] == 0x15 and m[0x4B8 + s] != prev.m[0x4B8 + s]:
                ev.append(f"slot{s} routine {prev.m[0x4B8 + s]}->{m[0x4B8 + s]}")
        if i % every == 0 or ev:
            hands = [(s, m[0x33E + s], m[0x324 + s], m[0x578 + s], m[0x4B8 + s]) for s in range(16)
                     if m[0x4B8 + s] and m[0x528 + s] == 0x15 and m[0x578 + s] < 0xF0]
            orbs = [(m[0x33E + s], m[0x324 + s]) for s in range(16) if m[0x4B8 + s] and m[0x528 + s] == 0x15 and m[0x578 + s] >= 0xF0]
            buls = [(m[0x33E + s], m[0x324 + s]) for s in range(16) if m[0x4B8 + s] and m[0x528 + s] == 0x01]
            oth = [(hex(m[0x528 + s]), m[0x33E + s], m[0x324 + s]) for s in range(16) if m[0x4B8 + s] and m[0x528 + s] not in (0x15, 0x14, 0x01)]
            print(f"{i:5d} bill {r.x:3d},{r.y:3d} fc={r.fc:3d} hands(slot,x,y,hp,routine) {hands} orbs {orbs} bullets {buls} other {oth} "
                  + "; ".join(ev), flush=True)
        prev = r
