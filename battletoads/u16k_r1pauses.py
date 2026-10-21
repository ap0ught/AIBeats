"""Track K: head pauses in a Level 6 segment's room 1 (frames where a snake head exists and does not move), with the toad's
state at that moment.  A toad clinging to a snake or standing at / ahead of its head's coordinate makes the head pause.
    python u16k_r1pauses.py <segment> [to=1992] -> logs/fix/u16k_r1pauses_<segment>.txt"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

seg = sys.argv[1]
to = int(sys.argv[2]) if len(sys.argv) > 2 else 1992
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))["inputs"]
e = BizHawk(log_name="u16k_r1pauses.log")
e.load("L4c5_end0")
prev, out, runs = None, [], []
for n, b in enumerate(ins[:to], 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    hd = [(q, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    if hd and prev and hd[0] == prev:
        x, H, z, an = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x3B5]
        if runs and runs[-1][1] == n - 1:
            runs[-1][1] = n
        else:
            runs.append([n, n, hd[0][1:], (x, H, z, an)])
    prev = hd[0] if hd else None
for a, b, h, t in runs:
    out.append(f"{a}..{b} ({b - a + 1} f): head {h} toad {t}")
single = sum(1 for a, b, h, t in runs if b == a)
out.append(f"{len(runs)} pauses, {single} of them single frames")
open(LOGS_DIR / "fix" / f"u16k_r1pauses_{seg}.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
e.close()
