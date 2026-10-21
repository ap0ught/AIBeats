"""Replay an input list from power-on and keep the whole 2 KB of RAM (and the PPU's OAM) for every frame.

    python tools/ram_capture.py <logs/x.inputs.txt> <name> [--core NesHawk] [--stop N] [--no-oam]

Writes logs/<name>.ram.npy   uint8 [rows+1, 2048]   row i = RAM after input row i (row 0 = before the first step)
       logs/<name>.oam.npy   uint8 [rows+1, 256]    the PPU's sprite memory after that frame
       logs/<name>.meta.npy  int32 [rows+1, 3]      emu.framecount, emu.lagcount, islagged
       logs/<name>.ram_inputs.txt                    the input of each row ("" for row 0), for contra/ramscan.py
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs, to_hex  # noqa: E402

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name)
        if isinstance(default, bool):
            del args[i]
            return True
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


core, stop, no_oam = opt("--core", "NesHawk"), opt("--stop", 0), opt("--no-oam", False)
rows = read_inputs(args[0])
name = args[1]
if stop:
    rows = rows[:stop]
n = len(rows)
ram = np.zeros((n + 1, 2048), dtype=np.uint8)
oam = np.zeros((n + 1, 256), dtype=np.uint8)
meta = np.zeros((n + 1, 3), dtype=np.int32)
t0 = time.time()
with BizHawk(log_name=f"ramcap_{name}.log", fields={}, core=core) as e:
    def grab(i):
        ram[i] = np.frombuffer(e.ram_all(), dtype=np.uint8)
        if not no_oam:
            oam[i] = np.frombuffer(e.oam(), dtype=np.uint8)
        s = e.state()
        meta[i] = (s["frame"], s["lag"], s["lagged"])
    grab(0)
    for i, r in enumerate(rows):
        e.cmd("stepx " + to_hex([r]))
        grab(i + 1)
        if (i + 1) % 5000 == 0:
            print(f"{i + 1}/{n}  {(i + 1) / (time.time() - t0):.0f} fps", flush=True)
np.save(LOGS_DIR / f"{name}.ram.npy", ram)
np.save(LOGS_DIR / f"{name}.oam.npy", oam)
np.save(LOGS_DIR / f"{name}.meta.npy", meta)
(LOGS_DIR / f"{name}.ram_inputs.txt").write_text("\n".join([""] + ["+".join(r) for r in rows]), encoding="utf-8")
print(f"captured {n} frames in {time.time() - t0:.0f}s -> logs/{name}.ram.npy")
