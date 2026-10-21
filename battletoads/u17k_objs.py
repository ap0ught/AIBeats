"""Track K2: all object slots (id, x, H) per frame for a script. python u17k_objs.py <tag> <n0> "<spec>" <from> <to> [every]"""
import sys
from u17k_lib import *
tag, n0, spec, f0, f1 = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
every = int(sys.argv[6]) if len(sys.argv) > 6 else 1
ins = seg("K6")[:n0] + parse(spec)
ins += [""] * max(0, f1 - len(ins))
e = BizHawk(log_name=f"u17k_objs_{tag}.log")
e.load("B4_end0")
out = []
prev = None
for n, b in enumerate(ins[:f1], 1):
    e.step(bt(b), 1)
    if n >= f0:
        m = e.ram(0, 0x800)
        ob = [(q, hex(m[0x3C1 + q]), m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q]]
        key = tuple(ob)
        if (n - f0) % every == 0 or (prev is not None and [o[:2] for o in ob] != [o[:2] for o in prev]):
            out.append(f"{n} toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439] | m[0x42A] << 8} | {ob}")
        prev = ob
open(FIX / f"u17k_objs_{tag}.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
e.close()
