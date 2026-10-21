"""Stage A beam: from L9c 7819 (the upper step) through the tunnel with the two propeller bugs to x >= 862 un-grabbed, as early as possible.
1-frame actions; the key keeps the last two inputs (double-tap memory); a goal must also survive 8 more frames holding Right.
-> logs/fix/heli_beamA.json, bookmark L9heli_A0.."""
import json, sys, random, time
from l9heli_fix_lib import *
WIDTH = int(sys.argv[1]) if len(sys.argv) > 1 else 400
ACTS = ["Right", "", "Right+A", "A", "Left"]
random.seed(2)
e = BizHawk(log_name="l9heli_fix_beamA.log"); e.load("L9heli_7819")
m = e.ram(0, 0x800); lives0 = m[0x11]
frontier = [(e.msave(), [])]; goals = []; t0 = time.time()
for layer in range(60):
    nxt = {}
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(bt(a), 1); m = e.ram(0, 0x800); s = toad(m)
            if s["hp"] < 47 or m[0x11] < lives0 or s["an"] in CARRIED: continue
            k = (s["x"], s["H"], s["z"], s["spd"], m[0x4C0], m[0x4CF] // 32, m[0x4A2], a, path[-1] if path else "")
            if k in nxt: continue
            p2 = path + [a]
            if s["x"] >= 862:
                sv = e.msave(); ok = True
                for _ in range(8):
                    e.step(("Right",), 1); mm = e.ram(0, 0x800)
                    if mm[0x3D0] in CARRIED or mm[0x51A] < 47: ok = False; break
                if ok: goals.append((len(p2), -s["x"], s["H"], sv, p2, tstr(m))); continue
                e.mfree(sv); continue
            pot = -s["x"] * 4 + max(0, s["H"] - 6540) * 2 - s["spd"] // 16
            nxt[k] = (pot, random.random(), e.msave(), p2)
    for sid, _ in frontier: e.mfree(sid)
    if goals: break
    cand = sorted(nxt.values(), key=lambda v: (v[0], v[1]))
    for c in cand[WIDTH:]: e.mfree(c[2])
    frontier = [(c[2], c[3]) for c in cand[:WIDTH]]
    if layer % 5 == 4: print(f"layer {layer + 1}: {len(cand)} states, best x {-cand[0][0] // 4 if cand else None}, {time.time() - t0:.0f}s", flush=True)
    if not frontier: print("died out"); break
goals.sort(key=lambda g: (g[0], g[2], g[1]))
out = []
for i, g in enumerate(goals[:6]):
    e.mload(g[3]); e.save(f"L9heli_A{i}"); print(f"GOAL {i}: {g[0]} frames -> index {7819 + g[0]}: {g[5]}", " ".join(x or "-" for x in g[4]), flush=True)
    out.append({"root": "L9heli_7819", "root_index": 7819, "frames": g[0], "inputs": g[4], "end": g[5], "bookmark": f"L9heli_A{i}"})
json.dump(out, open(LOGS_DIR / "fix" / "heli_beamA.json", "w"))
e.close()
