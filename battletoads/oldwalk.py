"""Walk the OLD route's inputs from our state through timed platforms (2026-10-04): like waitwalk.py but the
reference is the old run (replayed from L12w_at6705): at every old landing scan the standing wait (0..260) before
the old inputs and keep the smallest that makes the next landing (within 10 frames / 8 px).
    python oldwalk.py <our bookmark at old frame j0> <j0> <jstop> <out>  -> knowledge/ow_<out>.json, bookmark OW_<out>"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
bm, j0, jstop, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
e2 = BizHawk(log_name=f"oldwalk_ref_{out}.log"); e2.load("L12w_at6705"); rows = {}; lands = []; pz = 0
for i, b in enumerate(old[6705:jstop]):
    e2.step(tuple(v for v in b.split("+") if v), 1); m2 = e2.ram(0, 0x800); f = 6705 + i + 1; rows[f] = key(m2)
    if m2[0x475] == 0 and pz > 0 and f > j0: lands.append(f)
    pz = m2[0x475]
e2.close(); print(len(lands), "old landings after", j0, flush=True)
e = BizHawk(log_name=f"oldwalk_{out}.log"); e.load(bm); cur = e.msave(); inputs = []; j = j0
while True:
    nxt = [l for l in lands if l > j]
    if not nxt: print("no landing ahead of", j, flush=True); break
    j1 = nxt[0]; found = None
    lead = 0
    while j + lead < j1 and old[j + lead] == "": lead += 1                 # the old route's leading idle frames here (a hang, a stand): all of them may be dropped
    for wv in list(range(-(lead - lead % 2), 0, 2)) + list(range(0, 262, 2)):          # negative: DROP that many of the old route's leading idle frames (e.g. jump 2 frames earlier off a moving platform)
        e.mload(cur); e.step((), max(wv, 0)); seq = [""] * max(wv, 0); hit = None
        for s in range(j - min(wv, 0), j1 + 12):
            e.step(tuple(v for v in old[s].split("+") if v), 1); seq.append(old[s]); m = e.ram(0, 0x800); k = key(m)
            if m[0x51A] < 47 or m[0x11] < 4: break
            if s + 1 >= j1 - 10 and k[2] == 0 and abs(k[1] - rows[j1][1]) <= 1 and abs(k[0] - rows[j1][0]) <= 8: hit = (s + 1, k); break
        if hit: found = (wv, seq, hit); break
    if not found: print(f"STUCK: no wait reaches old landing {j1} from {j}", flush=True); break
    wv, seq, hit = found; inputs += seq; j = j1
    e.mload(cur); [e.step(tuple(v for v in b.split("+") if v), 1) for b in seq]; e.mfree(cur); cur = e.msave()
    print(f"old landing {j1} reached (ours {hit[1][:3]}, old {rows[j1][:3]}) with wait {wv}; {len(inputs)} frames (old {j1 - j0})", flush=True)
    json.dump({"bookmark": bm, "inputs": inputs, "old_at": j}, open(f"knowledge/ow_{out}.json", "w"))
e.mload(cur); e.save(f"OW_{out}"); json.dump({"bookmark": bm, "inputs": inputs, "old_at": j}, open(f"knowledge/ow_{out}.json", "w"))
print("saved OW_" + out, len(inputs), "frames, at old", j, flush=True); e.close()
