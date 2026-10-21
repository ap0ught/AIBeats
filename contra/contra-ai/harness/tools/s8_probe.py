"""Stage 8 probe: naive play (Right held, B tapped 2 on / 3 off, optional aim) from a state; logs events.

    python tools/s8_probe.py [state=dbg/s8_pre] [frames=4000] [extra buttons e.g. Up]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "dbg/s8_pre"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
extra = tuple(sys.argv[3].split("+")) if len(sys.argv) > 3 else ()
NAMES = {0x10: "guardian", 0x11: "fetus", 0x12: "wadder", 0x13: "blob", 0x14: "spider", 0x15: "eggron", 0x16: "heart",
         0x03: "capsule", 0x00: "item", 0x01: "ebullet"}
with Game(log_name="s8_probe.log") as g:
    r = g.load(state)
    prev = r
    t0 = time.time()
    for i in range(n):
        want = ("Right",) + extra + (("B",) if i % 5 < 2 else ())
        r = g.step(want)
        ev = []
        m, pm = r.m, prev.m
        for s in range(16):
            t = m[0x528 + s]
            if m[0x4B8 + s] and (not pm[0x4B8 + s] or pm[0x528 + s] != t) and t != 1:
                ev.append(f"NEW {s}:{NAMES.get(t, hex(t))} hp{m[0x578 + s]} at {m[0x33E + s]},{m[0x324 + s]} attr {m[0x5A8 + s]:02x} st {m[0x598 + s]:02x}")
            elif m[0x4B8 + s] and t in (0x10, 0x16, 0x15) and m[0x578 + s] != pm[0x578 + s]:
                if m[0x578 + s] % 10 == 0 or m[0x578 + s] < 3:
                    ev.append(f"{NAMES.get(t)} hp {m[0x578 + s]}")
            elif pm[0x4B8 + s] and not m[0x4B8 + s] and pm[0x528 + s] not in (1,):
                ev.append(f"gone {s}:{NAMES.get(pm[0x528 + s], hex(pm[0x528 + s]))}")
        for a, nm in ((0x3B, "bossdef"), (0x2C, "lroutine"), (0x90, "pstate"), (0xAA, "weapon"), (0x64, "screen"),
                      (0x84, "autodone"), (0xB0, "barrier")):
            if m[a] != pm[a] and not (nm == "barrier" and m[a] and pm[a]):
                ev.append(f"{nm} {pm[a]}->{m[a]}")
        if (m[0x75] != 0) != (pm[0x75] != 0):
            ev.append(f"autoscroll0 {pm[0x75]}->{m[0x75]}")
        if (m[0x76] != 0) != (pm[0x76] != 0):
            ev.append(f"autoscroll1 {pm[0x76]}->{m[0x76]}")
        if r.lagged:
            ev.append("LAG")
        if ev:
            print(i, r.desc(), "; ".join(ev), flush=True)
        if r.dead and not prev.dead:
            print("DEAD at", i, r.desc(), r.edesc())
            break
        prev = r
    print(f"{(i + 1) / (time.time() - t0):.0f} frames/s; ignored {g.ignored}; lag {g.lag}")
