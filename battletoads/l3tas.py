"""Turbo Tunnel's gauntlet by the TAS's own inputs (2026-10-06): tas/ram_l3all_1p.txt (inputs + RAM per frame) rows 13150..14700; 2 banned-press
frames get stripped. Sync our L3u state (bookmark L1b_end_r + inputs) with a TAS row by (x, h, z, speed), replay with the landing re-sync,
and report when the bikes appear / the mount state versus ours (L3u: 1,824 inputs to L3u_bikes)."""
import json, os
from toads.emulator import BizHawk, LOGS_DIR
NAMES = ["Right", "Left", "Down", "Up", "Start", "Select", "B", "A"]
rows = {}
for ln in open("tas/ram_l3all_1p.txt"):
    p = ln.split()
    if len(p) >= 3 and p[0].startswith("f"): rows[int(p[0][1:])] = (p[1], bytes.fromhex(p[2]))
def tin(f):
    keys = [n for n, c in zip(NAMES, rows[f][0]) if c != "."]
    if "Left" in keys and "Right" in keys: keys = [k for k in keys if k != "Left"]
    if "Up" in keys and "Down" in keys: keys = [k for k in keys if k != "Up"]
    return tuple(keys)
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565])
seg = json.load(open(LOGS_DIR / "pbeam_L3u.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
e = BizHawk(log_name="l3tas.log"); e.load(seg["bookmark"]); saves = {}; states = {}
for i, b in enumerate(ours):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if m[0x10] == 3 and 60 <= i + 1 <= 400 and m[0x439] == 64 and m[0x475] == 0: saves[i + 1] = e.msave(); states[i + 1] = st(m)
    if i + 1 > 400: break
print("our ground states at h 64:", list(states.items())[:6], "...", len(states), flush=True)
tst = {f: st(rows[f][1]) for f in range(13200, 13420) if f in rows and rows[f][1][0x10] == 3}
cands = [(i, f) for i, s in states.items() for f, t in tst.items() if s == t]
print("exact sync candidates (ours index, TAS frame):", cands[:20], flush=True)
best = None
for i, t0 in cands[:12]:
    e.mload(saves[i]); ins = []; hurt = None; bikes = None; sync = t0
    for t in range(t0 + 1, 14760):
        b = tin(t); e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); tm = rows[t][1]
        if tm[0x475] == 0 and rows[t - 1][1][0x475] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if abs((m[0x3FD] | m[0x3EE] << 8) - (tm[0x3FD] | tm[0x3EE] << 8)) <= 3 and abs(m[0x439] - tm[0x439]) <= 3: sync = t
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
        if bikes is None and any(m[0x3C1 + q] == 0x18 for q in range(2, 15)): bikes = (t, len(ins), st(m))
    print(f"ours {i} = TAS {t0}: sync held to {sync} (+{sync - t0}); hurt {hurt}; bikes appear {bikes}; end {st(m)} after {len(ins)} (ours from {i}: {len(ours) - i} to L3u_bikes)", flush=True)
    if bikes and not hurt and (best is None or i + bikes[1] < best[0]):
        best = (i + bikes[1], i, t0); e.save("L3T_bikes"); json.dump({"segment": "L3u", "from": i, "tas_t0": t0, "inputs": ins}, open("knowledge/l3_gauntlet_tas.json", "w"))
print("best (frames to the bikes from the segment start):", best, "(L3u: 1824 to the mount)", flush=True)
e.close()
