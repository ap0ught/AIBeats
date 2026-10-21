"""Terra Tubes: the 'helicopter' descent (2026-10-05, found by the owner in the up9 replay at frame 25279): our line hangs from the 0x70
object and sinks 330 px at 1 px/frame; the TAS (rows 59336-59438) jumps off and falls in ~100. Sync our L9c state with a TAS row at
(813..822, 102, ground), replay the TAS's inputs (landing re-sync) up to the corridor entry (59565 = our old index ~8403) and compare.
    -> knowledge/l9_heli.json {from (L9c index), tas_t0, inputs}, bookmark L9H_end (at TAS 59565)"""
import json, re, os
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l9heli.log"); e.load(seg["bookmark"]); saves = {}; states = {}; corr = None
for i, b in enumerate(ours):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800); s = st(m)
    if 7800 <= i + 1 <= 7960: saves[i + 1] = e.msave(); states[i + 1] = s
    if corr is None and i + 1 > 8300 and s[:3] == (584, 70, 0): corr = (i + 1, s, e.msave())
    if i + 1 > 8460: break
print("our corridor-entry state (old sync 8403):", corr[:2] if corr else None, flush=True)
cands = [(f, t) for f, s in states.items() for t in range(59300, 59345) if (rows[t][1], rows[t][2], rows[t][3]) == s[:3] and s[2] == 0]
print("sync candidates:", cands, flush=True)
best = None
for f, t0 in cands:
    e.mload(saves[f]); ins = []; hurt = None; land = None
    for t in range(t0 + 1, 59566):
        b = legal(tas[t - ANCHOR]); e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); r = rows[t]
        if r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if land is None and t >= 59430 and m[0x475] == 0 and m[0x439] == 38: land = t
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
    s = st(m); print(f"ours {f} = TAS {t0}: hurt {hurt}; landed at TAS {land}; end {s} vs corridor entry {corr[1] if corr else None}; {len(ins)} frames (ours {corr[0] - f if corr else '?'})", flush=True)
    if not hurt and (best is None or len(ins) < best[0]):
        best = (len(ins), f, t0); e.save("L9H_end"); json.dump({"segment": "L9c", "from": f, "tas_t0": t0, "inputs": ins, "end_state": s, "corr_index": corr[0] if corr else None}, open("knowledge/l9_heli.json", "w"))
print("best", best, flush=True); e.close()
