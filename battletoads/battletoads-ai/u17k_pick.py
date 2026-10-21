"""Track K2: the page mash behind several room-1 variants with the same capture frame (the page's dice differ per variant:
K6's page takes 47 frames after the BFS root, some variants 48).  For each (b, a, tap) of the stage-2 sweep behind the
stage-1 line (cut 1473, k 3, hold 42): room 1 -> room 2 -> K6's warp-room line -> idle -> BFS over {nothing, A, B}.
    python u17k_pick.py <tag> "b,a,tap;b,a,tap;..."  -> logs/fix/u17k_pick_<tag>.txt, logs/fix/u17k_pick_<tag>_<b>_<a>_<tap>.json"""
import hashlib, json, sys
from u17k_lib import *

tag = sys.argv[1]
cands = [tuple(int(v) for v in c.split(",")) for c in sys.argv[2].split(";")]
cut, k, hold, corner = 1473, 3, 42, 1704
k6 = seg("K6")
pre = k6[:cut] + k6[cut + k:1508]
base = pre + ["Right+A"] * 20 + ["Right"] * hold + [""] * 600
LINE_END, ROOM2_REF = 2252, 1986
logf = open(FIX / f"u17k_pick_{tag}.txt", "a", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); logf.write(s + "\n"); logf.flush()


def stage_next(stage, m):
    lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
    if stage == 0 and lv == 7:
        stage = 1
    if stage == 1 and hp == 0 and x == 0:
        stage = 2
    if stage == 2 and hp > 0 and x > 0:
        stage = 3
    return stage


e = BizHawk(log_name=f"u17k_pick_{tag}.log")
e.load("B4_end0")
for b_ in base[:1700]:
    e.step(bt(b_), 1)
root = e.msave()
for b, a, tap in cands:
    r1 = base[:corner + b] + ["Left"] * 2 + ["A"] * a + [""] * 400
    r1 = r1[:tap] + ["Right", ""] + ["Right+A"] * 54 + [""] * 200
    e.mload(root)
    room2, minhp = None, 99
    for n in range(1701, 2060):
        e.step(bt(r1[n - 1]), 1)
        m = e.ram(0x3E0, 0x140)          # 0x3E0..0x51F
        x, H = m[0x3FD - 0x3E0] | m[0x3EE - 0x3E0] << 8, m[0x439 - 0x3E0] | m[0x42A - 0x3E0] << 8
        minhp = min(minhp, m[0x51A - 0x3E0])
        if x == 76 and H < 7600:
            room2 = n
            break
    if not room2 or minhp < 47:
        log(f"b {b} a {a} tap {tap}: no room 2 (min hp {minhp})")
        continue
    head_ins = r1[:room2] + k6[ROOM2_REF:LINE_END]
    for b_ in k6[ROOM2_REF:LINE_END]:
        e.step(bt(b_), 1)
    at_touch = e.msave()
    left = None
    for j in range(400):
        e.step((), 1)
        if e.ram(0x10, 1)[0] != 8:
            left = j + 1
            break
    if not left:
        log(f"b {b} a {a} tap {tap}: room 2 at {room2}, the level byte never leaves 8")
        e.mfree(at_touch)
        continue
    e.mload(at_touch)
    e.mfree(at_touch)
    pre_ = [""] * (left - 2)
    for _ in pre_:
        e.step((), 1)
    layer, found = [(e.msave(), [], 0)], None
    for depth in range(1, 100):
        nxt, seen = [], set()
        for sid, path, st in layer:
            for bb in ("", "A", "B"):
                e.mload(sid)
                e.step(bt(bb), 1)
                m = bytes(e.ram(0, 0x800))
                st2 = stage_next(st, m)
                if st2 == 3:
                    found = path + [bb]
                    break
                key = (hashlib.sha1(m).digest(), st2)
                if key in seen:
                    continue
                seen.add(key)
                nxt.append((e.msave(), path + [bb], st2))
            if found:
                break
        for sid, _, _ in layer:
            e.mfree(sid)
        if found:
            for sid, _, _ in nxt:
                e.mfree(sid)
            break
        if len(nxt) > 400:
            nxt.sort(key=lambda n: -n[2])
            for n in nxt[400:]:
                e.mfree(n[0])
            nxt = nxt[:400]
        layer = nxt
    if not found:
        log(f"b {b} a {a} tap {tap}: room 2 at {room2}, BFS found nothing")
        continue
    new = head_ins + pre_ + found
    log(f"b {b} a {a} tap {tap}: room 2 at {room2}, level byte leaves 8 at touch+{left}, page {len(found)} frames after the root, "
        f"segment {len(new)} inputs (K6 2467: saves {2467 - len(new)}); presses {[(len(head_ins) + len(pre_) + i, p) for i, p in enumerate(found) if p]}")
    json.dump({"inputs": new, "room2": room2, "b": b, "a": a, "tap": tap, "len": len(new)}, open(FIX / f"u17k_pick_{tag}_{b}_{a}_{tap}.json", "w"))
e.close()
