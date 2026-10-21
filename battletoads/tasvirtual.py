"""A segment with one stretch replaced by the TAS's own inputs (2026-10-03): old[:a] + TAS inputs[k0:k1] + old[b:].
The TAS stretch is referenced against the FCEUX log (rows tasrow+1 ..); rngfit.py then re-rolls the dice until the
enemies do what they did for the TAS. a must be a frame where our toad matches log row `tasrow` (x, h, z).
    python tasvirtual.py <segment> <out> <a> <b> <k0> <k1> <tasrow>"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
seg, out, a, b, k0, k1, row = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8])
pre = int(sys.argv[8]) if len(sys.argv) > 8 else 0
d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json")); old = [x.replace(",", "+") for x in d["inputs"]]
tas = json.load(open("knowledge/tas1p_l12_inputs.json"))
e = BizHawk(log_name=f"tasvirtual_{out}.log"); e.load(d["bookmark"])
for i, x in enumerate(old[:b]):
    if i == b: break
    e.step(tuple(v for v in x.split("+") if v), 1)
e.save(f"{out}_at{b}")
e.close()
inputs = old[:a] + [""] * pre + [x.replace(",", "+") for x in tas[k0:k1]] + old[b:]
parts = [{"bookmark": d["bookmark"], "n": a}, {"tasrow": row, "taslog": "tas/watch_1p_l12.txt", "n": k1 - k0 + pre, "pre": pre, "level": 5},
         {"bookmark": f"{out}_at{b}", "n": len(old) - b}]
json.dump({"bookmark": d["bookmark"], "inputs": inputs, "parts": parts, "note": d.get("note", "")}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
print(f"{out}: {len(inputs)} frames (old {len(old)}): TAS inputs {k0}..{k1} replace old {a}..{b} (saves {(b - a) - (k1 - k0) - pre})")
