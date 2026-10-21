"""After the bug-free descent (L9B_down at (915,38)): walk left to x <= 833 standing, match the old L9c route's state (same h, |dx| <= 8,
on the ground, after index 8200) and walk the old route from there (oldwalk2) to the level end. -> knowledge/ow_o9b.json, OW_o9b"""
import json, subprocess, sys
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); old = [x.replace(",", "+") for x in seg["inputs"]]
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5], m[0x565])
e = BizHawk(log_name="l9rejoin2.log"); e.load("L9B_down"); walk = []
for _ in range(120):
    m = e.ram(0, 0x800)
    if (m[0x3FD] | m[0x3EE] << 8) <= 833 and m[0x475] == 0: break
    e.step(("Left",), 1); walk.append("Left")
n = 0
while e.byte(0x565) and n < 40: e.step((), 1); walk.append(""); n += 1
m = e.ram(0, 0x800); ours = key(m); print("after the walk:", ours, "hp", m[0x51A], "walk", len(walk), flush=True); e.save("L9B_j0")
json.dump({"bookmark": "L9B_down", "inputs": walk}, open("knowledge/l9_bugwalk.json", "w"))
e.load(seg["bookmark"]); best = None
for i, b in enumerate(old[:8420]):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800); f = i + 1
    if f >= 8200:
        k = key(m)
        if k[2] == 0 and k[1] == ours[1] and abs(k[0] - ours[0]) <= 8:
            d = abs(k[0] - ours[0]) + (0 if k[4] == ours[4] else 2)
            if best is None or d < best[0]: best = (d, f, k)
print("best old match:", best, flush=True); e.close()
if best is None: sys.exit(1)
subprocess.run([sys.executable, "-u", "oldwalk2.py", "L9c", seg["bookmark"], "0", "L9B_j0", str(best[1]), str(len(old)), "o9b"], stdout=sys.stdout, stderr=subprocess.STDOUT)
