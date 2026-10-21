"""Final builder: page-mash variants at the END of a segment (the card page before the next level) and what they do to the
hidden alignment at the next level's placement.

    python u17f_page.py <segment>[@entry bookmark] <next segment>[@reference bookmark] <T0> <next level byte> <out> [NA=240]
        T0 = index from which the tail is free (the page's presses are the non-empty inputs at or after T0)
    Variants: every page press gets a button (U17F_PBTN, default A,B), a hold of 1 or 2 frames (U17F_HOLD, default 1,2) and a
    cumulative delay (U17F_SHIFT, default 0,1,2) - the later presses move with it, so every press still comes after its card
    accepts one.  U17F_PRE=<index>:<button>[,...] adds fixed extra presses to every variant (before T0 is allowed: the replay then
    starts at the earliest one).
    For every variant: frame the toad is set down in the next level, alignment there (QuickNES core blob: PC, timestamp, parity),
    and - once per alignment - the next segment's first NA frames against its own reference (frames 8..NA identical AND the
    alignment NA frames in equal to the reference's).
    -> logs/fix/u17f_page_<out>.txt / .json; logs/pbeam_<out>.json = the shortest merged variant (bookmark = the entry bookmark)
No memory writes."""
import itertools
import os
import sys

from u17f_lib import *
from u16b_phase import core_of

