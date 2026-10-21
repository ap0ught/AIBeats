"""Exploratory sessions: run a scripted sequence of button holds with the camera rolling, dumping the whole 2 KB of
RAM every frame to logs/<name>.ram.npy (uint8, frames x 2048) and the inputs alongside, so ramscan.py can ask
"which byte moved when I held Right?" without any guide.

    python explore.py <name> [<start state>] <plan>
    plan = comma list of  <buttons>x<frames>   e.g.  Start:4,-:56,Right:600,A:6,-:54
           (buttons joined with +, '-' = nothing; a plan item may repeat with *N: "Start:4,-:56*20")
"""
import shutil
import sys
import time

import numpy as np

from toads.emulator import BizHawk, SHOTS_DIR, LOGS_DIR
from toads import tokens


def parse_plan(txt: str):
    out = []
    for item in txt.split(","):
        item = item.strip()
        if not item:
            continue
        rep = 1
        if "*" in item:
            item, r = item.split("*")
            rep = int(r)
        btn, n = item.split(":")
        btn = () if btn == "-" else tuple(btn.split("+"))
        out += [(btn, int(n))] * rep
    return out


def run(name: str, plan, state: str | None = None, record: bool = True, shot_every: int = 60, fields=None):
    out = SHOTS_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    emu = BizHawk(log_name=f"{name}.log", record=name if record else None, fields=fields or {})
    if state:
        emu.load(state)
    rams, inputs = [], []
    k = 0
    t0 = time.time()
    for btn, n in plan:
        for _ in range(n):
            emu.step(btn, 1)
            rams.append(np.frombuffer(emu.ram_all(), dtype=np.uint8))
            inputs.append("+".join(btn))
            if len(rams) % shot_every == 0:
                shutil.copyfile(emu.screenshot(f"_tmp_{name}"), out / f"{k:04d}.png")
                k += 1
    arr = np.stack(rams)
    np.save(LOGS_DIR / f"{name}.ram.npy", arr)
    (LOGS_DIR / f"{name}.ram_inputs.txt").write_text("\n".join(inputs))
    emu.save(f"{name}_end")
    print(f"{name}: {len(rams)} frames, {time.time() - t0:.0f}s wall, ram {arr.shape}")
    emu.close()
    return arr, inputs


if __name__ == "__main__":
    name = sys.argv[1]
    if len(sys.argv) == 4:
        state, plan = sys.argv[2], sys.argv[3]
    else:
        state, plan = None, sys.argv[2]
    run(name, parse_plan(plan), state)
    tokens.mark(f"explore {name}")
