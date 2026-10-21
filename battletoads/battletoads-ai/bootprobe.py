"""Mechanics probe (snapshots only): does a walking direction+B boot with the direction HELD after the press do big damage?
From L12p_f6000 replay L12r's inputs to frame F (after hit 1 on the wide-platform Hornhead, hp 47), then for each
(wait w, walk n, hold k): idle w, walk toward n frames, dir+B 1 frame, dir held k frames, idle; record the foe's hp over 80 frames.
    python bootprobe.py [F=6240]
"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F = int(sys.argv[1]) if len(sys.argv) > 1 else 6240
BM = sys.argv[2] if len(sys.argv) > 2 else "L12p_f6000"
B0 = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
FOE = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x5c
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
e = BizHawk(log_name=f"bootprobe_{F}.log"); e.load(BM)
for b in ins[B0:F]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == FOE: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
    return None
m = e.ram(0, 0x800); HP0 = foe(m)[2] if foe(m) else 0; print("root", F, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], "hp", m[0x51A], "foe", foe(m), flush=True)
res = {}
for w in range(0, 120, 4):
    for n in (0, 4, 8, 16, 24, 34):
        for k in (0, 12, 24):
            e.mload(root)
            e.step((), w); m = e.ram(0, 0x800); f0 = foe(m)
            if f0 is None: continue
            tx = m[0x3FD] | m[0x3EE] << 8
            d = (f0[0] - tx + 256) % 512 - 256
            t = "Right" if d >= 0 else "Left"
            e.step((t,), n); e.step((t, "B"), 1); e.step((t,), k)
            hp0 = f0[2]; hurt = False; got = None; an = None
            for i in range(80):
                m = e.step((), 1) and e.ram(0, 0x800)
                if m[0x51A] < 47: hurt = True; break
                f = foe(m)
                if f is None: got = 0; break
                if f[2] < hp0: got = f[2]; an = m[0x3B5]; break
            if got is not None:
                res[(w, n, k)] = (got, hurt, an)
                if got < hp0 - 16: print("BIG", (w, n, k), "hp", hp0, "->", got, "hurt", hurt, "foe", f0, flush=True)
print("hits found", len(res), "damage values", sorted({hp0 - g for g, _, _ in res.values()} if res else []), flush=True)
dmg = {}
for key, (g, hurt, an) in res.items(): dmg.setdefault(HP0 - g, []).append(key)
for d_, keys in sorted(dmg.items()): print("damage", d_, "count", len(keys), "e.g.", keys[:6], flush=True)
e.close()
