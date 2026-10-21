"""Walk from our state to the old route's exact state (2026-10-06): BFS over {idle, Left, Right} per frame, dedup on
(x, unwrapped h, z, facing, speed, anim); success = the old run's (x, h, z, facing, speed) at any old frame in b0..b1
(on the ground).   python retjoin.py <segment> <ref bookmark> <ref frame> <our bookmark> <b0> <b1> <depth> <out>
    -> knowledge/rj_<out>.json {b: old frame joined, inputs}"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
SEG, REFBM, REF0, BM, B0, B1, DEPTH, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), sys.argv[8]
old = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))["inputs"]]
import os
SUB = bool(os.environ.get("RJ_SUB"))
AIR = bool(os.environ.get("RJ_AIR"))        # targets/joins may be airborne or swimming (z 8)
def k5(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x4A2] & 0x40, m[0x565]) + ((m[0x448],) if SUB else ())
e = BizHawk(log_name=f"retjoin_{OUT}.log"); e.load(REFBM)
targets = {}
for i in range(REF0, B1):
    e.step(tuple(v for v in old[i].split("+") if v), 1); m = e.ram(0, 0x800)
    if i + 1 >= B0 and (AIR or m[0x475] == 0): targets.setdefault(k5(m) + ((m[0x3B5],) if AIR else ()), i + 1)
print(len(targets), "old target states in", B0, B1, sorted(targets)[:4], flush=True)
e.load(BM); m = e.ram(0, 0x800); print("ours:", k5(m), "an", m[0x3B5], flush=True)
layer = [(e.msave(), [])]; seen = {k5(m) + (m[0x3B5],)}; hit = None
for d in range(1, DEPTH + 1):
    nxt = []
    for sid, path in layer:
        for b in (("", "Left", "Right", "Up", "Down", "A", "Up+A", "Right+A", "Left+A") if AIR else ("", "Left", "Right")):
            e.mload(sid); e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
            if m[0x51A] < 47 or m[0x11] < 4: continue
            k = k5(m)
            kk = k + ((m[0x3B5],) if AIR else ())
            if (AIR or m[0x475] == 0) and kk in targets: hit = (targets[kk], path + [b]); break
            key = k + (m[0x3B5],)
            if key in seen: continue
            seen.add(key); nxt.append((e.msave(), path + [b]))
        if hit: break
    for sid, _ in layer: e.mfree(sid)
    if hit or not nxt: break
    layer = nxt
    if d % 20 == 0: print("depth", d, "states", len(layer), flush=True)
if hit:
    print("JOIN old frame", hit[0], "after", len(hit[1]), "frames", flush=True)
    json.dump({"b": hit[0], "inputs": hit[1]}, open(f"knowledge/rj_{OUT}.json", "w"))
else:
    print("no join within", DEPTH, flush=True)
e.close()
