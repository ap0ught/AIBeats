"""(v2: mine-aware key, 1-frame actions again from frame FINE2, stage A discourages high jumps)
Time-layered beam for the helicopter fix (2026-10-09).  Root = bookmark L9heli_7819 (L9c index 7819, the upper step before the
propeller bugs).  Stages by potential (lower = better; every layer = the same frame count, so the rank is pure progress):
  A  still left of x 848 above H 6470: get through the bug tunnel WITHOUT being grabbed (anim 36/37 pruned)
  B  falling down the shaft: lower is better
  C  floor level (H < 6260): further left is better
Goal: standing (z 0) on the floor H 6182 with x <= GX.   Stratified truncation (per 4-px x bucket) keeps landing spots diverse.
    python l9heli_fix_beam.py <out tag> [GX=760] [WIDTH=300] [LAYERS=260]
-> logs/fix/heli_beam_<tag>.json {root, root_index, inputs, end}, bookmarks L9heli_<tag>_0..4"""
import json, sys, os, random, time
from l9heli_fix_lib import *

TAG = sys.argv[1]; GX = int(sys.argv[2]) if len(sys.argv) > 2 else 760
WIDTH = int(sys.argv[3]) if len(sys.argv) > 3 else 300; LAYERS = int(sys.argv[4]) if len(sys.argv) > 4 else 260
ROOT = os.environ.get("ROOT", "L9heli_7819"); ROOT_INDEX = int(os.environ.get("ROOT_INDEX", 7819))
FINE = int(os.environ.get("FINE", 46))            # the first FINE frames use 1-frame actions, then 2-frame macros
FINE2 = int(os.environ.get("FINE2", 124))         # from this frame on 1-frame actions again (the floor, the mine)
HPMIN = int(os.environ.get("HPMIN", 47)); FLOORH = 6182
ACTS = ["", "Right", "Left", "A", "Right+A", "Left+A"]
random.seed(1)


def pot(s):
    x, H = s["x"], s["H"]
    if H >= 6470 and x < 848:
        return 20000 + (848 - x) * 3 + max(0, H - 6536) * 4
    if H >= 6260:
        return 10000 + (H - FLOORH)
    return (x - 500) + (0 if s["z"] == 0 else 3) + max(0, H - 6214)


def mine(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x72:
            return ((m[0x3FD + q] | m[0x3EE + q] << 8) // 4, m[0x565 + q])
    return None


def key(m, s):
    return (s["x"], s["H"], s["z"], s["spd"] // 8, m[0x4C0], m[0x4CF] // 64, m[0x4A2] & 0x70, s["an"] in (45,), mine(m) if s["H"] < 6260 else None)


e = BizHawk(log_name=f"l9heli_fix_beam_{TAG}.log")
e.load(ROOT)
m = e.ram(0, 0x800); lives0 = m[0x11]; print("root", tstr(m), "lives", lives0, flush=True)
frontier = [(e.msave(), [])]; goals = []; t0 = time.time(); frames = 0
for layer in range(LAYERS):
    n = 1 if (frames < FINE or frames >= FINE2) else 2
    nxt = {}
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid); e.step(bt(a), n); m = e.ram(0, 0x800); s = toad(m)
            if s["hp"] < HPMIN or m[0x11] < lives0 or s["an"] in CARRIED or s["lvl"] != 11:
                continue
            k = key(m, s)
            if k in nxt:
                continue
            p2 = path + [a] * n
            if s["z"] == 0 and s["H"] == FLOORH and s["x"] <= GX:
                goals.append((len(p2), s["x"], e.msave(), p2, tstr(m), ostr(m)))
                continue
            nxt[k] = (pot(s), random.random(), e.msave(), p2, s["x"])
    for sid, _ in frontier:
        e.mfree(sid)
    frames += n
    if goals and len(goals) >= 5:
        break
    cand = sorted(nxt.values(), key=lambda v: (v[0], v[1]))
    keep = []; per = {}; cap = max(3, WIDTH // 12)
    for c in cand:
        b = (c[0] // 2000, c[4] // 4)
        if per.get(b, 0) >= cap:
            continue
        per[b] = per.get(b, 0) + 1; keep.append(c)
        if len(keep) >= WIDTH:
            break
    ks = set(id(c) for c in keep)
    for c in cand:
        if id(c) not in ks:
            e.mfree(c[2])
    frontier = [(c[2], c[3]) for c in keep]
    if layer % 5 == 0 or goals:
        b = keep[0] if keep else None
        print(f"layer {layer} frames {frames}: {len(cand)} states, kept {len(keep)}, best pot {b[0] if b else None} x {b[4] if b else None}, goals {len(goals)}, {time.time() - t0:.0f}s", flush=True)
    if not frontier:
        print("died out", flush=True); break
goals.sort(key=lambda g: (g[0], g[1]))
out = []
for i, g in enumerate(goals[:5]):
    e.mload(g[2]); e.save(f"L9heli_{TAG}_{i}")
    print(f"GOAL {i}: {g[0]} frames after index {ROOT_INDEX} -> index {ROOT_INDEX + g[0]}: {g[4]} | {g[5]}", flush=True)
    out.append({"root": ROOT, "root_index": ROOT_INDEX, "frames": g[0], "inputs": g[3], "end": g[4], "objs": g[5], "bookmark": f"L9heli_{TAG}_{i}"})
json.dump(out, open(LOGS_DIR / "fix" / f"heli_beam_{TAG}.json", "w"))
e.close()
