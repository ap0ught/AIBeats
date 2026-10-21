"""Compare the first corridor mine's own data: ours (slot 7 after the join) vs the old run's (slot 4), frame by frame from its spawn (old 8432)
to the hit (8574).  Prints the attributes that differ and a few sample rows."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BASES = list(range(0x3C1, 0x5EC, 15))
e = BizHawk(log_name="l9heli_fix_p11.log"); e.load(sys.argv[1])
diffs = {}
for k in range(8279, 8580):
    e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k]); idx = k + 1
    if idx < 8432: continue
    qa = [q for q in range(2, 15) if m[0x3C1 + q] == 0x72 and (m[0x42A + q]) == 23]
    qb = [q for q in range(2, 15) if ref[0x3C1 + q] == 0x72 and (ref[0x42A + q]) == 23]
    if not qa or not qb: 
        if idx % 20 == 0: print(idx, "mine missing", qa, qb)
        continue
    qa, qb = qa[0], qb[0]
    ca = [m[b + qa] for b in BASES]; cb = [ref[b + qb] for b in BASES]
    d = [(hex(b), x, y) for b, x, y in zip(BASES, ca, cb) if x != y]
    for b, x, y in d: diffs.setdefault(b, []).append((idx, x, y))
    if idx in (8432, 8433, 8440, 8500, 8560, 8570, 8572, 8573, 8574) or (d and len(diffs) < 3 and idx % 10 == 0):
        print(idx, "ours slot", qa, "old slot", qb, "toad ours", m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, "hp", m[0x51A], "| mine ours x", m[0x3FD + qa] | m[0x3EE + qa] << 8, "h", m[0x439 + qa], "old x", ref[0x3FD + qb] | ref[0x3EE + qb] << 8, "h", ref[0x439 + qb], "| diffs", d, flush=True)
print("attributes that ever differ:", {b: (len(v), v[:3]) for b, v in diffs.items()})
e.close()
