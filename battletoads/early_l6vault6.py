"""EARLY track (2026-10-09): Karnath warp room, part 6 - is there ANY press that makes the toad jump while it is at or on
the rising head?  Root: the state after 176 / 182 / 189 inputs of logs/fix/early_l6vault2_best.keep.json (toad hanging
left of the head, level with it and above it).  Sequence: k frames of the climb / walk-over input (A or Right+A), a
release of g frames (one of 5 pad states), then one of 9 presses held 14 frames.  A JUMP = the toad's height relative
to the head grows by 10 px or more within 12 frames of the press.

    python early_l6vault6.py   -> logs/fix/early_l6vault6.txt
"""
import itertools
import json

from early_l6vault2 import rd, bt, ROOT, LOGS_DIR, BizHawk

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
pre_all = json.load(open(LOGS_DIR / "fix" / "early_l6vault2_best.keep.json"))["inputs"]
e = BizHawk(log_name="early_l6vault6.log")
e.load("cap14_f11000")
for i in range(11000, ROOT):
    e.step(bt(lines[i]), 1)
room = e.msave()
RELEASE = [(), ("Right",), ("Left",), ("Up",), ("Down",)]
PRESS = [("A",), ("Right", "A"), ("Left", "A"), ("Up", "A"), ("Up", "Right", "A"), ("Down", "A"), ("Down", "Right", "A"), ("B",), ("Right", "B")]
out, n, jumps = [], 0, []
for cut in (150, 160, 168, 176, 182, 189):
    e.mload(room)
    for b in pre_all[:cut]:
        e.step(bt(b), 1)
    t = rd(e)
    base = e.msave()
    out.append(f"root r+{cut}: toad x {t['x']} H {t['H']} rel {t['H'] - t['head'][1]} anim {t['an']} z {t['z']}")
    print(out[-1], flush=True)
    for k, hold, g, rel_btn, press in itertools.product(range(0, 14, 1), (("A",), ("Right", "A")), (1, 2), RELEASE, PRESS):
        if k % 2 and cut != 189:
            continue
        e.mload(base)
        ok = True
        for _ in range(k):
            e.step(hold, 1)
        for _ in range(g):
            e.step(rel_btn, 1)
        t0 = rd(e)
        if t0["hp"] < 47 or not t0["head"]:
            continue
        r0, best, bx = t0["H"] - t0["head"][1], -999, None
        for j in range(12):
            e.step(press, 1)
            t = rd(e)
            if t["hp"] < 47 or not t["head"]:
                ok = False
                break
            if t["H"] - t["head"][1] - r0 > best:
                best, bx = t["H"] - t["head"][1] - r0, (j + 1, t["x"], t["H"], t["an"], t["z"], t["spd"])
        n += 1
        if ok and best >= 10:
            jumps.append((cut, k, "+".join(hold), g, "+".join(rel_btn) or "-", "+".join(press), r0, best, bx))
            if len(jumps) <= 15:
                print("  JUMP:", jumps[-1], flush=True)
    e.mfree(base)
out.append(f"{n} sequences; {len(jumps)} raise the toad 10 px or more relative to the head within 12 frames")
out += ["  " + str(j) for j in sorted(jumps, key=lambda z: -z[7])[:30]]
print(out[-1 - min(30, len(jumps))], flush=True)
open(LOGS_DIR / "fix" / "early_l6vault6.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
e.close()
