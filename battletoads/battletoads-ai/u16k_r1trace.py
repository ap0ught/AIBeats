"""Track K: trace of L6c's room 1 ending (from the bookmark): toad and snake heads per frame -> logs/fix/u16k_r1trace.txt
Also saves states/u16k_r1_<n>.State at the given segment indices (roots for room-1 probes; bookmark replay).
    python u16k_r1trace.py [from=1480] [save indices ...]"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
f0 = int(sys.argv[1]) if len(sys.argv) > 1 else 1480
saves = [int(a) for a in sys.argv[2:]]
e = BizHawk(log_name="u16k_r1trace.log")
e.load("L4c5_end0")
out = []
for n, b in enumerate(ins[:2030], 1):
    e.step(bt(b), 1)
    if n in saves:
        e.save(f"u16k_r1_{n}")
    if n >= f0:
        m = e.ram(0, 0x800)
        heads = [(q, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
        others = sorted(set(m[0x3C1 + q] for q in range(1, 15) if m[0x3C1 + q] not in (0, 0x4C, 0x4D)))
        vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
        out.append(f"{n} {b or '-':8s} toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439] | m[0x42A] << 8} z{m[0x475]} a{m[0x3B5]} s{m[0x565]} v{vy:.1f} lv{m[0x10]} | heads {heads} | other ids {[hex(o) for o in others]}")
open(LOGS_DIR / "fix" / "u16k_r1trace.txt", "w").write("\n".join(out) + "\n")
print(len(out), "rows")
e.close()
