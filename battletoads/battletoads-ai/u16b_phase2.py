"""u16b: the CPU alignment frame by frame over a stretch of a segment.   python u16b_phase2.py <segment> <from index> <count> [tag]
Per frame: input, level byte, level timer, health, timestamp (1/15 CPU clocks; mod 15 = the sub-cycle class), PC, frame-count parity."""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt
from u16b_phase import sig
SEG, I0, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tag = sys.argv[4] if len(sys.argv) > 4 else SEG
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json")); ins = [b.replace(",", "+") for b in sj["inputs"]]
if I0 < 0: I0 += len(ins)
e = BizHawk(log_name=f"u16b_phase2_{tag}.log")
e.load(sj["bookmark"])
for b in ins[:I0]:
    e.step(bt(b), 1)
for i in range(I0, min(I0 + N, len(ins))):
    e.step(bt(ins[i]), 1)
    c = sig(e, "u16b_phase2_" + tag); m = e.ram(0, 0x800)
    ts = c[4] | c[5] << 8
    print(i + 1, repr(ins[i]), "lv", m[0x10], "t", m[0x0B], "hp", m[0x51A], "ts", ts, "mod15", ts % 15, "PC $%04X" % (c[12] | c[13] << 8), "par", c[8] & 1, "ppu2001?", "", flush=True)
e.close()
