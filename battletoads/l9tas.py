"""Terra Tubes' duck corridor by the 1-player TAS's own inputs (2026-10-04): we hop it at ~1.1 px/frame (L9 frames ~8444-8904, 460 frames);
the TAS runs it in 315 (rows 59575-59890 of tas/watch_1p_log.txt). Like l4c5tas.py: find a frame of ours whose toad (x, h, z, speed)
equals a TAS row before the corridor, then apply the TAS's inputs (tas1p_l9_inputs.json, index = TAS frame - ANCHOR) with the landing
re-sync, and see whether the toad gets through unhurt.
    python l9tas.py            -> prints the sync pairs and how far each holds; the best is saved as knowledge/l9_corridor_tas.json, bookmark L9T_out"""
import json, os, re, sys
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json"))
ANCHOR = int(os.environ.get("L9_ANCHOR", 51652))
seg = json.load(open(LOGS_DIR / "pbeam_L9m.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def tx(m): return m[0x3FD] | m[0x3EE] << 8
def st(m): return (tx(m), m[0x439], m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l9tas.log"); e.load(seg["bookmark"])
states = {}; saves = {}
for i, b in enumerate(ours):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if 8300 <= i + 1 <= 8460:
        states[i + 1] = st(m); saves[i + 1] = e.msave()
    if i + 1 > 8460: break
print("ours 8300..8460:", [(f, s[:4]) for f, s in list(states.items())[::20]], flush=True)
T0, T1 = 59440, 59600
cands = [(f, t) for f, s in states.items() for t in range(T0, T1) if t in rows and (rows[t][1], rows[t][2], rows[t][3]) == s[:3] and s[2] == 0]
print("sync candidates (x, h, on ground):", cands[:30], flush=True)
best = None
FB = int(os.environ.get("L9_BASE", 8300))                        # wait-scan mode: idle k frames at this earlier frame of ours, then our own inputs to the sync frame (a different mine phase)
trials = [(f, t0, 0) for f, t0 in cands[:40]]
if os.environ.get("L9_WAITSCAN"):
    pick = [(f, t0) for f, t0 in cands if f in (int(v) for v in os.environ["L9_WAITSCAN"].split(","))]
    trials = [(f, t0, k) for k in range(0, 260, 3) for f, t0 in pick]
for f, t0, k in trials:
    if k == 0: e.mload(saves[f]); pre = []
    else:
        e.mload(saves[FB]); e.step((), k); pre = [""] * k
        for b in ours[FB:f]: e.step(tuple(v for v in b.split("+") if v), 1); pre.append(b)
        m = e.ram(0, 0x800)
        if m[0x51A] < 47: print(f"k {k}: hurt before the sync frame", flush=True); continue
        if st(m)[:3] != states[f][:3]:                         # the slide differs after the wait: look for a fresh sync with any TAS row over the next 80 of our frames
            t0 = None
            for b in ours[f:f + 80]:
                e.step(tuple(v for v in b.split("+") if v), 1); pre.append(b); m = e.ram(0, 0x800); s3 = st(m)
                if m[0x51A] < 47: break
                if s3[2] == 0:
                    tt = [t for t in range(T0, T1 + 40) if t in rows and (rows[t][1], rows[t][2], rows[t][3]) == s3[:3]]
                    if tt: t0 = tt[0]; break
            if t0 is None: print(f"k {k}: no fresh sync after the wait (at {st(m)[:4]})", flush=True); continue
    ins = []; hurt = None; sync = t0; out = None
    for t in range(t0 + 1, 59990):
        j = t - ANCHOR
        if j >= len(tas): break
        b = legal(tas[j]); e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); r = rows.get(t)
        if r and abs(tx(m) - r[1]) <= 3 and abs(m[0x439] - r[2]) <= 3: sync = t
        if r and r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if m[0x51A] < 47 or m[0x11] < 3:
            hurt = t; break
        if tx(m) >= 1115 and out is None: out = t
        if out and t > out + 30: break
    print(f"k {k} ours {f} = TAS {t0}: sync held to {sync} (+{sync - t0}); hurt {hurt}; corridor exit (x>=1115) at {out}; end {st(m)[:4]}", flush=True)
    if out and not hurt and (best is None or len(ins) < best[0]):
        best = (len(ins), f, t0, ins); e.save("L9T_out"); json.dump({"segment": "L9m", "from": FB if k else f, "wait": k, "tas_t0": t0, "inputs": pre + ins}, open("knowledge/l9_corridor_tas.json", "w"))
print("best", best[:3] if best else None, flush=True)
e.close()
