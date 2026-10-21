"""Replace the long wait on the top moving platform (0x5d) with a walk Left (2026-10-07).
    python l12toppatch.py <segment> <out> [walk]   -> logs/pbeam_<out>.json (same bookmark), bookmark <out>_end0 (level 13 set-down)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
seg, out = sys.argv[1], sys.argv[2]; WALKS = [int(sys.argv[3])] if len(sys.argv) > 3 else list(range(60, 90, 2))
d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json")); ins = [x.replace(",", "+") for x in d["inputs"]]
# the idle run: >= 100 frames of '' in the last 1200 frames
best = None; i = len(ins) - 1200; run0 = None
for k in range(len(ins) - 1200, len(ins)):
    if ins[k] == "":
        run0 = k if run0 is None else run0
    else:
        if run0 is not None and 100 <= k - run0 <= 160: best = (run0, k)
        run0 = None
print("idle run", best, flush=True)
a, b = best
e = BizHawk(log_name=f"toppatch_{out}.log"); e.load(d["bookmark"])
for x in ins[:a]: e.step(tuple(v for v in x.split("+") if v), 1)
m = e.ram(0, 0x800); print("at", a, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, flush=True)
base = e.msave()
def lvl(): return e.ram(0x10, 1)[0]
e.mload(base); n = a; oldend = None
for x in ins[a:]:
    e.step(tuple(v for v in x.split("+") if v), 1); n += 1
    if lvl() != 5 and oldend is None: oldend = n
print("old level end", oldend, flush=True)
res = []
for walk in WALKS:
    e.mload(base); n = a; end = None; hurt = False
    seq = ["Left"] * walk + ins[b:]
    for x in seq:
        e.step(tuple(v for v in x.split("+") if v), 1); n += 1
        m = e.ram(0, 0x800)
        if m[0x10] == 5 and m[0x51A] < 47: hurt = True; break
        if m[0x10] != 5 and end is None: end = n
    if end and not hurt: res.append((end, walk)); print("walk", walk, "level end", end, flush=True)
res.sort()
if not res: print("no walk works"); sys.exit(1)
end, walk = res[0]
new = ins[:a] + ["Left"] * walk + ins[b:]
new = new[:len(new) - (len(ins) - oldend) ] if oldend else new
json.dump({"bookmark": d["bookmark"], "inputs": new, "note": d.get("note", "") + " Top: walk Left on the moving platform instead of riding it.", "slack": d.get("slack", 0)}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
print(f"{out}: {len(new)} frames (was {len(ins)}), walk {walk}, level end {end} vs {oldend}", flush=True)
e.close()
