"""Walk the record's inputs through the timed-platform section (2026-10-04): the green platforms are solid only in
a window of the frame timer, so at every landing scan the standing wait (0..260) before the record's next inputs
and keep the smallest that makes the next landing (within 10 frames / 8 px); landings re-align the input index.
    python waitwalk.py <bookmark at TAS landing j0> <j0> <jstop> <out>  -> knowledge/ww_<out>.json, bookmark WW_<out>"""
import json, sys, resync
from toads.emulator import BizHawk
def legal(b):
    ks = [v for v in b.split("+") if v]
    if "Left" in ks and "Right" in ks: ks = [v for v in ks if v not in ("Left", "Right")]
    if "Up" in ks and "Down" in ks: ks = [v for v in ks if v not in ("Up", "Down")]
    return "+".join(ks)
TAS = [legal("+".join(t)) for t in resync.TAS]; rows = resync.rows   # the record's Left+Right stands become idle frames
bm, j0, jstop, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
lands = [j for j in range(j0 + 1, jstop) if rows[j][3] == 0 and rows[j - 1][3] > 0]
e = BizHawk(log_name=f"waitwalk_{out}.log"); e.load(bm); cur = e.msave(); inputs = []; j = j0
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
while True:
    nxt = [l for l in lands if l > j]
    if not nxt: print("no landing ahead of", j, flush=True); break
    j1 = nxt[0]
    found = None
    for w in range(0, 262, 2):
        e.mload(cur); e.step((), w); seq = [""] * w; hit = None
        for s in range(j - 1, j1 + 12):                      # from one input before the landing: the record's double tap starts there
            e.step(tuple(v for v in TAS[s].split("+") if v), 1); seq.append(TAS[s]); m = e.ram(0, 0x800); k = key(m)
            if m[0x51A] < 47 or m[0x11] < 4: break
            if s >= j1 - 10 and k[2] == 0 and k[1] == rows[j1][2] and abs(k[0] - rows[j1][1]) <= 8: hit = (s, k); break
        if hit: found = (w, seq, hit); break
    if not found: print(f"STUCK: no wait reaches landing {j1} from {j}", flush=True); break
    w, seq, hit = found; inputs += seq; j = j1
    e.mload(cur); [e.step(tuple(v for v in b.split("+") if v), 1) for b in seq]; e.mfree(cur); cur = e.msave()
    print(f"landing {j1} reached (ours {hit[1][:3]}, TAS {rows[j1][1:4]}) with wait {w}; {len(inputs)} frames so far (TAS {j1 - j0})", flush=True)
    json.dump({"bookmark": bm, "inputs": inputs, "jend": j}, open(f"knowledge/ww_{out}.json", "w"))
e.mload(cur); e.save(f"WW_{out}"); json.dump({"bookmark": bm, "inputs": inputs, "jend": j}, open(f"knowledge/ww_{out}.json", "w"))
print("saved WW_" + out, len(inputs), "frames, at TAS", j, flush=True); e.close()
