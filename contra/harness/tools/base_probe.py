"""Play a movie segment from a state and print an event log (rooms, clears, deaths, lag) next to the movie's inputs.

    python tools/base_probe.py <state> <movie.inputs.txt> <m> [frames] [--edits logs/x.seg.json]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import apply_edit  # noqa: E402

args = sys.argv[1:]
edits = None
if "--edits" in args:
    i = args.index("--edits"); edits = args[i + 1]; del args[i:i + 2]
state, movie, m = args[0], read_inputs(args[1]), int(args[2])
n = int(args[3]) if len(args) > 3 else 1500
rows = [tuple(r) for r in movie[m - 1:m - 1 + n + 50]]
if edits:
    for ed in json.loads(Path(edits).read_text())["edits"]:
        rows = apply_edit(rows, tuple(ed))
rows = rows[:n]
F = {"level": 0x30, "lroutine": 0x2C, "pstate": 0x90, "death": 0xB4, "screen": 0x64, "scroll": 0x65, "cleared": 0x37,
     "loc": 0x40, "cores": 0x86, "elec": 0xC8, "trans": 0x61, "iscroll": 0x73, "x": 0x334, "y": 0x31A, "adv": 0xD0,
     "pseq": 0xBC, "pad": 0xF1, "fc": 0x1A, "bossdef": 0x3B, "attack": 0x88, "inv": 0xAE}
with BizHawk(log_name="base_probe.log", fields=F) as e:
    e.load(state)
    e.trace(True)
    e.run(rows)
    tr = e.last_trace
    hp = None
prev = None
for i, s in enumerate(tr):
    ev = []
    if prev is not None:
        for k in ("screen", "cleared", "loc", "cores", "iscroll", "adv", "pstate", "death", "bossdef", "lroutine", "attack"):
            if s[k] != prev[k]:
                ev.append(f"{k} {prev[k]}->{s[k]}")
        if s["elec"] and not prev["elec"]:
            ev.append(f"ELECTROCUTED {s['elec']}")
        if s["lagged"]:
            ev.append("lag")
    if ev:
        print(f"i={i:5d} movie {m + i:5d} emu {s['frame']:5d} x={s['x']:3d} y={s['y']:3d} in={'+'.join(rows[i]) or '.':12s} " + "; ".join(ev))
    prev = s
print("last", tr[-1])
