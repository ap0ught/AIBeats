"""Watch the bridge flames (enemy type $11) from a state: Bill's buttons per interval, flame X/Y every k frames.

    python tools/s3_flames.py <state> <policy from:buttons,...> [frames=300] [every=8]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

state = sys.argv[1]
pol = []
for tok in sys.argv[2].split(","):
    a, b = tok.split(":")
    pol.append((int(a), tuple(x for x in b.split("+") if x)))
n = int(sys.argv[3]) if len(sys.argv) > 3 else 300
every = int(sys.argv[4]) if len(sys.argv) > 4 else 8
with Game(log_name="s3_flames.log") as g:
    r = g.load(state)
    for i in range(n):
        btn = ()
        for a, b in pol:
            if i >= a:
                btn = b
        r = g.step(btn)
        if i % every == 0 or r.dead:
            fl = [(x, y) for (s, t, ro, hp, x, y, st, at) in r.enemies() if t == 0x11]
            oth = [(hex(t), x, y) for (s, t, ro, hp, x, y, st, at) in r.enemies() if t not in (0x11,)]
            print(f"{i:4d} bill {r.x:3d},{r.y:3d} A={r.screen * 240 + r.scroll} jump={r.jump:02x} flames {fl} others {oth}")
        if r.dead:
            print("DEAD at", i)
            break
