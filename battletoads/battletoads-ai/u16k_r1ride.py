"""Track K: room 1, the ride on snake 3's 7984-run (index 1571..1712, the head moves left from x 400 to 112).  A toad
standing at or ahead of the head's coordinate makes the head pause (7 lost frames in L6c); two or more px behind it there
are no pauses.  Variants of L6c's 'idle 5, Left x8' after index 1571: idle i0, Left x k -> index at which the head
reaches x 112, the toad's x there, the number of head pauses.
    python u16k_r1ride.py -> logs/fix/u16k_r1ride.txt"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name="u16k_r1ride.log")
e.load("L4c5_end0")
for b in ins0[:1571]:
    e.step(bt(b), 1)
root = e.msave()
out = []
for i0, k in [(5, 8), (5, 0), (5, 2), (5, 4), (5, 5), (5, 6), (5, 7), (0, 0), (0, 4), (9, 4), (12, 4), (16, 4), (9, 6), (12, 6)]:
    e.mload(root)
    seq = [""] * i0 + ["Left"] * k + [""] * 200
    prev, pauses, arr, tr = None, 0, None, []
    for j, b in enumerate(seq):
        e.step(bt(b), 1)
        n = 1571 + j + 1
        m = e.ram(0, 0x800)
        x, H, z = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475]
        hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
        if not hd:
            break
        hx = hd[0][0]
        if prev is not None and hx == prev and hx > 112:
            pauses += 1
        prev = hx
        if n in (1600, 1640, 1680):
            tr.append(f"{n}:{x - hx:+d}")
        if hx == 112 and arr is None and n > 1600:
            arr = (n, x, H, z)
        if arr and n == arr[0] + 12:
            arr = arr + ((x, H, z),)
            break
    out.append(f"idle {i0} Left x{k}: head reaches x 112 at {arr[0] if arr else None} (L6c 1714); toad then {arr[1:] if arr else None}; pauses {pauses}; toad-head {' '.join(tr)}")
    print(out[-1], flush=True)
open(LOGS_DIR / "fix" / "u16k_r1ride.txt", "w").write("\n".join(out) + "\n")
e.close()
