"""After the sixth-Hornhead skip (2026-10-03): the TAS lands on the sinking platform at 2284, holds Left+Right for
12 frames (standing still while keeping the run state) and dash-jumps with the platform's spring at 2299 up to the
(431,246) ledge, landing at 2338, then 2346 at (454,30). Legal stand-in: idle / a step back, double-tap, release,
Right+A - scanned so that one of the TAS's mid-air frames 2300..2337 is matched exactly; then its inputs to 2346.
    python l12h6b.py  -> knowledge/l12_h6b.json (inputs from H6_j2284), bookmark H6_j2346"""
import json, resync
from toads.emulator import BizHawk
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
e = BizHawk(log_name="h6b.log"); e.load("H6_j2284"); root = e.msave()
m = e.ram(0, 0x800)
print("at 2284:", (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5], m[0x565]), "camy", m[0x89] | m[0x8A] << 8, "(TAS 4096)",
      [(hex(m[0x3C1+q]), m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q]) for q in range(2, 15) if m[0x3C1+q]], flush=True)
idx = {rows[j][1:5]: j for j in range(2300, 2338)}
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
best = None
for a in range(0, 14):
    for back in range(0, 5):
        for tap in ("|Right||Right|", "|Right|||Right|", "||Right||Right|", "Right||Right|", "Right|||Right|"):
            for k in range(16, 28, 2):
                e.mload(root); seq = []
                def st(b):
                    e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); return e.ram(0, 0x800)
                for _ in range(a): st("")
                for _ in range(back): st("Left")
                for b in tap.split("|"): st(b)
                hit = None
                for i in range(k + 45):
                    m = st("Right+A" if i < k else "Right")
                    if m[0x51A] < 47 or m[0x11] < 6 or (m[0x475] == 0 and i > 8): break
                    j = idx.get(key(m))
                    if j: hit = j; break
                if not hit: continue
                for s in range(hit + 1, 2347): m = st(TAS[s])
                plat = sorted((m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q]) for q in range(2, 15) if m[0x3C1+q] == 0x36)
                ok = key(m) == rows[2346][1:5] and m[0x51A] == 47 and m[0x11] == 6
                print(f"a {a} back {back} {tap} A {k}: match TAS {hit} after {len(seq) - (2346 - hit)} frames -> end {key(m)} plat {plat} camy {m[0x89] | m[0x8A] << 8} {'OK' if ok else ''}", flush=True)
                if ok and (best is None or len(seq) < len(best)):
                    best = list(seq)
                    json.dump({"bookmark": "H6_j2284", "j0": 2284, "jend": 2346, "inputs": best}, open("knowledge/l12_h6b.json", "w"))
                    e.mload(root)
                    for b in best: e.step(tuple(v for v in b.split("+") if v), 1)
                    e.save("H6_j2346")
                    print(f"SAVED {len(best)} frames (TAS 2284->2346 took 62)", flush=True)
e.close()
