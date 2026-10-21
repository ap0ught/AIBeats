"""Terra Tubes: get down to the floor (h 38) past the hovering bugs (0x74, hp 15) WITHOUT being carried (anim 36/37 = carried, sinks at
1 px/frame; the up9 line lost ~300 frames there). Small beam from L9c index 7852 ((813,102) standing): 2-frame macros, width 300,
goal = standing on h 38 with x >= 790; carried or hurt = pruned. -> knowledge/l9_bug.json, bookmark L9B_down"""
import json
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("B",), ("Right", "B"), ("Down",), ("Down", "Right"), ("Up",)]
MACRO = 2; WIDTH = 300; STEPS = 90
e = BizHawk(log_name="l9bug.log"); e.load(seg["bookmark"])
for b in ours[:7852]: e.step(tuple(v for v in b.split("+") if v), 1)
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x42A], m[0x475], m[0x3B5] in (36, 37), m[0x565] // 32)
frontier = [(e.msave(), [])]; seen = set(); goal = None
for step in range(STEPS):
    nxt = []
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(a, MACRO); m = e.ram(0, 0x800)
            if m[0x51A] < 47 or m[0x11] < 3 or m[0x3B5] in (36, 37): continue
            k = key(m)
            if k in seen: continue
            seen.add(k); p2 = path + ["+".join(a)] * MACRO
            x, h, hh, z = k[0], k[1], k[2], k[3]
            if z == 0 and h == 38 and x >= 790 and hh == 25 - 1 + 0 or (z == 0 and h == 38 and x >= 790):
                goal = (e.msave(), p2); break
            # rank: lower (unwrapped) first, then right
            H = hh * 256 + h
            nxt.append((H + (0 if z else 0), -x, e.msave(), p2))
        if goal: break
    for sid, _ in frontier: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n: (n[0], n[1]))
    for n in nxt[WIDTH:]: e.mfree(n[2])
    frontier = [(n[2], n[3]) for n in nxt[:WIDTH]]
    if step % 10 == 0: print(f"step {step}: {len(nxt)} states, best H {nxt[0][0] if nxt else None} x {-nxt[0][1] if nxt else None}", flush=True)
    if not frontier: print("died out", flush=True); break
if goal:
    e.mload(goal[0]); m = e.ram(0, 0x800); print("GOAL after", len(goal[1]), "frames: toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x42A], "an", m[0x3B5], flush=True)
    e.save("L9B_down"); json.dump({"segment": "L9c", "from": 7852, "inputs": goal[1]}, open("knowledge/l9_bug.json", "w"))
e.close()
