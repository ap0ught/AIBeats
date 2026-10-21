"""Track C: Level 8's page padded on purpose.  The Terra Tubes entry merges with the next segment only for one value of
(segment length mod 6) (see u17c_notes section 4), so a fight whose kill + death is not in that class needs a page 2 or 4
frames longer: the mash simply starts later.

    python u17c_tail.py <raw segment>[@entry bookmark] <kill index> <next segment>[@ref bookmark] <out (C...)> [NA=240] [d range lo,hi=-8,14]
        tail variants: idle W = (frames from the kill to the level byte leaving 7) + d, then A,B (or B,A) on alternate frames;
        for each: segment length, alignment (PC, timestamp, frame parity) at the placement, identical frames 8..NA of the next
        segment (and the alignment NA frames in must equal the reference's)
    then, around the shortest variants that are in the right class but not merged, one extra Select / Up / Down on each frame
    of the death wait (env U17C_TAIL_SCAN=0 turns it off; U17C_TAIL_MAXLEN = longest segment length worth scanning)
    -> logs/fix/u17c_tail_<out>.txt / .json, logs/pbeam_<out>.json = the shortest merged variant (bookmark = the entry), <out>_end0b"""
import json
import os
import sys

from u17c_lib import *
from u16b_phase import core_of

SPEC, KILL, NSPEC, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
NA = int(sys.argv[5]) if len(sys.argv) > 5 else 240
DLO, DHI = [int(v) for v in (sys.argv[6] if len(sys.argv) > 6 else "-8,14").split(",")]
SEG, _, BM = SPEC.partition("@")
NXT, _, NBM = NSPEC.partition("@")
sj, nj = segj(SEG), segj(NXT)
BM, NBM = BM or sj["bookmark"], NBM or nj["bookmark"]
pre = seg(SEG)[:KILL]
nxt = seg(NXT)
LVL = 11
log = Log(f"u17c_tail_{OUT}.txt")
e = BizHawk(log_name=f"u17c_tail_{OUT}.log", fields={"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11})


def phase():
    c = core_of(e.save("u17c_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1


e.load(NBM)
PH0 = phase()
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
FULL = NA - 7
log(f"reference {NXT} from {NBM}: PC ${PH0[0]:04X} ts {PH0[1]} parity {PH0[3]}")
e.load(BM)
for b in pre:
    s = e.step(bt(b), 1)
base = e.msave()
left = None
for k in range(1, 700):
    s = e.step((), 1)
    if s.level != 7:
        left = k
        break
log(f"{SEG} from {BM}: kill after {KILL} inputs; the level byte leaves 7 {left} frames later (input {KILL + left})")
SEEN = {}


def run(W, first, extra=None):
    """-> (tail inputs, phase, identical frames) or None"""
    e.mload(base)
    pat = ("A", "B") if first == "A" else ("B", "A")
    tail, stage = [], 0
    for k in range(W + 400):
        b = "" if k < W else pat[(k - W) % 2]
        if extra and extra[0] == k and extra[1] not in b.split("+"):
            b = (b + "+" + extra[1]).lstrip("+")
        s = e.step(bt(b), 1)
        tail.append(b)
        stage = placed_stage(stage, s.level, s.hp, s.x | s.xh << 8, LVL)
        if stage == 3:
            break
    else:
        return None
    if not (s.hp == 47 and s.lives == 3):
        return None
    ph = phase()
    k2 = (ph, cut(e.ram(0, 0x800)))
    if k2 not in SEEN:
        same = 0
        for j in range(len(REF)):
            e.step(bt(nxt[j]), 1)
            if j < 7:
                continue
            if cut(e.ram(0, 0x800)) != REF[j]:
                break
            same += 1
        if same == FULL and phase() != PHN:
            same = -1
        SEEN[k2] = same
    return tail, ph, SEEN[k2]


res = []
for d in range(DLO, DHI + 1):
    for first in ("A", "B"):
        r = run(left + d, first)
        if r is None:
            continue
        tail, ph, same = r
        res.append((KILL + len(tail), d, first, None, ph[0], ph[1], ph[3], same))
        log(f"  mash from level-left{d:+d}, {first} first: segment {KILL + len(tail)} (page {len(tail) - left}); PC ${ph[0]:04X} ts {ph[1]} (class {ph[1] % 15 // 5}) parity {ph[3]}; identical {same}/{FULL}"
            + ("  MERGED" if same == FULL else ""))
good = sorted(r for r in res if r[7] == FULL)
if not good and os.environ.get("U17C_TAIL_SCAN", "1") != "0":
    # right class (timestamp mod 15 and parity equal to the reference's) but another instruction boundary: one extra press in the death wait
    MAXLEN = int(os.environ.get("U17C_TAIL_MAXLEN", 10 ** 9))
    cls = sorted((r for r in res if r[5] % 15 == PH0[1] % 15 and r[6] == PH0[3] and r[0] <= MAXLEN), key=lambda r: r[0])
    log(f"no plain variant merges; variants in the reference's class: {[(r[0], r[1], r[2], r[5]) for r in cls][:12]}")
    done = 0
    for ln, d, first, _, _, _, _, _ in cls[:4]:
        hit = False
        for k in range(left - 1, 0, -1):
            for btn in ("Select", "Up", "Down"):
                r = run(left + d, first, (k, btn))
                done += 1
                if r is None:
                    continue
                tail, ph, same = r
                res.append((KILL + len(tail), d, first, (k, btn), ph[0], ph[1], ph[3], same))
                if same == FULL:
                    log(f"  MERGED: mash from level-left{d:+d}, {first} first + {btn} on tail frame {k}: segment {KILL + len(tail)}; ts {ph[1]}")
                    hit = KILL + len(tail) <= ln
                    if hit:
                        break
            if hit:
                break
        if hit:
            break
    log(f"extra-press variants tried: {done}")
    good = sorted((r for r in res if r[7] == FULL), key=lambda r: (r[0], r[3] is not None))
tab = {}
for r in res:
    tab.setdefault((r[0], r[5] % 15 // 5, r[6]), set()).add(r[7])
log(f"(segment length, class, parity) -> identical frames: {sorted((k, sorted(v)) for k, v in tab.items())}")
write_json(FIX / f"u17c_tail_{OUT}.json", {"segment": SEG, "kill": KILL, "left": left, "ref": [PH0[0], PH0[1], PH0[3]], "results": [list(r) for r in res]})
if good:
    ln, d, first, extra, pc, ts, par, same = good[0]
    tail, ph, same = run(left + d, first, tuple(extra) if extra else None)
    full = pre + tail
    e.load(BM)
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0b")
    dd = dict(sj)
    dd.update(bookmark=BM, inputs=full, built_from=SEG, wait=left + d, mash=[first, "B" if first == "A" else "A"], extra=extra, in_phase_with=NXT, alignment=[pc, ts, par])
    for q in ("placed", "level_left"):
        dd.pop(q, None)
    write_seg(OUT, dd)
    lr, ud, st, sel = banned(full)
    log(f"wrote pbeam_{OUT}.json: {len(full)} inputs (mash from level-left{d:+d}, {first} first, extra {extra}); ts {ts}; Left+Right {lr}, Up+Down {ud}, Start {st}, Select frames {sel}; "
        f"end {toad(e.ram(0, 0x800))}; bookmark {OUT}_end0b")
else:
    log("NO merged variant")
e.close()
