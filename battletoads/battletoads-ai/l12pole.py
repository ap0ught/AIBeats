"""Beam from the early landing on the small platform (L12_lap + l12_lap_launch) to a hang on the pole at (288, 4944).
1-frame actions, every distinct (x, h, z, anim, speed) kept once per layer, ranked by distance to the pole; goal =
static airborne near x 288 for 4 frames.   python l12pole.py -> knowledge/l12_lap_pole.json"""
import json
from toads.emulator import BizHawk
from shortcut import k5
launch = json.load(open("knowledge/l12_lap_launch.json"))
e = BizHawk(log_name="l12pole.log"); e.load("L12_lap")
for b in launch: e.step(tuple(v for v in b.split("+") if v), 1)
ACTS = ["", "Right", "Right+A", "A", "Left", "Left+A", "Up+A"]
layer = [(e.msave(), [], None, 0)]                              # state, path, last (x,h), static count
goal = None
for depth in range(1, 260):
    cand = {}
    for sid, path, last, static in layer:
        for act in ACTS:
            e.mload(sid); e.step(tuple(v for v in act.split("+") if v), 1); m = e.ram(0, 0x800); k = k5(m)
            if m[0x51A] < 40 or m[0x11] < 6: continue
            st = static + 1 if (k[2] == 8 and last == k[:2]) else 0
            if st >= 4 and abs(k[0] - 288) <= 8:
                goal = (depth, path + [act], k, m[0x3B5]); break
            key = k + (m[0x3B5],)
            if key in cand: continue
            cand[key] = (abs(k[0] - 288) + abs(k[1] - 4944) + (0 if k[2] else 15), e.msave(), path + [act], k[:2], st)
        if goal: break
    for sid, _, _, _ in layer: e.mfree(sid)
    if goal: break
    nodes = sorted(cand.values(), key=lambda n: n[0])
    if not nodes:
        print("layer", depth, "dead (all states lost)", flush=True); break
    keep = nodes[:300] + [n for n in nodes[300:] if n[3][1] >= 4915][:120]   # plus the ones still up on the platform (the wind comes later)
    drop = [n for n in nodes[300:] if n not in keep]
    layer = [(sid, p, last, st) for _, sid, p, last, st in keep]
    for _, sid, _, _, _ in drop: e.mfree(sid)
    if depth % 5 == 0: print(f"layer {depth}: {len(cand)} states, nearest {nodes[0][0]} {nodes[0][3]}", flush=True)
if goal:
    print("POLE at", len(launch) + goal[0], "state", goal[2], "anim", goal[3], "(old 520)", flush=True)
    json.dump(launch + goal[1], open("knowledge/l12_lap_pole.json", "w"))
else:
    print("no pole grab found")
e.close()
