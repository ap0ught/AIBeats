"""The wide-platform Hornhead by the big boot (2026-10-06): old inputs to F, then idle w, walk toward n, dir+B, dir k; idle till it is gone.
    python l12boot.py <F> <w> <n> <k> <out>  -> knowledge/l12_boot_<out>.json {a: 6184, kill, inputs (from 6184)}, bookmark BOOT_<out> (foe gone)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F, w, n, k, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
e = BizHawk(log_name=f"l12boot_{out}.log"); e.load("L12p_f6000")
for b in ins[6000:F]: e.step(tuple(v for v in b.split("+") if v), 1)
new = list(ins[6184:F])
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x5c: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
def st(b, c=1):
    for _ in range(c): e.step(tuple(v for v in b.split("+") if v), 1); new.append(b)
    return e.ram(0, 0x800)
m = st("", w); f0 = foe(m); tx = m[0x3FD] | m[0x3EE] << 8
t = "Right" if (f0[0] - tx + 256) % 512 - 256 >= 0 else "Left"
st(t, n); st(t + "+B", 1); m = st(t, k)
kill = None
for i in range(200):
    m = st("")
    f = foe(m)
    if f and f[2] == 0 and kill is None: kill = 6184 + len(new); print("hp 0 at", kill, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], flush=True)
    if f is None: break
gone = 6184 + len(new)
print("foe gone at", gone, "(old kill 6423, gone 6461) toad x", m[0x3FD] | m[0x3EE] << 8, "h", m[0x439], "z", m[0x475], "an", m[0x3B5], "spd", m[0x565], "hp", m[0x51A], "0B", m[0x0B], flush=True)
e.save(f"BOOT_{out}")
json.dump({"a": 6184, "kill": kill, "gone": gone, "inputs": new}, open(f"knowledge/l12_boot_{out}.json", "w"))
e.close()
