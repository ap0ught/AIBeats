"""Big-boot condition probe: for (w, n) print the toad's speed/anim at the B press and the damage dealt.
    python bootprobe2.py <F> <bookmark> <b0> <foe hex>"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F, BM, B0, FOE = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4], 16)
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
e = BizHawk(log_name=f"bootprobe2_{F}.log"); e.load(BM)
for b in ins[B0:F]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == FOE: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
m = e.ram(0, 0x800); print("root", F, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], "spd", m[0x565], "foe", foe(m), flush=True)
rows = []
for w in range(0, 44, 4):
    for n in range(20, 46, 2):
        e.mload(root); e.step((), w); m = e.ram(0, 0x800); f0 = foe(m)
        if f0 is None: continue
        tx = m[0x3FD] | m[0x3EE] << 8; d = (f0[0] - tx + 256) % 512 - 256; t = "Right" if d >= 0 else "Left"
        spds = []
        for i in range(n):
            e.step((t,), 1); mm = e.ram(0, 0x800); spds.append(mm[0x565])
        m = e.ram(0, 0x800); press = (m[0x565], m[0x3B5], m[0x3FD] | m[0x3EE] << 8, m[0x439]); fp = foe(m)
        e.step((t, "B"), 1); e.step((t,), 12)
        hp0 = f0[2]; got = None; hurt = False
        for i in range(70):
            m = e.step((), 1) and e.ram(0, 0x800)
            if m[0x51A] < 47: hurt = True; break
            f = foe(m)
            if f is None: got = 0; break
            if f[2] < hp0: got = f[2]; break
        rows.append((w, n, press, fp, None if got is None else hp0 - got, hurt))
for r in rows:
    if r[4] is not None: print(r, flush=True)
print("max speed seen per n:", flush=True)
e.close()
