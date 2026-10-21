"""EARLY track (2026-10-09): Karnath warp room diagnostic - what happens when the climbing toad catches the rising head?
Jump at the snake at S=sj (Right+A x a), then mash Left+A / Right+A every frame and never do anything else; print the
toad and the head every 3 frames.      python early_l6diag.py x0 sj a [p=1]"""
import sys
from early_l6fling import *   # noqa

x0, sj, a = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
p = int(sys.argv[4]) if len(sys.argv) > 4 else 1
lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_l6diag.log", fields=F)
e.load("cap14_f11000")
for i in range(11000, ROOT):
    s = e.step(bt(lines[i]), 1)
s0 = s
r, phase, cnt = 0, "walk", 0
out = []
while r < 300:
    x, H = s.x | s.xh << 8, s.height | s.hh << 8
    S = r - 71
    inp = ()
    if phase == "walk":
        if S >= sj:
            phase, cnt = "jump", a
        elif abs(x - x0) > 1 and s.z == 0:
            inp = ("Right",) if x < x0 else ("Left",)
    if phase == "jump":
        if cnt > 0:
            inp = ("Right", "A"); cnt -= 1
        else:
            phase = "climb"
    if phase == "climb":
        inp = ("Left", "A") if (r // p) % 2 == 0 else ("Right", "A")
    s = e.step(inp, 1)
    r += 1
    hd = head(s)
    if r % 3 == 0 or s.hp < 47:
        out.append(f"r+{r} S{r-71}: toad x {s.x | s.xh << 8} H {s.height | s.hh << 8} z {s.z} anim {s.anim} spd {s.spd} hp {s.hp} | head {hd} dH {((s.height | s.hh << 8) - hd[1]) if hd else None} | {'+'.join(inp)}")
    if s.hp < 47 or s.lives < s0.lives:
        out.append("HURT"); break
print("\n".join(out))
open(LOGS_DIR / "fix" / f"early_l6diag_{x0}_{sj}_{a}_{p}.txt", "w").write("\n".join(out) + "\n")
e.close()
