"""L12h DEBUG probe (poke on a snapshot, not a run): does the queen fight L13y0 replay identically from L12g_end0 when only the slow timer
byte $0C differs by 128 (= The Revolution 256 ticks shorter)? Also tries $0B/$0C shifted by other amounts for reference."""
import json, sys
from l12h_lib import *
d = json.load(open(LOGS_DIR / "pbeam_L13y0.json")); ins = [x.replace(",", "+") for x in d["inputs"]]
e = BizHawk(log_name="fix_l12h_q0c.log")
def play(pokes):
    e.load("L12g_end0")
    m = e.ram(0, 0x800); t0 = (m[0x0B], m[0x0C])
    for a, v in pokes(m).items(): e.poke(a, v)
    ctr = []; left = None; hp = None
    for i, b in enumerate(ins):
        e.step(bt(b), 1)
        if i % 100 == 99 or i == len(ins) - 1:
            m = e.ram(0, 0x800); ctr.append(m[0x586]); hp = m[0x51A]
        if left is None and e.byte(0x10) != 13: left = i + 1
    m = e.ram(0, 0x800)
    return t0, ctr, left, m[0x10], hp
print("base      ", play(lambda m: {}), flush=True)
print("$0C ^ 0x80", play(lambda m: {0x0C: m[0x0C] ^ 0x80}), flush=True)
print("$0B+2,$0C+1", play(lambda m: {0x0B: (m[0x0B] + 2) & 255, 0x0C: (m[0x0C] + 1) & 255}), flush=True)
e.close()
