"""Probe 4: why does the 1-player TAS run under the bugs untouched (TAS 59328-59340) while our toad is grabbed at x 822?
Our line: L9c 7818 + hold Right (grab at +22).  Dump our RAM per frame and diff against the TAS's RAM (FCEUX dump
logs/fix/heli_tas1p_ram.txt) on the frames where the toad's x and h agree."""
import json
from l9heli_fix_lib import *
tas = {}
for l in open(LOGS_DIR / "fix" / "heli_tas1p_ram.txt"):
    p = l.split()
    tas[int(p[0][1:])] = (p[1], bytes.fromhex(p[2]))
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p4.log")
e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + 7818): e.step(bt(ins[f]), 1)
ours = []
for i in range(30):
    e.step(("Right",), 1); ours.append(e.ram(0, 0x800))
e.close()
json.dump([m.hex() for m in ours], open(LOGS_DIR / "fix" / "heli_p4_ours.json", "w"))
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475])
tk = {}
for t, (b, m) in tas.items():
    if 59290 <= t <= 59345: tk.setdefault(key(m), t)
IGN = set(range(0x100, 0x200)) | set(range(0x200, 0x300)) | set(range(0x700, 0x800))   # stack, OAM, sound
for i, m in enumerate(ours):
    k = key(m); t = tk.get(k)
    print(i + 1, "ours", tstr(m), "| TAS frame", t, flush=True)
    if t:
        tm = tas[t][1]
        d = [(a, m[a], tm[a]) for a in range(0x800) if m[a] != tm[a] and a not in IGN]
        print("   diff bytes (addr ours tas):", " ".join(f"{a:03x}:{x}/{y}" for a, x, y in d), flush=True)
