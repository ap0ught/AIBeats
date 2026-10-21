"""Probe the heart room: from a state near the boss scroll, play a simple policy and print the heart's HP, the
player and the enemies; screenshots at chosen frames.

    python tools/s8_heart_probe.py <state> <policy> [frames=420] [--shots prefix:i1,i2]
policy: comma list of  <from>:<buttons>  (buttons joined by +, B is added at the legal cadence unless "nofire")
        e.g.  0:Right,150:Right+Up
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots"); shots = args[i + 1]; del args[i:i + 2]
state = args[0]
pol = []
for tok in args[1].split(","):
    a, b = tok.split(":")
    pol.append((int(a), tuple(x for x in b.split("+") if x and x != "nofire"), "nofire" in b))
n = int(args[2]) if len(args) > 2 else 420
shot_at = set()
if shots:
    pre, lst = shots.split(":")
    shot_at = set(int(x) for x in lst.split(","))
NAMES = {0x10: "guardian", 0x11: "fetus", 0x12: "wadder", 0x13: "blob", 0x14: "spider", 0x15: "egg", 0x16: "HEART", 1: "eb"}
with Game(log_name="s8_heart_probe.log") as g:
    r = g.load(state)
    prev = r
    for i in range(n):
        btn, nofire = (), False
        for a, b, nf in pol:
            if i >= a:
                btn, nofire = b, nf
        want = set(btn)
        if not nofire:
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
            if m[0x4B8 + s] and (not pm[0x4B8 + s] or pm[0x528 + s] != t) and t != 1:
                ev.append(f"NEW {s}:{NAMES.get(t, hex(t))} hp{m[0x578 + s]} at {m[0x33E + s]},{m[0x324 + s]}")
            elif m[0x4B8 + s] and t in (0x16, 0x15, 0x10) and m[0x578 + s] != pm[0x578 + s]:
                ev.append(f"{NAMES.get(t)}[{s}] hp {pm[0x578 + s]}->{m[0x578 + s]}")
        if m[0x3B] != pm[0x3B]:
            ev.append(f"bossdef {m[0x3B]}")
        if (m[0x75] != 0) != (pm[0x75] != 0):
            ev.append(f"auto0 {m[0x75]}")
        if r.lagged:
            ev.append("LAG")
        if ev or i % 30 == 0:
            hs = [s for s in range(16) if m[0x4B8 + s] and m[0x528 + s] == 0x16]
            hinfo = f"heart {m[0x33E + hs[0]]},{m[0x324 + hs[0]]} hp {m[0x578 + hs[0]]}" if hs else ""
            print(f"{i:4d} x={r.x:3d} y={r.y:3d} pos={r.pos} jump={r.jump:02x} nbul={r.nbul()} {hinfo} | " + "; ".join(ev), flush=True)
        if r.dead and not prev.dead:
            print("DEAD at", i, r.desc(), r.edesc())
            break
        prev = r
    print("end", r.desc(), "lag", g.lag)
