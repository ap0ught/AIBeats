"""Exact re-join of the old route (up14 / L9c) from a new, earlier state (2026-10-09).
BFS over 1-frame inputs from our state; hit = the toad's kinematic key equals the old run's key at any old index j in the
windows (cap14.ram rows are the old run).  Every hit is then VERIFIED: the old inputs j+1.. are replayed and the RAM compared
with the old run's own rows (toad track + all non-volatile bytes) for VERIFY frames.
    python l9heli_fix_join.py <beam json> <goal idx> <start frame in that path> <depth> <out tag> [windows "8300-8315,8357-8361"]
-> logs/fix/heli_join_<tag>.json {root, root_index, inputs (path prefix + join), join_old_index, gain}, bookmark L9heli_join_<tag>"""
import json, sys, os, time
from l9heli_fix_lib import *

SRC, GI, START, DEPTH, TAG = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
WINS = sys.argv[6] if len(sys.argv) > 6 else "8300-8315,8357-8361,8393-8409"
VERIFY = int(os.environ.get("VERIFY", 600))
ACTS = os.environ.get("ACTS", ",Left,Right").split(",")
AIR = bool(os.environ.get("AIR"))
R = cap(); ins = up14_inputs()
VOL = set(range(0x100, 0x300)) | set(range(0x700, 0x800)) | {0x0B, 0x0C, 0x25, 0x26, 0x27, 0x28}     # stack, OAM, sound, timers, dice


def kin(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x4A2], m[0x4C0], m[0x4CF])


targets = {}
for w in WINS.split(","):
    a, b = (int(v) for v in w.split("-"))
    for j in range(a, b + 1):
        m = bytes(R[OFF + j - 1])
        if AIR or m[0x475] == 0:
            targets.setdefault(kin(m), j)
print(len(targets), "old target states", flush=True)
g = json.load(open(SRC))[GI]
e = BizHawk(log_name=f"l9heli_fix_join_{TAG}.log"); e.load(g["root"])
prefix = g["inputs"][:START]
for b in prefix:
    e.step(bt(b), 1)
m = e.ram(0, 0x800); print("start", START, "->", g["root_index"] + START, tstr(m), "|", ostr(m), flush=True)
lives0 = m[0x11]


def verify(sid, j):
    """replay the old inputs after old index j; return (frames identical in the toad track, first diff, volatile-free diff count at the end)"""
    e.mload(sid); bad = None; n = 0; last = None
    for k in range(j, min(j + VERIFY, 9987)):
        e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
        if kin(m)[:5] != kin(ref)[:5] or m[0x51A] != ref[0x51A]:
            bad = (k + 1, kin(m)[:5], kin(ref)[:5]); break
        n += 1; last = sum(1 for a in range(0x800) if a not in VOL and m[a] != ref[a])
    return n, bad, last


layer = [(e.msave(), [])]; seen = {kin(m)}; hits = []; t0 = time.time()
for d in range(1, DEPTH + 1):
    nxt = []
    for sid, path in layer:
        for a in ACTS:
            e.mload(sid); e.step(bt(a), 1); m = e.ram(0, 0x800)
            if m[0x51A] < 47 or m[0x11] < lives0 or m[0x3D0] in CARRIED:
                continue
            k = kin(m)
            if k in seen:
                continue
            seen.add(k)
            s2 = e.msave(); p2 = path + [a]
            if k in targets:
                j = targets[k]; n, bad, last = verify(s2, j)
                tot = START + len(p2); gain = (j - g["root_index"]) - tot
                print(f"HIT depth {d}: old index {j} after {tot} frames (gain {gain}); verify: {n} frames identical, first diff {bad}, other-byte diffs at end {last}", flush=True)
                hits.append((gain, n, j, p2, s2, bad, last))
            nxt.append((s2, p2))
    hitsids = set(h[4] for h in hits)
    for sid, _ in layer:
        if sid not in hitsids:
            e.mfree(sid)
    layer = nxt
    if d % 4 == 0:
        print(f"depth {d}: {len(layer)} states, seen {len(seen)}, hits {len(hits)}, {time.time() - t0:.0f}s", flush=True)
    if not layer or any(h[1] >= VERIFY - 1 or h[5] is None for h in hits):
        break
good = sorted([h for h in hits if h[5] is None or h[1] >= VERIFY - 1], key=lambda h: -h[0])
if good:
    gain, n, j, p2, s2, bad, last = good[0]
    e.mload(s2); e.save(f"L9heli_join_{TAG}")
    out = {"root": g["root"], "root_index": g["root_index"], "inputs": prefix + p2, "join_old_index": j, "gain": gain, "verified_frames": n, "other_diffs": last}
    json.dump(out, open(LOGS_DIR / "fix" / f"heli_join_{TAG}.json", "w"))
    print("SAVED join at old index", j, "gain", gain, "frames; path", len(out["inputs"]), flush=True)
else:
    print("no verified join; hits:", [(h[0], h[1], h[2], h[5]) for h in hits][:20], flush=True)
e.close()