SEGSPEC, NXTSPEC, T0, LVL, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 240
SEG, _, SEGBM = SEGSPEC.partition("@")
NXT, _, NXTBM = NXTSPEC.partition("@")
PBTN = os.environ.get("U17F_PBTN", "A,B").split(",")
HOLD = [int(x) for x in os.environ.get("U17F_HOLD", "1,2").split(",")]
SHIFT = [int(x) for x in os.environ.get("U17F_SHIFT", "0,1,2").split(",")]
PRE = {int(a.split(":")[0]): a.split(":")[1] for a in os.environ.get("U17F_PRE", "").split(",") if a}
F = {"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11}
sj, nj = segj(SEG), segj(NXT)
SEGBM = SEGBM or sj["bookmark"]
NXTBM = NXTBM or nj["bookmark"]
sg = seg(SEG)
nxt = seg(NXT)
n = len(sg)
presses = [(i, sg[i]) for i in range(T0, n) if sg[i]]
log = Log(f"u17f_page_{OUT}.txt")
log(f"{SEG} from {SEGBM}: {n} inputs, page presses {presses}; buttons {PBTN}, holds {HOLD}, cumulative delays {SHIFT}, fixed extra presses {PRE}")
e = BizHawk(log_name=f"u17f_page_{OUT}.log", fields=F)
SKIP = 7


def phase():
    c = core_of(e.save("u17f_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1   # PC, timestamp, registers, frame-count parity


e.load(NXTBM)
PH0 = phase()
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
FULL = NA - SKIP
log(f"reference {NXT} from {NXTBM}: alignment at its entry PC ${PH0[0]:04X} timestamp {PH0[1]} parity {PH0[3]}; {NA} frames in: PC ${PHN[0]:04X} ts {PHN[1]} parity {PHN[3]}")


def add(b, btn):
    return b if btn in b.split("+") else (b + "+" + btn).lstrip("+")


SEEN = {}
START = min([T0] + list(PRE))


def run(tail):
    """tail = {index: buttons} for the frames from T0 on (everything else empty); PRE presses are added on top of the segment"""
    stage, i = 0, START
    while i < n + 60:
        b = sg[i] if i < T0 else tail.get(i, "")
        if i in PRE:
            b = add(b, PRE[i])
        if banned1(b):
            return None
        s = e.step(bt(b), 1)
        i += 1
        stage = placed_stage(stage, s.level, s.hp, s.x | s.xh << 8, LVL)
        if stage == 3:
            break
    else:
        return None
    ph = phase()
    k = (ph, cut(e.ram(0, 0x800)))
    if k not in SEEN:
        same = 0
        for j in range(len(REF)):
            e.step(bt(nxt[j]), 1)
            if j < SKIP:
                continue
            if cut(e.ram(0, 0x800)) != REF[j]:
                break
            same += 1
        if same == FULL and phase() != PHN:
            same = -1
        SEEN[k] = same
    return i, ph, SEEN[k]


e.load(SEGBM)
for b in sg[:START]:
    e.step(bt(b), 1)
base = e.msave()
res, tab = [], {}
np_ = len(presses)
count = 0
for btns in itertools.product(PBTN, repeat=np_):
    for holds in itertools.product(HOLD, repeat=np_):
        for shifts in itertools.product(SHIFT, repeat=np_):
            tail, cum = {}, 0
            for (idx, _), b, h, sh in zip(presses, btns, holds, shifts):
                cum += sh
                for q in range(h):
                    tail[idx + cum + q] = b.replace("&", "+")
            e.mload(base)
            r = run(tail)
            count += 1
            if r is None:
                tab[("never set down",)] = tab.get(("never set down",), 0) + 1
                continue
            ln, ph, same = r
            key_ = (ln, f"${ph[0]:04X}", ph[1], ph[3], same)
            tab[key_] = tab.get(key_, 0) + 1
            res.append((ln, same == FULL, tail, ph[:2], (btns, holds, shifts)))
            if same == FULL and tab[key_] <= 6:
                log(f"  MERGED: buttons {btns} holds {holds} delays {shifts} -> segment {ln} inputs; alignment PC ${ph[0]:04X} ts {ph[1]} parity {ph[3]}")
            if count % 200 == 0:
                log(f"    ... {count} variants; (length, PC, ts, parity, identical frames of {FULL}) -> variants: {sorted(tab.items(), key=lambda t: str(t[0]))}")
log(f"variants {count}; (length, PC, ts, parity, identical next-level frames of {FULL}; -1 = all identical but another alignment after them) -> variants:")
for k_, v in sorted(tab.items(), key=lambda t: str(t[0])):
    log(f"    {k_}: {v}")
good = sorted((r for r in res if r[1]), key=lambda r: (r[0], sum(r[4][1]), sum(r[4][2])))
write_json(FIX / f"u17f_page_{OUT}.json", {"segment": SEG, "entry": SEGBM, "next": NXT, "ref": NXTBM, "T0": T0, "pre": {str(k): v for k, v in PRE.items()},
                                            "table": [[list(map(str, k_)), v] for k_, v in tab.items()],
                                            "merged": [[r[0], {str(k): v for k, v in r[2].items()}, list(r[3]), [list(x) for x in r[4]]] for r in good[:200]]})
if good:
    ln, ok, tail, ph, desc = good[0]
    full = []
    for i in range(ln):
        b = sg[i] if i < T0 else tail.get(i, "")
        if i in PRE:
            b = add(b, PRE[i])
        full.append(b)
    e.load(SEGBM)
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0b")
    d = dict(sj)
    d.update(bookmark=SEGBM, inputs=full, built_from=SEG, page=[list(x) for x in desc], sync_press={str(k): v for k, v in PRE.items()}, in_phase_with=NXT, alignment=list(ph))
    if "placed" in d:
        d["placed"] = d["placed"] - len(sj["inputs"]) + ln
    write_seg(OUT, d)
    lr, ud, st, sel = banned(full)
    log(f"wrote pbeam_{OUT}.json: {ln} inputs ({ln - len(sj['inputs']):+d} vs {SEG}), page {desc}, extra presses {PRE}; alignment PC ${ph[0]:04X} ts {ph[1]}; Left+Right {lr}, Up+Down {ud}, Start {st}, "
        f"Select frames {sel}; end {toad(e.ram(0, 0x800))}; bookmark {OUT}_end0b")
else:
    log("NO merged variant")
e.close()
