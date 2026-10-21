"""Corridor: which sync frame / 1-frame tweak keeps our toad on the TAS's EXACT integer track (2026-10-04)? The mine homes on the toad
(speed byte 32 -> 160 at ~8 px), so a 1-px lead is enough to get clipped where the TAS passes. For every sync candidate f (ours) = t0 (TAS),
and for a few 1-frame tweaks (an extra idle / a dropped Right at frame p), count how long x and h stay exactly equal, and whether the toad
is hurt / exits the corridor. Saves the best exit as knowledge/l9_corridor_tas.json + bookmark L9T_out."""
import json, re, os
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652
seg = json.load(open(LOGS_DIR / "pbeam_L9m.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l9align.log"); e.load(seg["bookmark"]); saves = {}; states = {}
for i, b in enumerate(ours):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if 8290 <= i + 1 <= 8420: saves[i + 1] = e.msave(); states[i + 1] = st(m)
    if i + 1 > 8420: break
cands = [(f, t) for f, s in states.items() for t in range(59470, 59600) if t in rows and (rows[t][1], rows[t][2], rows[t][3]) == s[:3] and s[2] == 0]
print(len(cands), "candidates", flush=True)
def play(f, t0, tweak=None):
    e.mload(saves[f]); ins = []; exact = t0; hurt = None; out = None; drift = None
    for t in range(t0 + 1, 59990):
        j = t - ANCHOR
        if j >= len(tas): break
        b = legal(tas[j])
        if tweak and t == tweak[0]:
            if tweak[1] == "idle": e.step((), 1); ins.append("")
            elif tweak[1] == "drop": b = ()
        e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); r = rows.get(t)
        if r and r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        s = st(m)
        if r and drift is None and (s[0], s[1]) == (r[1], r[2]): exact = t
        elif r and drift is None: drift = (t, s[0] - r[1], s[1] - r[2])
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
        if s[0] >= 1115 and out is None: out = t
        if out and t > out + 30: break
    return exact, drift, hurt, out, ins
best = None
for f, t0 in cands:
    for tweak in [None] + [(p, k) for p in range(t0 + 1, t0 + 12) for k in ("idle", "drop")]:
        exact, drift, hurt, out, ins = play(f, t0, tweak)
        if tweak is None or exact - t0 >= 40:
            print(f"ours {f} = TAS {t0} tweak {tweak}: exact to {exact} (+{exact - t0}) drift {drift}; hurt {hurt}; exit {out}", flush=True)
        if out and not hurt and (best is None or len(ins) < best[0]):
            best = (len(ins), f, t0, tweak); e.save("L9T_out"); json.dump({"segment": "L9m", "from": f, "tas_t0": t0, "tweak": tweak, "inputs": ins}, open("knowledge/l9_corridor_tas.json", "w"))
            print("   SAVED", best, flush=True)
print("best", best, flush=True)
e.close()
