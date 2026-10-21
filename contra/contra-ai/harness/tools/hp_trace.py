"""Play a movie segment from a state and log every change of enemy HP / vulnerability for slots that are not bullets.

    python tools/hp_trace.py <state> <movie.inputs.txt> <m> <frames> [--from i] [--poke addr=val,...] [--edits seg.json]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs, to_hex  # noqa: E402
from contra.resync import apply_edit  # noqa: E402

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]
        return v
    return default


i0 = int(opt("--from", "0"))
pokes = opt("--poke", "")
edits = opt("--edits", None)
state, mv, m, n = args[0], args[1], int(args[2]), int(args[3])
rows = [()] * (n + 60) if mv == "-" else [tuple(r) for r in read_inputs(mv)[m - 1:m - 1 + n + 60]]
if edits:
    for ed in json.loads(Path(edits).read_text())["edits"]:
        rows = apply_edit(rows, tuple(ed))
rows = rows[:n]
with BizHawk(log_name="hptrace.log", fields={}) as e:
    e.load(state)
    for pk in [p for p in pokes.split(",") if p]:
        a, v = pk.split("=")
        e.poke(int(a, 0), int(v, 0))
    if i0:
        e.run(rows[:i0])
    prev = np.frombuffer(e.ram_all(), dtype=np.uint8)
    for i in range(i0, n):
        e.cmd("stepx " + to_hex([rows[i]]))
        r = np.frombuffer(e.ram_all(), dtype=np.uint8)
        ev = []
        for s in range(16):
            t = r[0x528 + s]
            if r[0x4B8 + s] and t != 1 and (not prev[0x4B8 + s] or prev[0x528 + s] != t):
                ev.append(f"slot {s} NEW type ${t:02x} hp {r[0x578 + s]} x={r[0x33E + s]} y={r[0x324 + s]} state ${r[0x598 + s]:02x}")
            elif r[0x4B8 + s] and t != 1:
                if r[0x578 + s] != prev[0x578 + s]:
                    ev.append(f"slot {s} type ${t:02x} hp {prev[0x578 + s]}->{r[0x578 + s]}")
                if (r[0x598 + s] ^ prev[0x598 + s]) & 0x80:
                    ev.append(f"slot {s} type ${t:02x} {'INVULNERABLE' if r[0x598 + s] & 0x80 else 'vulnerable'} (routine {r[0x4B8 + s]})")
            elif prev[0x4B8 + s] and not r[0x4B8 + s] and prev[0x528 + s] != 1:
                ev.append(f"slot {s} type ${prev[0x528 + s]:02x} gone")
        for a, nm in ((0x3B, "bossdef"), (0x2C, "lroutine"), (0x90, "pstate"), (0xAA, "weapon"), (0x64, "screen"), (0x84, "autoscroll_done")):
            if r[a] != prev[a]:
                ev.append(f"{nm} {prev[a]}->{r[a]}")
        if ev:
            print(f"i={i:5d} movie {m + i} x={r[0x334]:3d} y={r[0x31A]:3d} scr {r[0x64]}.{r[0x65]:3d} in={'+'.join(rows[i]) or '.':14s} " + "; ".join(ev), flush=True)
        prev = r
