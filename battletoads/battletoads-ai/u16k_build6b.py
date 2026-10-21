"""Track K: build a Level 6 segment = L6c[0:2022] + warp-room line (cut on the portal touch) + idle through the warp
animation + the SHORTEST page mash found by a breadth-first search over {nothing, A, B} per frame (no Start).

    python u16k_build6b.py <out> <line json>      line json = {inputs: [...]} from the room root (up14 frame 11910)
    -> logs/pbeam_<out>.json (bookmark L4c5_end0), states/<out>_end0b.State, logs/fix/u16k_build6b_<out>.txt/.json

(1) reference L6c from L4c5_end0; (2) the line to the touch (toad stopped at x >= 408 on the ledge) and on, idle, to two
frames before the level byte leaves 8; (3) BFS, deduplicated on the RAM hash, to the Level 8 placement (level byte 7, then
toad hp 0 / x 0, then hp > 0 and x > 0); (4) one-piece replay from the bookmark against L6c's end state.
"""
import hashlib
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

out = sys.argv[1]
line = json.load(open(sys.argv[2]))["inputs"]
CUT = 2022
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
old_ins = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
logf = open(LOGS_DIR / "fix" / f"u16k_build6b_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n")
    logf.flush()


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], rtn=m[0x23] | m[0x24] << 8, score="".join(str(d) for d in m[0x5F4:0x5FA]))


def stage_next(stage, m):
    lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
    if stage == 0 and lv == 7:
        stage = 1
    if stage == 1 and hp == 0 and x == 0:
        stage = 2
    if stage == 2 and hp > 0 and x > 0:
        stage = 3
    return stage


e = BizHawk(log_name=f"u16k_build6b_{out}.log")

# ---- 1. the reference
e.load("L4c5_end0")
stage, placed_ref = 0, None
for n, b in enumerate(old_ins, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if n == CUT:
        root_ref = toad(m)
    stage = stage_next(stage, m)
    if stage == 3 and placed_ref is None:
        placed_ref = n
m_ref = bytes(e.ram(0, 0x800))
log(f"reference L6c: {len(old_ins)} inputs, placement at {placed_ref}; room root {root_ref}; end {toad(m_ref)}")
assert placed_ref == len(old_ins)

# ---- 2. the line to the touch, then idle until two frames before the level byte leaves 8
e.load("L4c5_end0")
for b in old_ins[:CUT]:
    e.step(bt(b), 1)
ins, touch, minhp, e50d = list(old_ins[:CUT]), None, 99, None
for b in line:
    e.step(bt(b), 1)
    ins.append(b)
    m = e.ram(0, 0x800)
    t = toad(m)
    minhp = min(minhp, t["hp"])
    if t["x"] >= 408 and t["spd"] == 0 and t["z"] == 0 and (t["H"] & 0xFF) == (7518 & 0xFF):
        touch = len(ins)
        break
assert touch and minhp == 47 and t["lives"] == root_ref["lives"], f"no clean touch: {t} minhp {minhp}"
log(f"touch at input {touch} (r+{touch - CUT}) x {t['x']}")
at_touch = e.msave()
left = None
for j in range(400):
    e.step((), 1)
    m = e.ram(0, 0x800)
    if e50d is None and (m[0x23] | m[0x24] << 8) == 0xE50D:
        e50d = touch + j + 1
    if m[0x10] != 8:
        left = touch + j + 1
        break
assert left, "the level byte never leaves 8"
log(f"$E50D at {e50d} (r+{e50d - CUT}); level byte leaves 8 at input {left} (touch+{left - touch}, $E50D+{left - e50d})")
e.mload(at_touch)
for j in range(left - touch - 2):
    e.step((), 1)
    ins.append("")

# ---- 3. BFS over the mash
layer = [(e.msave(), [], 0)]
found = None
for depth in range(1, 120):
    nxt, seen = [], set()
    for sid, path, st in layer:
        for b in ("", "A", "B"):
            e.mload(sid)
            e.step(bt(b), 1)
            m = bytes(e.ram(0, 0x800))
            st2 = stage_next(st, m)
            if st2 == 3:
                found = path + [b]
                break
            key = (hashlib.sha1(m).digest(), st2)
            if key in seen:
                continue
            seen.add(key)
            nxt.append((e.msave(), path + [b], st2))
        if found:
            break
    for sid, _, _ in layer:
        e.mfree(sid)
    if found:
        break
    if len(nxt) > 400:
        nxt.sort(key=lambda n: -n[2])
        for n in nxt[400:]:
            e.mfree(n[0])
        nxt = nxt[:400]
    layer = nxt
    if depth % 10 == 0:
        log(f"  BFS depth {depth}: {len(layer)} states, stages {sorted(set(n[2] for n in layer))}")
assert found, "BFS found no placement"
# trailing presses that are not needed: blank them from the end while the placement frame stays (cheap check below in step 4)
new = ins + found
log(f"BFS: placement {len(found)} frames after the BFS root -> segment {len(new)} inputs (L6c {len(old_ins)}; saves {len(old_ins) - len(new)}); "
    f"presses in the tail: {[(i, b) for i, b in enumerate(found) if b]}")
bad = [i for i, b in enumerate(new[CUT:], CUT) if "Start" in b or ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)]
assert not bad, f"banned presses in the new part at {bad[:5]}"

# ---- 4. one piece from the bookmark
e.load("L4c5_end0")
stage, placed, minhp6 = 0, None, 99
for n, b in enumerate(new, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if m[0x10] == 8 and n > 300:
        minhp6 = min(minhp6, m[0x51A])
    stage = stage_next(stage, m)
    if stage == 3 and placed is None:
        placed = n
m_new = bytes(e.ram(0, 0x800))
a, b_ = toad(m_ref), toad(m_new)
diff = [i for i in range(0x800) if m_ref[i] != m_new[i]]
log(f"one-piece replay from L4c5_end0: {len(new)} inputs, placement at {placed}, min hp in the level {minhp6}; end {b_}")
log(f"L6c end: {a}")
log(f"RAM bytes that differ from L6c's end state: {len(diff)}: {[hex(i) for i in diff[:40]]}")
ok = placed == len(new) and all(a[k] == b_[k] for k in ("level", "x", "H", "hp", "lives", "score")) and minhp6 == 47
log(f"VERIFIED {ok}: frames saved {len(old_ins) - len(new)}")
if ok:
    e.save(out + "_end0b")
    note = ("KARNATH'S LAIR. Room 1: three snakes, their heads pause at corners and lift you; the exit is a ledge three screens up. "
            "Warp room: a sprint jump at the rising snake (tap Right, let go, Right+A on the same frame keeps the run speed through the grab), "
            "climb with Right+A held, over the snake's head while it still rises and a 3-pixel-a-frame flight over the first star to the portal's ledge."
            "||The record's line, read off his video frame by frame; our jump comes about 16 frames earlier than his")
    json.dump({"bookmark": "L4c5_end0", "inputs": new, "note": note, "rerolls": [], "slack": 0}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    json.dump({"segment": out, "len": len(new), "old_len": len(old_ins), "frames_saved": len(old_ins) - len(new), "touch_r": touch - CUT,
               "e50d_r": e50d - CUT, "level_left_at": left, "tail": found, "ram_diff": [hex(i) for i in diff]},
              open(LOGS_DIR / "fix" / f"u16k_build6b_{out}.json", "w"))
    log(f"wrote logs/pbeam_{out}.json and states/{out}_end0b.State")
e.close()
