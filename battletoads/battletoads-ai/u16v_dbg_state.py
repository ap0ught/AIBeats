"""Verifier debug: does an in-memory state reload reproduce the plain replay frame for frame around frame 2516?"""
import sys
from pathlib import Path
from toads.emulator import BizHawk
FIX = Path(__file__).resolve().parent / "logs" / "fix"
rows = Path(FIX / "u16v_up16b2.inputs.txt").read_text(encoding="utf-8").split("\n")[1:]
REF = (FIX / "u16v_run1.ram").read_bytes()
ref = lambda f: REF[(f - 1) * 2048:f * 2048]
tk = lambda r: tuple(x for x in r.split(",") if x)
e = BizHawk(log_name="u16v_dbg_emu.log", fields={"level": 0x10})
for f in range(1, 2311):
    e.step(tk(rows[f - 1]), 1)
sid = e.msave()
for label in ("main line", "after mload #1", "after mload #2"):
    if label != "main line":
        e.mload(sid)
    diffs = []
    for f in range(2311, 2600):
        s = e.step(tk(rows[f - 1]), 1)
        ram = e.ram_all()
        if ram != ref(f):
            diffs.append((f, [(hex(i), ram[i], ref(f)[i]) for i in range(2048) if ram[i] != ref(f)[i]][:10], s.frame, s.lag))
    print(label, "frames differing from the plain replay:", len(diffs))
    for d in diffs[:12]:
        print("   ", d)
e.close()
