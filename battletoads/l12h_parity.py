"""L12h probe: is the queen fight (L13y0) portable when The Revolution's length changes? Delay the end of L12g by n idle frames inserted at a
standing moment, replay to Level 13, compare the entry RAM with L12g_end0 and replay L13y0 behind it."""
import json, sys
from l12h_lib import *
G = seg("L12g"); Q = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L13y0.json"))["inputs"]]
e = BizHawk(log_name="fix_l12h_parity.log")
e.load("L12g_end0"); e.step((), 1); ref = e.ram(0, 0x800)
e.load("L12h_g_f8500"); run(e, G[8500:8600]); base = e.msave()
for at, n in [(8649, 0), (8649, 2), (8649, 1), (8609, 2), (8609, 4), (8649, 4), (8609, 1), (8649, 3)]:
    e.mload(base); seq = G[8600:at] + [""] * n + G[at:]
    k = 8600; end = None
    for b in seq:
        e.step(bt(b), 1); k += 1
        if e.byte(0x10) == 13: end = k; break
    if end is None:
        for i in range(300):
            e.step((), 1); k += 1
            if e.byte(0x10) == 13: end = k; break
    if end is None: print("insert", n, "at", at, ": level 13 not reached", flush=True); continue
    # L12g ends (set-down) at 8880 with level byte 13 from 8880: mimic -> state after input `end`
    st = e.msave(); e.step((), 1); m = e.ram(0, 0x800); d = [a for a in range(0x800) if m[a] != ref[a]]
    e.mload(st)
    ctr = []; left = None
    for i, b in enumerate(Q):
        e.step(bt(b), 1)
        if i % 200 == 199: ctr.append(e.byte(0x586))
        if left is None and e.byte(0x10) != 13: left = i + 1
    hp = e.byte(0x51A)
    print("insert", n, "at", at, ": level 13 at", end, "| entry RAM differs in", [f"${a:03X}" for a in d][:12], "| queen ctr", ctr, "left13 at", left, "hp", hp, flush=True)
    e.mfree(st)
e.close()
