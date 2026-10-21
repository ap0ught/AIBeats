"""From the bug-free landing (L9B_down, (915,38)): idle k so the floor's mine train moves on, then walk left to x 796 and join the old L9c
route where it runs through at (796,38) speed 96 (index 8272); oldwalk2 continues it. Scans k, keeps the smallest that walks there unhurt."""
import json, subprocess, sys
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); old = [x.replace(",", "+") for x in seg["inputs"]]
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5], m[0x51A])
e = BizHawk(log_name="l9join3.log"); e.load(seg["bookmark"])
for b in old[:8272]: e.step(tuple(v for v in b.split("+") if v), 1)
ref = key(e.ram(0, 0x800)); print("old 8272:", ref, flush=True)
e.load("L9B_down"); base = e.msave(); found = None
for k in range(0, 300, 4):
    e.mload(base); e.step((), k); ok = True; n = 0
    while n < 140:
        m = e.ram(0, 0x800)
        if m[0x51A] < 47 or m[0x3B5] in (36, 37): ok = False; break
        if (m[0x3FD] | m[0x3EE] << 8) <= 796: break
        e.step(("Left",), 1); n += 1
    s = key(e.ram(0, 0x800))
    if ok and s[1] == 38 and s[2] == 0 and abs(s[3] - ref[3]) <= 8:
        print("k", k, "-> at 796 after", n, "Left frames:", s, flush=True)
        if found is None:
            found = (k, n); e.save("L9B_j0"); json.dump({"bookmark": "L9B_down", "inputs": [""] * k + ["Left"] * n, "old_at": 8272}, open("knowledge/l9_bugjoin.json", "w"))
    elif k % 40 == 0: print("k", k, "->", "hurt/carried" if not ok else s, flush=True)
    if found and k > found[0] + 40: break
e.close()
if found is None: print("no join", flush=True); sys.exit(1)
subprocess.run([sys.executable, "-u", "oldwalk2.py", "L9c", seg["bookmark"], "0", "L9B_j0", "8272", str(len(old)), "o9b"], stdout=sys.stdout, stderr=subprocess.STDOUT)
