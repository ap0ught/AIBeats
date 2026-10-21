"""Probe 3: is there a way to LET GO of the helicopter bug (anim 36/37)?  From the carried state at L9c 7880 (and 7960, 8060) try every
button / pair held for 40 frames, plus taps, and report when the anim leaves 36/37 and what the toad does next."""
from itertools import combinations
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p3.log")
e.load("L9heli_7852")
BT = ["Up", "Down", "Left", "Right", "Select", "B", "A"]
combos = [()] + [(b,) for b in BT] + [c for c in combinations(BT, 2) if not (set(c) == {"Left", "Right"} or set(c) == {"Up", "Down"})]
for f in range(OFF + 7852, OFF + 8060):
    e.step(bt(ins[f]), 1); idx = f + 1 - OFF
    if idx in (7880, 7960, 8060):
        m = e.ram(0, 0x800); print("root", idx, tstr(m), "|", ostr(m), flush=True); root = e.msave()
        for c in combos:
            for mode in ("hold", "tap", "mash"):
                e.mload(root); free = None; tr = []
                for i in range(48):
                    b = c if mode == "hold" or (mode == "tap" and i == 0) or (mode == "mash" and i % 2 == 0) else ()
                    e.step(b, 1); m = e.ram(0, 0x800); s = toad(m)
                    if free is None and s["an"] not in CARRIED: free = (i + 1, s["x"], s["H"], s["an"])
                    if i in (15, 31, 47): tr.append((s["x"], s["H"], s["an"], s["hp"]))
                if free or mode == "hold": print(f"  {idx} {mode:5s} {'+'.join(c):14s} free {free} {tr}", flush=True)
        e.mload(root)
e.close()
