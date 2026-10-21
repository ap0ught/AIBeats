"""Boot-boot probe: from F (before the first hit), idle w, hold dir toward the foe n1 frames (a run), dir+B, hold n2, dir+B, hold 12.
Records the foe's hp after each blow.   python bootprobe3.py <F> <bookmark> <b0> <foe hex> [wmax]"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F, BM, B0, FOE = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4], 16)
WMAX = int(sys.argv[5]) if len(sys.argv) > 5 else 36
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
e = BizHawk(log_name=f"bootprobe3_{F}.log"); e.load(BM)
for b in ins[B0:F]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == FOE: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
m = e.ram(0, 0x800); print("root", F, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], "spd", m[0x565], "foe", foe(m), flush=True)
best = None
for w in range(0, WMAX + 1, 6):
    for n1 in (20, 26, 32, 38, 44):
        for n2 in (0, 6, 12, 18, 24, 30, 36, 44, 52):
            e.mload(root); e.step((), w); m = e.ram(0, 0x800); f0 = foe(m)
            if f0 is None: continue
            tx = m[0x3FD] | m[0x3EE] << 8; d = (f0[0] - tx + 256) % 512 - 256; t = "Right" if d >= 0 else "Left"
            e.step((t,), n1); m = e.ram(0, 0x800); sp1 = m[0x565]
            e.step((t, "B"), 1); e.step((t,), n2); m = e.ram(0, 0x800); sp2 = m[0x565]; f1 = foe(m)
            e.step((t, "B"), 1); e.step((t,), 12)
            hurt = False; hps = []; gone = None
            for i in range(80):
                m = e.step((), 1) and e.ram(0, 0x800)
                if m[0x51A] < 47: hurt = True; break
                f = foe(m)
                if f is None: gone = i; break
                if not hps or f[2] != hps[-1]: hps.append(f[2])
            tot = w + n1 + 1 + n2 + 1 + 12 + (gone if gone is not None else 80)
            row = (w, n1, n2, sp1, sp2, f1[2] if f1 else None, hps, gone, hurt, tot)
            if gone is not None and not hurt:
                print("KILL", row, flush=True)
                if best is None or tot < best[-1]: best = row
            elif hps and hps[-1] <= (f0[2] - 32):
                print("two hits", row, flush=True)
print("best kill", best, flush=True)
e.close()
