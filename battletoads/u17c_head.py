"""Track C: the page at the HEAD of a segment (the card between two levels, skipped so far with one button every other frame):
shortest press pattern by breadth-first search, kept only when the rest of the segment replays unchanged behind it.

    python u17c_head.py <segment> <next level byte> <out (C...)> [NA=240] [extra layers=2]
        env U17C_HEAD_PROBE=1: only print the reference head (level byte, health, x, timer per frame) and stop
    1. reference: the segment from its own bookmark; P = the input on which the toad is set down in the next level
       (level byte, then health 0 / x 0, then health > 0 and x > 0); RAM of the NA frames after it; the hidden alignment
    2. BFS from the bookmark over {nothing, A, B} per frame, deduplicated on the RAM hash, to the placement
    3. every placement found with depth d < P and d = P (mod 2): the segment's inputs after P behind it - frames 8..NA
       identical and the alignment NA frames in equal to the reference's (= merged for good)?  If none: one extra
       Select / Up / Down on each frame of the shortest paths.
    -> logs/fix/u17c_head_<out>.txt, logs/pbeam_<out>.json (bookmark = the segment's), states/<out>_end0b.State
No memory writes; never Start."""
import hashlib
import os
import sys

from u17c_lib import *
from u16b_phase import core_of

SEG, LVL, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
NA = int(sys.argv[4]) if len(sys.argv) > 4 else 240
EXTRA = int(sys.argv[5]) if len(sys.argv) > 5 else 2
log = Log(f"u17c_head_{OUT}.txt")
sj = segj(SEG)
sg = seg(SEG)
BM = os.environ.get("U17C_HEAD_BM") or sj["bookmark"]   # (the bookmark of an old segment can differ from the true chain state in the pad bytes: give the true one)
e = BizHawk(log_name=f"u17c_head_{OUT}.log")


