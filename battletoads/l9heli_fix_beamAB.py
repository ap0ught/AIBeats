"""Stage A+B(top) beam: from L9c 7819 through the bug tunnel and down past the first shaft hazard to H <= HG, un-grabbed and unhurt,
as early as possible.  1-frame actions, key keeps the last two inputs.  -> logs/fix/heli_beamAB.json, bookmarks L9heli_AB0.."""
import json, sys, random, time
from l9heli_fix_lib import *
WIDTH = int(sys.argv[1]) if len(sys.argv) > 1 else 400
HG = int(sys.argv[2]) if len(sys.argv) > 2 else 6440
ACTS = ["Right", "", "Right+A", "A", "Left"]
random.seed(3)
e = BizHawk(log_name="l9heli_fix_beamAB.log"); e.load("L9heli_7819")
m = e.ram(0, 0x800); lives0 = m[0x11]
frontier = [(e.msave(), [])]; goals = []; t0 = time.time()
for layer in range(90):
    nxt = {}
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(bt(a), 1); m = e.ram(0, 0x800); s = toad(m)
            if s["hp"] < 47 or m[0x11] < lives0 or s["an"] in CARRIED: continue
            k = (s["x"], s["H"], s["z"], s["spd"], m[0x4C0], m[0x4CF] // 32, m[0x4A2], a, path[-1] if path else "")
            if k in nxt: continue
            p2 = path + [a]
            if s["H"] <= HG:
                goals.append((len(p2), s["x"], e.msave(), p2, tstr(m), m[0x466])); continue
            if s["x"] < 848 and s["H"] >= 6470: pot = 20000 + (848 - s["x"]) * 4 + max(0, s["H"] - 6540) * 2 - s["spd"] // 16
            else: pot = 10000 + (s["H"] - 6182)
            nxt[k] = (pot, random.random(), e.msave(), p2, s["x"])
    for sid, _ in frontier: e.mfree(sid)
    if len(goals) >= 12: break
    cand = sorted(nxt.values(), key=lambda v: (v[0], v[1]))
    keep = []; per = {}
    for c in cand:
        b = (c[0] // 4, c[4] // 3)
        if per.get(b, 0) >= 12: continue
        per[b] = per.get(b, 0) + 1; keep.append(c)
        if len(keep) >= WIDTH: break
    ks = set(id(c) for c in keep)
    for c in cand:
        if id(c) not in ks: e.mfree(c[2])
    frontier = [(c[2], c[3]) for c in keep]
    if layer % 5 == 4: print(f"layer {layer + 1}: {len(cand)} states, best pot {cand[0][0] if cand else None} x {cand[0][4] if cand else None}, goals {len(goals)}, {time.time() - t0:.0f}s", flush=True)
    if not frontier: print("died out"); break
goals.sort(key=lambda g: (g[0], g[1]))
out = []
for i, g in enumerate(goals[:12]):
    e.mload(g[2]); e.save(f"L9heli_AB{i}"); print(f"GOAL {i}: {g[0]} frames -> index {7819 + g[0]}: {g[4]} subH {g[5]} |", " ".join(x or "-" for x in g[3]), flush=True)
    out.append({"root": "L9heli_7819", "root_index": 7819, "frames": g[0], "inputs": g[3], "end": g[4], "bookmark": f"L9heli_AB{i}"})
json.dump(out, open(LOGS_DIR / "fix" / "heli_beamAB.json", "w"))
e.close()
