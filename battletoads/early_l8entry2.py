"""EARLY track (2026-10-09): Intruder Excluder's entry wait, part 2.  early_l8entry.py: the old climb inputs shifted by k
frames part from the old track at the first jump (1 px) but the toad is first hurt only much later for k = 28..35.
So: how high does the old line get when it simply starts k frames sooner?  For each k: frames (since the placement,
up14 frame 12488) at which the toad first STANDS 130 / 200 / 330 / 460 / 600 px above the start, unhurt, against
up14's 223 / 263 / 383 / 494 / 563.
    python early_l8entry2.py   -> logs/fix/early_l8entry2.txt"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
START = 12488
MARKS = (130, 200, 330, 460, 600, 800, 1000, 1200)
lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_l8entry2.log", fields=F)
e.load("cap14_f12000")
for i in range(12000, START):
    s = e.step(bt(lines[i]), 1)
root = e.msave()
H0 = s.height | s.hh << 8
out = []
for k in (0, 20, 24, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36):
    e.mload(root)
    seq = [lines[i] for i in range(START, START + 1300)]
    del seq[2:2 + k]
    got, hurt = {}, None
    for j, b in enumerate(seq):
        t = e.step(bt(b), 1)
        H = t.height | t.hh << 8
        if t.hp < 47 or t.lives < s.lives:
            hurt = (j + 1, H - H0)
            break
        for g in MARKS:
            if g not in got and H - H0 >= g and t.z == 0:
                got[g] = j + 1
    out.append(f"drop {k:2d}: standing at +px after frames {got}; first hurt {hurt}")
    print(out[-1], flush=True)
open(LOGS_DIR / "fix" / "early_l8entry2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
e.close()
