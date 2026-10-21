"""u16b: print the Level 8 -> 9 transition of a built segment frame by frame (level byte, timers, dice, pad), then the first frames of
the next segment behind it against that segment's own reference.   python u16b_tailprobe.py <segment> [next segment=L9heli_c2] [last N=75]"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt
SEG = sys.argv[1]
NXT = sys.argv[2] if len(sys.argv) > 2 else "L9heli_c2"
N = int(sys.argv[3]) if len(sys.argv) > 3 else 75
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json")); nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
e = BizHawk(log_name=f"u16b_tailprobe_{SEG}.log")
e.load(nj["bookmark"]); ref = [e.ram(0, 0x800)]
for b in nj["inputs"][:40]:
    e.step(bt(b), 1); ref.append(e.ram(0, 0x800))
e.load(sj["bookmark"])
ins = sj["inputs"]
for i, b in enumerate(ins):
    e.step(bt(b), 1)
    if i >= len(ins) - N:
        m = e.ram(0, 0x800)
        print(i + 1, repr(b), "lv", m[0x10], "t", m[0x0B], m[0x0C], "hp", m[0x51A], "x", m[0x3FD] | m[0x3EE] << 8, "rng", m[0x25], m[0x26], m[0x27], m[0x28], "pad", m[0x2B], m[0x2C])
m = e.ram(0, 0x800)
print("end vs reference entry:", [hex(a) for a in range(0x800) if m[a] != ref[0][a] and not 0x100 <= a < 0x200][:20])
for j, b in enumerate(nj["inputs"][:40]):
    e.step(bt(b), 1); m = e.ram(0, 0x800)
    d = [hex(a) for a in range(0x800) if m[a] != ref[j + 1][a] and not 0x100 <= a < 0x200]
    print("next", j + 1, repr(b), "t", m[0x0B], m[0x0C], "rng", m[0x25], m[0x26], m[0x27], m[0x28], "ref rng", ref[j + 1][0x25], ref[j + 1][0x26], ref[j + 1][0x27], ref[j + 1][0x28], "diff", len(d), d[:10])
e.close()
