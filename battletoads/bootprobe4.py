"""Big-boot distance probe: from F (after hit 1), idle w, then walk toward the foe until the gap <= G (or 120 f), press dir+B
(dir held 12), record the gap/foe state at the press and the damage.   python bootprobe4.py <F> <bookmark> <b0> <foe hex>"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F, BM, B0, FOE = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4], 16)
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
e = BizHawk(log_name=f"bootprobe4_{F}.log"); e.load(BM)
for b in ins[B0:F]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == FOE: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
def gap(m, f): return (f[0] - (m[0x3FD] | m[0x3EE] << 8) + 256) % 512 - 256
m = e.ram(0, 0x800); print("root", F, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], "spd", m[0x565], "foe", foe(m), flush=True)
big = []
for w in range(0, 100, 4):
    for G in range(8, 48, 3):
        e.mload(root); e.step((), w); m = e.ram(0, 0x800); f0 = foe(m)
        if f0 is None: continue
        t = "Right" if gap(m, f0) >= 0 else "Left"; n = 0
        while n < 120:
            m = e.ram(0, 0x800); f = foe(m)
            if f is None: break
            if abs(gap(m, f)) <= G: break
            e.step((t,), 1); n += 1
        if f is None or abs(gap(m, f)) > G: continue
        press = (n, m[0x565], m[0x3B5], abs(gap(m, f)), f[1] - m[0x439], f[3])
        e.step((t, "B"), 1); e.step((t,), 12)
        hp0 = f[2]; got = None; hurt = False; an = None
        for i in range(60):
            m = e.step((), 1) and e.ram(0, 0x800)
            if m[0x51A] < 47: hurt = True; break
            f = foe(m)
            if f is None: got = 0; break
            if f[2] < hp0: got = f[2]; an = m[0x3B5]; break
        if got is None: continue
        dmg = hp0 - got
        if dmg > 16: big.append((w, G, press, dmg, hurt, an)); print("BIG", (w, G), "press(n,spd,an,gap,dh,foest)", press, "dmg", dmg, "hurt", hurt, "an at hit", an, flush=True)
        elif w % 20 == 0 and G in (8, 20, 32, 44): print("   ", (w, G), press, "dmg", dmg, "an at hit", an, flush=True)
print("BIG count", len(big), flush=True)
e.close()
