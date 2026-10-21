"""Replay a stage segment from a state and print its route events: jumps, ledge changes, weapon changes, frames
without forward progress, enemy kills near the player. Used to read the route out of the fitted TAS stages.

    python tools/s1_trace_ref.py <state> <seg.json|inputs.txt> [max_frames]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs, to_hex  # noqa: E402

state, seg = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
if seg.endswith(".json"):
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
else:
    rows = read_inputs(seg)
rows = rows[:mx]
ETYPE = {}
with BizHawk(log_name="s1_trace_ref.log", fields={}) as e:
    e.load(state)
    prev = None
    L = None
    for i, row in enumerate(rows):
        e.cmd("stepx " + to_hex([row]))
        r = e.ram_all()
        fr = i + 1
        if r[0x2C] == 4 and L is None:
            L = fr
        if L is None:
            continue
        t = fr - L
        prog = r[0x64] * 256 + r[0x65] + r[0x334]
        ev = []
        if prev is not None:
            pprog = prev[0x64] * 256 + prev[0x65] + prev[0x334]
            if (r[0xA0] & 15) and not (prev[0xA0] & 15):
                ev.append("JUMP")
            if not (r[0xA0] & 15) and (prev[0xA0] & 15):
                ev.append("LAND")
            if r[0xA4] and not prev[0xA4]:
                ev.append(f"FALL code ${r[0xA4]:02x}")
            if r[0xAA] != prev[0xAA]:
                ev.append(f"WEAPON ${prev[0xAA]:02x}->${r[0xAA]:02x}")
            if prog - pprog != 1 and r[0x2C] == 4 and r[0x1A] != prev[0x1A]:
                ev.append(f"dprog {prog - pprog}")
            if r[0x1A] == prev[0x1A]:
                ev.append("LAG")
            if r[0x75] and not prev[0x75]:
                ev.append("AUTOSCROLL start")
            if r[0x2C] != prev[0x2C]:
                ev.append(f"lroutine {prev[0x2C]}->{r[0x2C]}")
            if r[0x3B] != prev[0x3B]:
                ev.append(f"bossdef {prev[0x3B]}->{r[0x3B]}")
            if r[0x30] != prev[0x30]:
                ev.append(f"level {prev[0x30]}->{r[0x30]}")
            if r[0xB2] != prev[0xB2]:
                ev.append(f"water ${prev[0xB2]:02x}->${r[0xB2]:02x}")
            for s in range(16):
                ty = r[0x528 + s]
                if r[0x4B8 + s] and (not prev[0x4B8 + s] or prev[0x528 + s] != ty) and ty != 1:
                    ev.append(f"NEW e{s} type ${ty:02x} hp {r[0x578 + s]} at {r[0x33E + s]},{r[0x324 + s]} attr ${r[0x5A8 + s]:02x}")
                if r[0x4B8 + s] and prev[0x4B8 + s] and ty == prev[0x528 + s] and ty != 1 and r[0x578 + s] == 0 and prev[0x578 + s] != 0:
                    ev.append(f"KILL e{s} type ${ty:02x}")
        if ev:
            print(f"t={t:5d} scr {r[0x64]:2d}.{r[0x65]:3d} x={r[0x334]:3d} y={r[0x31A]:3d} fc={r[0x1A]:3d} in={'+'.join(row) or '.':12s} " + "; ".join(ev), flush=True)
        prev = r
