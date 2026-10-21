"""Track K: room 1, getting onto snake 3's 7984-run WITHOUT touching the rising head (L6c jumps at it at index 1508 and makes
it pause at 1539/1544/1549).  From L6c[:1508] (toad parked at (334,7934) on the snake's lower run): idle w, A x a straight
up (optionally Left/Right taps), then idle: where does the toad end, when does the head reach x 112 (L6c 1714, pause-free
ride 1708), how many pauses.
    python u16k_r1ride2.py -> logs/fix/u16k_r1ride2.txt"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name="u16k_r1ride2.log")
e.load("L4c5_end0")
for b in ins0[:1508]:
    e.step(bt(b), 1)
root = e.msave()
out = []
for w, a in [(w, a) for w in (36, 40, 44, 48, 52, 56, 60) for a in (32, 24)]:
    e.mload(root)
    seq = [""] * w + ["A"] * a + [""] * 260
    prev, pauses, arr, land, tr = None, [], None, None, []
    for j, b in enumerate(seq):
        e.step(bt(b), 1)
        n = 1508 + j + 1
        m = e.ram(0, 0x800)
        x, H, z, hp = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A]
        hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
        if not hd or hp < 47:
            break
        if prev is not None and hd[0] == prev:
            pauses.append(n)
        prev = hd[0]
        if land is None and j > w + 5 and z == 0:
            land = (n, x, H, x - hd[0][0])
        if hd[0][0] == 112 and arr is None and n > 1600:
            arr = n
        if arr and n == arr + 10:
            tr = (x, H, z)
            break
    out.append(f"idle {w} A{a}: lands {land}; head reaches x 112 at {arr}; toad 10 frames later {tr}; pauses at {pauses}")
    print(out[-1], flush=True)
open(LOGS_DIR / "fix" / "u16k_r1ride2.txt", "w").write("\n".join(out) + "\n")
e.close()
