"""Compose the rebuilt Level 12 (2026-10-04): the continuous chain from L12_start (old L12a[:1802] + the TAS-walk
pieces) + the old L12w remainder from the old frame whose landing equals the TAS landing we reach, as a two-part
segment for rngfit (part 1 replayed from L12_start, part 2 from L12w_at<old>).
    python l12compose.py <tasrun out e.g. R5> <TAS landing j> <old L12w frame> [extra piece json...]
      -> logs/pbeam_L12y.json {bookmark: L12_start, inputs, parts}; then
         RNGFIT_IDS=5c,62 python rngfit.py L12y L11n_end0 L12z   (entry wait 0; the briefing mash at the end)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
def J(p):
    d = json.load(open(p)); return d["inputs"] if isinstance(d, dict) else d
out, jl, oldf = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
part1 = J(LOGS_DIR / "pbeam_L12x_part.json") + J(LOGS_DIR / "pbeam_L12bw4.json") + J("knowledge/l12_bwkill.json") + J("knowledge/l12_bwl.json") + J("knowledge/l12_gp1.json") + J("knowledge/l12_gp2.json") + J(f"knowledge/tasrun_{out}.json")
for p in sys.argv[4:]: part1 += J(p)
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
part2 = old[oldf:]
e = BizHawk(log_name="compose.log"); e.load("L12_start")
for b in part1: e.step(tuple(v for v in b.split("+") if v), 1)
m = e.ram(0, 0x800); e.save("L12y_join")
e2 = BizHawk(log_name="compose2.log"); e2.load(f"L12w_at{oldf}"); m2 = e2.ram(0, 0x800)
k = lambda m: (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
print(f"part 1: {len(part1)} frames -> {k(m)} ; old L12w at {oldf}: {k(m2)} ; camy {m[0x89] | m[0x8A] << 8} vs {m2[0x89] | m2[0x8A] << 8}; 0B {m[0x0B]} vs {m2[0x0B]}", flush=True)
print("objects ours:", [(hex(m[0x3C1+q]), m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q]) for q in range(2, 15) if m[0x3C1+q]])
print("objects old :", [(hex(m2[0x3C1+q]), m2[0x3FD+q] | m2[0x3EE+q] << 8, m2[0x439+q]) for q in range(2, 15) if m2[0x3C1+q]])
json.dump({"bookmark": "L12_start", "inputs": part1 + part2, "parts": [{"bookmark": "L12_start", "n": len(part1)}, {"bookmark": f"L12w_at{oldf}", "n": len(part2)}],
           "note": w.get("note", "")}, open(LOGS_DIR / "pbeam_L12y.json", "w"))
print(f"L12y: {len(part1) + len(part2)} frames (L12w was {len(old)}; saves {len(old) - len(part1) - len(part2)} before the fit)")
e.close(); e2.close()
