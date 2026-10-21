"""Terra Tubes floor crossing, time-aware (2026-10-05): from the bug-free landing (L9B_down, (915,38)) to the corridor entry the old
route reaches at L9c index 8402 ((584,70) standing). Unlike l9bug*.py the key carries the step, so waiting for the mine train is a move.
Beam: 2-frame macros, width W, rank by distance to the goal (x then height), prune hurt/carried.  -> knowledge/l9_cross.json, bookmark L9X_corr"""
import json, os
from toads.emulator import BizHawk
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("B",), ("Left", "B"), ("Down",), ("Down", "Left"), ("Up",)]
MACRO = 2; WIDTH = int(os.environ.get("W", 500)); STEPS = int(os.environ.get("STEPS", 320))
GX, GH, GHH = int(os.environ.get("GX", 584)), int(os.environ.get("GH", 70)), int(os.environ.get("GHH", 24)); SPD = os.environ.get("SPDMAX"); SUBX = os.environ.get("SUBX"); SPDEQ = os.environ.get("SPDEQ"); XTOL = int(os.environ.get("XTOL", 4)); ROOT = os.environ.get("ROOT", "L9B_down"); OUT = os.environ.get("OUT", "")
e = BizHawk(log_name=f"l9cross_{os.environ.get('WAIT0', '0')}.log"); e.load(ROOT); e.step((), int(os.environ.get("WAIT0", 0)))      # arrive later on purpose: the mine train moves on
def key(m, step): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x42A], m[0x475], m[0x565] // 4, m[0x3B5] // 8, (m[0x448] // 8 if SUBX else 0), step)
frontier = [(e.msave(), [])]; goal = None
for step in range(STEPS):
    nxt = []; seen = set()
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(a, MACRO); m = e.ram(0, 0x800)
            if m[0x51A] < int(os.environ.get("HPMIN", 47)) or m[0x11] < 3 or m[0x3B5] in (36, 37): continue
            k = key(m, step)
            if k[:6] in seen: continue
            seen.add(k[:6]); p2 = path + ["+".join(a)] * MACRO
            x, h, hh, z = k[0], k[1], k[2], k[3]
            if z == 0 and h == GH and hh == GHH and abs(x - GX) <= XTOL and (SPD is None or m[0x565] <= int(SPD)) and (SUBX is None or m[0x448] == int(SUBX)) and (SPDEQ is None or m[0x565] == int(SPDEQ)): goal = (e.msave(), p2); break
            H = hh * 256 + h; score = (abs(H - (GHH * 256 + GH)) + abs(x - GX) // 4) if os.environ.get("MODE") == "down" else (abs(x - GX) + abs(H - (GHH * 256 + GH)) // 2) if os.environ.get("MODE") == "near" else ((max(0, x - GX) if GX < 700 else max(0, GX - x)) + (abs(H - (GHH * 256 + GH)) if abs(x - GX) <= 20 else 0))      # rank by x; the height only counts near the goal (the entry ledge is reached by a jump from (635,38))
            nxt.append((score, e.msave(), p2))
        if goal: break
    for sid, _ in frontier: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n: n[0])
    for n in nxt[WIDTH:]: e.mfree(n[1])
    frontier = [(n[1], n[2]) for n in nxt[:WIDTH]]
    if step % 10 == 0: print(f"step {step}: {len(nxt)} states, best score {nxt[0][0] if nxt else None}", flush=True)
    if not frontier: print("died out", flush=True); break
if goal:
    e.mload(goal[0]); m = e.ram(0, 0x800); print("GOAL after", len(goal[1]), "frames: toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x42A], "spd", m[0x565], "an", m[0x3B5], flush=True)
    e.save("L9X_corr" + OUT); json.dump({"bookmark": ROOT, "wait0": int(os.environ.get("WAIT0", 0)), "inputs": [""] * int(os.environ.get("WAIT0", 0)) + goal[1]}, open(f"knowledge/l9_cross_{os.environ.get('WAIT0', '0')}{OUT}.json", "w"))
e.close()
