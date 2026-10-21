"""u16b: alignment census of a built Level 8's tail - which (wait before the mash, first mash button) variants reach Terra Tubes with which
CPU alignment (PC, timestamp, frame parity), and which of them merge with the old Level 9.
    python u16b_census.py <built segment> [next=L9heli_c2] [waits lo:hi = 280:320]
Prints one line per variant and a table alignment -> outcome.  Read-only."""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, FIX, write_json
from u16b_phase import sig as _core
SEG = sys.argv[1]
NXT = sys.argv[2] if len(sys.argv) > 2 else "L9heli_c2"
LO, HI = (int(v) for v in (sys.argv[3] if len(sys.argv) > 3 else "280:320").split(":"))
NA, SKIP = 240, 7
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json")); nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]; nxt = [b.replace(",", "+") for b in nj["inputs"]]
T0 = sj["kill_frame"] - 12483
e = BizHawk(log_name=f"u16b_census_{SEG}.log", fields={"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11})
cut = lambda m: m[:0x100] + m[0x200:]
def phase():
    c = _core(e, "u16b_phase_census_" + SEG)
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1
e.load(nj["bookmark"]); PH0 = phase(); REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1); REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
e.load(sj["bookmark"])
for b in seg[:T0]:
    e.step(bt(b), 1)
base = e.msave()
SEEN, rows = {}, []
for wait in range(LO, HI + 1):
    for first in ("A", "B"):
        e.mload(base)
        pat, stage, ins = ([first, "B" if first == "A" else "A"]), 0, []
        for j in range(wait + 900):
            b = "" if j < wait else pat[(j - wait) % 2]
            s = e.step(bt(b), 1); ins.append(b)
            if stage == 0 and s.level == 11: stage = 1
            if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0: stage = 2
            if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0: break
        ph = phase(); key = (ph, cut(e.ram(0, 0x800)))
        if key not in SEEN:
            same = 0
            for j in range(NA):
                e.step(bt(nxt[j]), 1)
                if j < SKIP: continue
                if cut(e.ram(0, 0x800)) != REF[j]: break
                same += 1
            if same == NA - SKIP and phase() != PHN: same = -1
            SEEN[key] = same
        ln = T0 + len(ins)
        rows.append((ln, wait, first, ph[0], ph[1], ph[3] == PH0[3], SEEN[key]))
        print(f"wait {wait} first {first}: segment {ln}; alignment PC ${ph[0]:04X} ts {ph[1]} {'same parity' if ph[3] == PH0[3] else 'ODD shift'}; identical {SEEN[key]}/{NA - SKIP}{'  MERGED' if SEEN[key] == NA - SKIP else ''}", flush=True)
print("reference alignment: PC $%04X ts %d" % PH0[:2])
write_json(FIX / f"u16b_census_{SEG}.json", {"rows": rows})
e.close()