def phase():
    c = core_of(e.save("u17c_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1


def st_next(stage, m):
    return placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)


# ---- 1. the reference
e.load(BM)
m0 = bytes(e.ram(0, 0x800))
stage, P = 0, None
rows = []
for i, b in enumerate(sg[:1500], 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    rows.append((i, b, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, m[0x0B], m[0x3B5]))
    stage = st_next(stage, m)
    if stage == 3:
        P = i
        break
assert P, "the reference never sets the toad down in the next level within 1,500 inputs"
PH0 = phase()
REF = []
for b in sg[P:P + NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
lv = [r[2] for r in rows]
left = next((r[0] for r in rows if r[2] != lv[0]), None)
log(f"{SEG} from {BM}: entry level byte {m0[0x10]} toad {toad(m0)}; level byte changes at input {left}; toad set down in level {LVL} on input {P}; "
    f"head buttons {sorted(set(sg[:P]))}; alignment at the placement PC ${PH0[0]:04X} ts {PH0[1]} parity {PH0[3]}")
if os.environ.get("U17C_HEAD_PROBE") == "1":
    for r in rows:
        log("  ", r)
    e.close()
    sys.exit(0)
FULL = NA - 7


def merged():
    """the loaded state = a placement: the reference's next NA inputs behind it -> identical frames 8..NA (-1: identical but another alignment)"""
    same = 0
    for j in range(len(REF)):
        e.step(bt(sg[P + j]), 1)
        if j < 7:
            continue
        if cut(e.ram(0, 0x800)) != REF[j]:
            break
        same += 1
    if same == FULL and phase() != PHN:
        return -1
    return same


# ---- 2. BFS
e.load(BM)
layer = [(e.msave(), [], 0)]
found = []                                                    # (depth, path)
first_d = None
for depth in range(1, P + 3):
    nxt, seen = [], set()
    for sid, path, st in layer:
        for b in ("", "A", "B"):
            e.mload(sid)
            e.step(bt(b), 1)
            m = bytes(e.ram(0, 0x800))
            st2 = st_next(st, m)
            if st2 == 3:
                found.append((depth, path + [b]))
                continue
            k = (hashlib.sha1(m).digest(), st2)
            if k in seen:
                continue
            seen.add(k)
            nxt.append((e.msave(), path + [b], st2))
    for sid, _, _ in layer:
        e.mfree(sid)
    if found and first_d is None:
        first_d = depth
    if len(nxt) > 500:
        nxt.sort(key=lambda n: -n[2])
        for n in nxt[500:]:
            e.mfree(n[0])
        nxt = nxt[:500]
    layer = nxt
    if depth % 10 == 0:
        log(f"  BFS depth {depth}: {len(layer)} states, stages {sorted(set(n[2] for n in layer))}, placements so far {len(found)}")
    if first_d is not None and depth >= first_d + EXTRA:
        break
    if not layer:
        break
for sid, _, _ in layer:
    e.mfree(sid)
log(f"BFS: first placement at depth {first_d} (reference {P}: {P - (first_d or P)} frames sooner); placements by depth: "
    f"{sorted((d, sum(1 for x in found if x[0] == d)) for d in set(x[0] for x in found))}")
if first_d is None or first_d >= P:
    log("nothing shorter than the reference head")
    e.close()
    sys.exit(0)

# ---- 3. which placements merge with the rest of the segment
results = []


def test(path, why):
    e.load(BM)
    stage = 0
    for b in path:
        e.step(bt(b), 1)
        stage = st_next(stage, e.ram(0, 0x800))
    if stage != 3:
        return None
    ph = phase()
    same = merged()
    results.append((len(path), same, ph[:2] + (ph[3],), why, path))
    return same


cands = sorted((x for x in found if x[0] < P and (P - x[0]) % 2 == 0), key=lambda x: x[0])
log(f"{len(cands)} placements with an even gain; testing ...")
hit = None
for d, path in cands[:60]:
    same = test(path, "bfs")
    if same == FULL:
        hit = (d, path)
        log(f"  MERGED: depth {d} presses {[(i, b) for i, b in enumerate(path) if b]}")
        break
if hit is None and os.environ.get("U17C_HEAD_NOEXTRA") != "1":   # (presses on the page do not move the alignment: u17c_head2.py is the tool)
    done = 0
    for d, path in cands[:6]:
        for i in range(len(path) - 1, -1, -1):
            for btn in ("Select", "Up", "Down"):
                p2 = list(path)
                p2[i] = (p2[i] + "+" + btn).lstrip("+")
                same = test(p2, f"{btn}@{i}")
                done += 1
                if same == FULL:
                    hit = (len(p2), p2)
                    log(f"  MERGED: depth {d} + {btn} on frame {i}: presses {[(k, b) for k, b in enumerate(p2) if b]}")
                    break
            if hit:
                break
        if hit:
            break
    log(f"extra-press variants tried: {done}")
tab = {}
for ln, same, ph, why, path in results:
    tab.setdefault((ln, ph), set()).add(same)
log(f"(head length, (PC, ts, parity)) -> identical frames seen: {sorted((k, sorted(v)) for k, v in tab.items())}")
write_json(FIX / f"u17c_head_{OUT}.json", {"segment": SEG, "P": P, "first_depth": first_d, "ref_phase": [PH0[0], PH0[1], PH0[3]],
                                            "results": [[ln, same, list(ph), why, path] for ln, same, ph, why, path in results]})
if hit:
    d, path = hit
    full = list(path) + sg[P:]
    assert not any(banned1(b) for b in path)
    e.load(BM)
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0b")
    dd = dict(sj)
    dd.update(bookmark=BM, inputs=full, built_from=SEG, head=[P, d], head_presses=[(i, b) for i, b in enumerate(path) if b])
    write_seg(OUT, dd)
    log(f"wrote pbeam_{OUT}.json: {len(full)} inputs ({len(full) - len(sg):+d} vs {SEG}); end {toad(e.ram(0, 0x800))}; bookmark {OUT}_end0b")
else:
    log("NO merging head found")
e.close()
