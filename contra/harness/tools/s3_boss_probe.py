"""Watch the dragon: from a state on the top floor, play a policy and print the boss timeline.

    python tools/s3_boss_probe.py <state> <policy from:buttons,...> [frames=1000] [--shots prefix:i1,i2] [--fire]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots"); shots = args[i + 1]; del args[i:i + 2]
fire = "--fire" in args
if fire:
    args.remove("--fire")
state = args[0]
pol = []
for tok in args[1].split(","):
    a, b = tok.split(":")
    pol.append((int(a), tuple(x for x in b.split("+") if x and x != "-")))
n = int(args[2]) if len(args) > 2 else 1000
shot_at = set()
if shots:
    pre, lst = shots.split(":")
    shot_at = set(int(x) for x in lst.split(","))
with Game(log_name="s3_boss_probe.log") as g:
    r = g.load(state)
    prev = r
    for i in range(n):
        btn = ()
        for a, b in pol:
            if i >= a:
                btn = b
        want = set(btn)
        if fire:
            p = g.pad
            if p.down["B"]:
                if p.t - p.start["B"] < 2:
                    want.add("B")
            elif p.can_press("B"):
                want.add("B")
        r = g.step(want)
        if i in shot_at:
            g.e.screenshot(f"{pre}_{i:04d}")
        m, pm = r.m, prev.m
        ev = []
        for s in range(16):
            t = m[0x528 + s]
            if not m[0x4B8 + s]:
                if pm[0x4B8 + s] and pm[0x528 + s] != 1:
                    ev.append(f"gone {s}:t{pm[0x528 + s]:02x}")
                continue
            if not pm[0x4B8 + s] or pm[0x528 + s] != t:
                if t != 1:
                    ev.append(f"NEW {s}:t{t:02x} hp{m[0x578 + s]} at {m[0x33E + s]},{m[0x324 + s]} st{m[0x598 + s]:02x}")
                continue
            if t in (0x14, 0x15):
                if m[0x578 + s] != pm[0x578 + s]:
                    ev.append(f"{s}:t{t:02x} hp {pm[0x578 + s]}->{m[0x578 + s]}")
                if m[0x4B8 + s] != pm[0x4B8 + s]:
                    ev.append(f"{s}:t{t:02x} routine {pm[0x4B8 + s]}->{m[0x4B8 + s]}")
                if (m[0x598 + s] ^ pm[0x598 + s]) & 0x81:
                    ev.append(f"{s}:t{t:02x} state {pm[0x598 + s]:02x}->{m[0x598 + s]:02x}")
        for a, nm in ((0x3B, "bossdef"), (0x2C, "lroutine"), (0x84, "autodone"), (0x85, "partsdead"), (0x30, "level"),
                      (0x2D, "elr")):
            if m[a] != pm[a]:
                ev.append(f"{nm} {pm[a]}->{m[a]}")
        for a, nm in ((0x75, "auto0"), (0x74, "paltimer")):
            if (m[a] != 0) != (pm[a] != 0):
                ev.append(f"{nm} {pm[a]}->{m[a]}")
        if r.lagged:
            ev.append("LAG")
        if ev or i % 100 == 0:
            print(f"{i:4d} f{r.frame} x={r.x:3d} y={r.y:3d} A={r.screen * 240 + r.scroll} fc={r.fc:3d} jump={r.jump:02x} | " + "; ".join(ev), flush=True)
        if r.dead and not prev.dead:
            print("DEAD at", i, r.desc(), r.edesc())
            break
        prev = r
    print("end", r.desc(), "lag", g.lag)
