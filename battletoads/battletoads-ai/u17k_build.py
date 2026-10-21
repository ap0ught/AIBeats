"""Track K2: build K7 = new room 1 (inputs to the capture in the exit hole, e.g. logs/fix/u17k_p3b_<tag>_best.json) + idle
until the toad appears in room 2 + K6's own inputs from its room-2 frame (index 1986) to the Level 8 placement.
    python u17k_build.py <out> <room1 json> [bookmark=B4_end0]
-> logs/pbeam_<out>.json, states/<out>_end0b.State, logs/fix/u17k_build_<out>.txt/.json
Checks: one-piece replay from the bookmark; placement on the last input; end state = K6's from the same bookmark (level 7,
toad position, hp 47, lives 2, score), RAM diff listed; min hp 47 in the level; no Start / L+R / U+D; no memory writes."""
import hashlib, json, sys
from u17k_lib import *

out, r1 = sys.argv[1], json.load(open(sys.argv[2]))["inputs"]
bm = sys.argv[3] if len(sys.argv) > 3 else "B4_end0"
k6 = seg("K6")
logf = open(FIX / f"u17k_build_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); logf.write(s + "\n"); logf.flush()


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], lives=m[0x11],
                score="".join(str(d) for d in m[0x5F4:0x5FA]))


def stage_next(stage, m):
    lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
    if stage == 0 and lv == 7:
        stage = 1
    if stage == 1 and hp == 0 and x == 0:
        stage = 2
    if stage == 2 and hp > 0 and x > 0:
        stage = 3
    return stage


def replay(e, ins, tag):
    e.load(bm)
    stage, placed, minhp, room2, sh = 0, None, 99, None, []
    for n, b in enumerate(ins, 1):
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        if m[0x10] == 8 and n > 300:
            minhp = min(minhp, m[0x51A])
        if room2 is None and n > 1700 and (m[0x3FD] | m[0x3EE] << 8) == 76 and (m[0x439] | m[0x42A] << 8) < 7600:
            room2 = n
        stage = stage_next(stage, m)
        if stage == 3 and placed is None:
            placed = n
        if room2:
            mm = bytearray(m); mm[0x100:0x200] = bytes(256)
            sh.append(hashlib.sha1(bytes(mm)).hexdigest()[:10])
    m = bytes(e.ram(0, 0x800))
    log(f"{tag}: {len(ins)} inputs, toad in room 2 at {room2}, placement at {placed}, min hp {minhp}, end {toad(m)}")
    return m, placed, minhp, room2, sh


e = BizHawk(log_name=f"u17k_build_{out}.log")
m_ref, placed_ref, hp_ref, room2_ref, sh_ref = replay(e, k6, "reference K6")
assert placed_ref == len(k6) and room2_ref == 1986, (placed_ref, room2_ref)
# new room 1: to the frame the toad appears in room 2
e.load(bm)
room2 = None
ins = list(r1) + [""] * 200
for n, b in enumerate(ins, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if n > 1700 and (m[0x3FD] | m[0x3EE] << 8) == 76 and (m[0x439] | m[0x42A] << 8) < 7600:
        room2 = n
        break
assert room2, "the new room 1 never reaches room 2"
# warp room: K6's own line to the portal touch (K6 index 2252 = end of Right+A x170), idle until two frames before the
# level byte leaves 8, then the SHORTEST page mash by BFS over {nothing, A, B} per frame (as u16k_build6c.py does; no Start)
LINE_END = 2252
head_ins = ins[:room2] + k6[room2_ref:LINE_END]
e.load(bm)
for b in head_ins:
    e.step(bt(b), 1)
at_touch = e.msave()
left = None
for j in range(400):
    e.step((), 1)
    if e.ram(0x10, 1)[0] != 8:
        left = j + 1
        break
assert left, "the level byte never leaves 8"
log(f"line ends at {len(head_ins)}; level byte leaves 8 {left} frames later (K6: 2434 - 2252 = 182 if identical)")
e.mload(at_touch)
pre = [""] * (left - 2)
for b in pre:
    e.step((), 1)
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
assert found, "BFS found no placement"
log(f"BFS: placement {len(found)} frames after the BFS root; presses {[(len(head_ins) + len(pre) + i, b) for i, b in enumerate(found) if b]}")
new = head_ins + pre + found
log(f"new room 1: toad in room 2 at {room2} (K6 {room2_ref}: {room2_ref - room2} frames sooner); segment {len(new)} inputs (K6 {len(k6)})")
bad = banned(new)
assert not bad, f"banned presses at {bad[:5]}"
m_new, placed, minhp, room2b, sh_new = replay(e, new, "one-piece replay of the new segment")
diff = [i for i in range(0x800) if m_ref[i] != m_new[i]]
a, b_ = toad(m_ref), toad(m_new)
same_tail = sum(1 for x, y in zip(sh_ref, sh_new) if x == y)
log(f"RAM bytes that differ from K6's end state: {len(diff)}: {[hex(i) for i in diff[:40]]}; frames since the room-2 frame with RAM identical to K6's "
    f"(stack page excluded): {same_tail} of {len(sh_new)}")
ok = placed == len(new) and all(a[k] == b_[k] for k in ("level", "x", "H", "hp", "lives", "score")) and minhp == 47
log(f"VERIFIED {ok}: frames saved vs K6 {len(k6) - len(new)}; Start {sum('Start' in x for x in new)} Select {sum('Select' in x for x in new)}")
if ok:
    e.save(out + "_end0b")
    note = json.load(open(LOGS_DIR / "pbeam_K6.json")).get("note", "")
    tmp = LOGS_DIR / f"pbeam_{out}.json.tmp"
    json.dump({"bookmark": bm, "inputs": new, "note": note, "rerolls": [], "slack": 0}, open(tmp, "w"))
    import os
    os.replace(tmp, LOGS_DIR / f"pbeam_{out}.json")
    json.dump({"segment": out, "len": len(new), "k6_len": len(k6), "frames_saved_vs_K6": len(k6) - len(new), "room2_appears": room2,
               "ram_diff_vs_K6_end": [hex(i) for i in diff], "bookmark": bm, "inputs_sha1": hashlib.sha1("\n".join(new).encode()).hexdigest()},
              open(FIX / f"u17k_build_{out}.json", "w"))
    log(f"wrote logs/pbeam_{out}.json and states/{out}_end0b.State")
e.close()
