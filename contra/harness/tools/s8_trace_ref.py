"""Replay a seg.json (rows) from its state and print a compact trace: position every k frames, jumps, HP events.

    python tools/s8_trace_ref.py <seg.json> [every=20] [from=0] [to=99999] [--shots prefix:i1,i2,...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game, PROJECT  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots"); shots = args[i + 1]; del args[i:i + 2]
seg = json.loads(Path(args[0]).read_text())
every = int(args[1]) if len(args) > 1 else 20
i0 = int(args[2]) if len(args) > 2 else 0
i1 = int(args[3]) if len(args) > 3 else 99999
rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
shot_at = set()
if shots:
    pre, lst = shots.split(":")
    shot_at = set(int(x) for x in lst.split(","))
with Game(log_name="s8_trace.log") as g:
    r = g.load(seg["state"])
    prev = r
    for i, row in enumerate(rows[:i1]):
        g.e.cmd("stepx " + f"{to_mask(row):02x}")
        r = g.read()
        if i in shot_at:
            g.e.screenshot(f"{pre}_{i:05d}")
        if i < i0:
            prev = r
            continue
        m, pm = r.m, prev.m
        ev = []
        for s in range(16):
            t = m[0x528 + s]
            if m[0x4B8 + s] and (not pm[0x4B8 + s] or pm[0x528 + s] != t) and t != 1:
                ev.append(f"NEW {s}:t{t:02x} hp{m[0x578 + s]} at {m[0x33E + s]},{m[0x324 + s]} a{m[0x5A8 + s]:02x}")
            elif m[0x4B8 + s] and t != 1 and m[0x578 + s] != pm[0x578 + s]:
                ev.append(f"{s}:t{t:02x} hp {pm[0x578 + s]}->{m[0x578 + s]}")
            elif pm[0x4B8 + s] and not m[0x4B8 + s] and pm[0x528 + s] != 1:
                ev.append(f"gone {s}:t{pm[0x528 + s]:02x}")
        for a, nm in ((0x3B, "bossdef"), (0x2C, "lroutine"), (0x90, "pstate"), (0xAA, "weapon"), (0x84, "autodone"),
                      (0x25, "pause")):
            if m[a] != pm[a]:
                ev.append(f"{nm} {pm[a]}->{m[a]}")
        for a, nm in ((0x75, "auto0"), (0x76, "auto1"), (0xB0, "barrier")):
            if (m[a] != 0) != (pm[a] != 0):
                ev.append(f"{nm} {pm[a]}->{m[a]}")
        if (m[0xA0] != 0) != (pm[0xA0] != 0):
            ev.append("JUMP" if m[0xA0] else "LAND")
        if (m[0xA4] != 0) != (pm[0xA4] != 0):
            ev.append("FALL" if m[0xA4] else "LAND(f)")
        if r.lagged:
            ev.append("LAG")
        if ev or i % every == 0:
            print(f"{i:5d} {'+'.join(row):14s} {r.desc()} | " + "; ".join(ev), flush=True)
        prev = r
