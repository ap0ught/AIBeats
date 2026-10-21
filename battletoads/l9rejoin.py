"""After the corridor (2026-10-04): replay L9T_770 + 2 idle + the beam piece (knowledge/l4s_L9T_770.json) -> bookmark L9T_exit; find the
old L9m frame j0 whose state matches ours (same h low byte, |dx| <= 8, on the ground) after 8880; then oldwalk2 the old route to the end.
    python l9rejoin.py  -> knowledge/ow_o9a.json, bookmark OW_o9a"""
import json, subprocess, sys
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9m.json")); old = [x.replace(",", "+") for x in seg["inputs"]]
piece = json.load(open("knowledge/l4s_L9T_770.json"))
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5], m[0x565])
e = BizHawk(log_name="l9rejoin.log"); e.load("L9T_770"); e.step((), 2)
for b in piece: e.step(tuple(v for v in b.split("+") if v), 1)
m = e.ram(0, 0x800); ours = key(m); print("our exit state:", ours, "hp", m[0x51A], "cam", m[0x87] | m[0x88] << 8, flush=True); e.save("L9T_exit")
e.load(seg["bookmark"]); best = None
for i, b in enumerate(old[:9400]):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800); f = i + 1
    if f >= 8880:
        k = key(m)
        if k[2] == 0 and k[1] == ours[1] and abs(k[0] - ours[0]) <= 8:
            d = abs(k[0] - ours[0]) + (0 if k[4] == ours[4] else 3)
            if best is None or d < best[0]: best = (d, f, k)
print("best old match:", best, flush=True)
if best is None: sys.exit(1)
j0 = best[1]
subprocess.run([sys.executable, "-u", "oldwalk2.py", "L9m", seg["bookmark"], "0", "L9T_exit", str(j0), str(len(old)), "o9a"], stdout=sys.stdout, stderr=subprocess.STDOUT)
e.close()
