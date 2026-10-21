"""NesHawk port of up17: one more straight replay from power-on, with pictures around the landing and the T. Bird cut.

    python u17p_shots.py <capture tag of the list> [<out prefix>]      e.g. u17p_shots.py u17vd

Replays the input list named in logs/fix/core_<tag>.json through the bridge on the core that capture was made on (read
back from the emulator: the "PPU Bus" memory domain exists only on NesHawk), takes screenshots after the frames listed
below, and compares the RAM after the last input with the capture's. Pictures: logs/fix/core_u17_shots/<prefix>_f<frame>.png
(a picture taken after frame N shows the game state of frame N-1 for sprites). Sends only capstep / screenshot / coreinfo:
no savestate, no memory write, nothing on controller 2.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

import core_check_toads as cc
import toads.emulator as emu_mod

FIX = cc.FIX
tag = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else tag
summ = json.loads((FIX / f"core_{tag}.json").read_text())
rows = cc.read_inputs(cc.PROJECT / summ["inputs"])
R = np.memmap(FIX / f"core_{tag}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
lv = R[:, 0x10].astype(int)
anim = R[:, 0x3B5].astype(int)
n = len(R) - 1
landing = next(f for f in range(1, n + 1) if lv[f] == 1 and anim[f - 1] == 5 and anim[f] == 4)
cuts = [f for f in range(1, n + 1) if lv[f - 1] == 13 and lv[f] == 254]
want = sorted(set([landing - 3, landing - 1, landing, landing + 1, landing + 2,
                   cuts[0] - 1, cuts[0], cuts[0] + 12,
                   cuts[1] - 30, cuts[1] - 1, cuts[1], cuts[1] + 1, cuts[1] + 9, cuts[1] + 10, cuts[1] + 11, cuts[1] + 12,
                   cuts[1] + 20, min(cuts[1] + 29, len(rows))]))
core = summ["core_info"]["core_seen"]
os.environ["TOADS_CORE"] = core
emu_mod.BRIDGE_LUA = cc.derived_bridge()
out = FIX / "core_u17_shots"
out.mkdir(parents=True, exist_ok=True)
e = emu_mod.BizHawk(log_name=f"fix_core_{prefix}_shots.log", fields={})
info = cc.parse_info(e.cmd("coreinfo"))
print(f"[{prefix}] list {summ['inputs']} ({len(rows)} frames); core wanted {core}; loaded: {info['core_seen']} (board {info['board']}, "
      f"memory domains {info['domains']})", flush=True)
if info["core_seen"].lower() != core.lower():
    e.close()
    raise SystemExit("wrong core loaded")
ram = b""
seen_cuts = []
prev = None
for i, b in enumerate(rows, 1):
    fc, lag, isl, hx = e.cmd("capstep " + (",".join(b) or "-")).split(" ")
    ram = bytes.fromhex(hx)
    if prev == 13 and ram[0x10] == 254:
        seen_cuts.append(i)
    prev = ram[0x10]
    if i in want:
        p = out / f"{prefix}_f{i:05d}.png"
        e.cmd(f"screenshot {p}")
        same = ram == R[i].tobytes()
        print(f"[{prefix}] frame {i}: level byte {ram[0x10]}, RAM {'= capture' if same else 'DIFFERS from capture'} -> {p.name}", flush=True)
e.close()
got = hashlib.sha1(ram).hexdigest()
ok = got == summ.get("sha1_at_input_end") and seen_cuts == cuts
print(f"[{prefix}] landing {landing}; 13 -> 254 at {seen_cuts} (capture {cuts}); RAM sha1 after the last input {got} "
      f"({'MATCH' if ok else 'MISMATCH'} with the capture's {summ.get('sha1_at_input_end')})")
print(f"[{prefix}] T. Bird cut {cuts[1]}: pictures at cut -30, -1, 0, +1, +9, +10, +11, +12, +20, +29 in {out}")
