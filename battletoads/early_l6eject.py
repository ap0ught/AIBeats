"""EARLY track (2026-10-09): Karnath warp room - does the rising snake head EJECT a toad that lets go next to it?
The record's toad passes through the head sprite at head height and comes out on its right side moving fast
(logs/fix/wr_karnath_3.jpg, video 187.75-187.90).  From up14's own climb at r+f0 (the toad hangs on the left side,
x 95, a little below the head) hold one pad state for 24 frames and report the rightmost x and where the toad is.
    python early_l6eject.py   -> logs/fix/early_l6eject.txt"""
from early_l6vault import *   # noqa (rd, bt, ROOT, LOGS_DIR, BizHawk)

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_l6eject.log")
e.load("cap14_f11000")
for i in range(11000, ROOT):
    e.step(bt(lines[i]), 1)
room = e.msave()
res = []
ACTS2 = [(), ("A",), ("Right",), ("Right", "A"), ("Left",), ("Left", "A"), ("Down",), ("Up",), ("Down", "Right"), ("B",), ("Right", "B")]
for f0 in (150, 160, 170, 176, 182, 188, 194, 200, 206, 212, 218, 222):
    e.mload(room)
    for i in range(ROOT, ROOT + f0):
        e.step(bt(lines[i]), 1)
    s = rd(e)
    base = e.msave()
    for a in ACTS2:
        for pre in (0, 1, 2, 3):                 # the climb hop has a 4-frame rhythm: try each phase
            e.mload(base)
            for i in range(pre):
                e.step(bt(lines[ROOT + f0 + i]), 1)
            mx, at, hurt, t = 0, None, False, None
            for j in range(24):
                e.step(a, 1)
                t = rd(e)
                if t["hp"] < 47:
                    hurt = True
                    break
                if t["x"] > mx:
                    mx, at = t["x"], (j + 1, t["x"], t["H"], t["H"] - t["head"][1] if t["head"] else None, t["an"], t["z"])
            res.append((f0, pre, "+".join(a) or "-", s["H"] - s["head"][1], mx, at, hurt))
    e.mfree(base)
out = ["f0 pre action dH0 -> rightmost x (frame, x, H, dH, anim, z) hurt"]
for r in res:
    if r[4] > 100:
        out.append(str(r))
out.append(f"{len(res)} trials; {sum(1 for r in res if r[4] > 100)} moved right of x 100; max x {max(r[4] for r in res)}")
print("\n".join(out[-40:]))
open(LOGS_DIR / "fix" / "early_l6eject.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
e.close()
