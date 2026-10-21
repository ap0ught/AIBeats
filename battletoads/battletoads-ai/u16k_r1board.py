"""Track K: room 1, boarding the head of snake 3 on its top run (H 8048, toad stands at 8062).  Root L6c[:1708] (toad parked at
(126,7998) beside the vertical body at x 112).  Idle w0, hold A for a1 frames (grab the body, cling jump), optional
Right from frame d on; report the first frame the toad stands at H 8062 and its x relative to the head.
    python u16k_r1board.py -> logs/fix/u16k_r1board.txt"""
import itertools, json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name="u16k_r1board.log")
e.load("L4c5_end0")
for b in ins0[:1708]:
    e.step(bt(b), 1)
root = e.msave()
out, rows = [], []
for w0, a1, rt in itertools.product((14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34), (4, 8, 12, 16, 20, 24, 28, 32, 40), (0, 1)):
    e.mload(root)
    seq = [""] * w0 + ["A"] * a1 + [""] * 80
    land, run = None, 0
    for i, b in enumerate(seq):
        if rt and i >= w0 + a1:
            b = "Right"
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        x, H, z, hp = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A]
        hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
        if hp < 47:
            land = ("HURT", 1708 + i + 1)
            break
        run = run + 1 if (i > w0 + 3 and z == 0) else 0
        if run >= 4:
            land = (1708 + i + 1 - 3, x, H, (x - hd[0][0]) if hd else None)
            break
    line = f"idle {w0} A{a1} {'then Right' if rt else ''}: stands {land}"
    out.append(line)
    if land and land[0] != "HURT" and land[2] == 8062:
        rows.append((land[0], line))
rows.sort()
print("\n".join(l for _, l in rows[:14]))
open(LOGS_DIR / "fix" / "u16k_r1board.txt", "w").write("\n".join(out) + "\n")
e.close()
