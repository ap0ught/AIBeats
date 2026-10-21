"""Track C: make the NEXT level roll the reference dice behind a rebuilt segment (copy of chain B's u16b_sync.py, generalised).

The level load zeroes the dice $25-$28; the only hidden state behind a rebuilt segment is the CPU's alignment against the frame
(QuickNES core blob of a savestate: bytes 4-5 timestamp in 1/15 CPU clocks, 8-11 frame count, 12-13 PC, 14-19 registers).  One
harmless press (Select / Up / Down) on a frame of the segment's free tail steers it.

    python u17c_sync.py <segment>[@entry bookmark] <next segment>[@reference bookmark] <T0> <next level byte> <out> [NA=240]
        T0 = index of the first input of the segment's free tail; from there on one extra press per variant is added
        env U17C_BTNS (Select,Up,Down)  U17C_TWO=1 pairs when no single press works  U17C_ONLYTWO=1  U17C_PAIRS (1500)  U17C_SEED
            U17C_EXACT=1 only variants whose alignment EQUALS the reference's are written   U17C_MAXHITS (8, pairs)
            U17C_IDLE=k  k extra empty frames are inserted at T0 first (k even keeps the parity)
    For every (tail frame, button): replay from a rolling base, find the frame the toad is set down in the next level, read the
    alignment there, and - once per alignment - replay the next segment's first NA frames against that segment's own reference
    (whole RAM, stack page excluded; frames 8..NA must all be identical AND the alignment NA frames in must equal the reference's).
    -> logs/fix/u17c_sync_<out>.txt / .json, logs/pbeam_<out>.json = the shortest merged variant (bookmark = the entry bookmark),
       states/<out>_end0b.State (tool-made end state)
No memory writes."""
import json
import os
import random
import sys

from u17c_lib import *
from u16b_phase import core_of

SEGSPEC, NXTSPEC, T0, LVL, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 240
SEG, _, SEGBM = SEGSPEC.partition("@")
NXT, _, NXTBM = NXTSPEC.partition("@")
BTNS = os.environ.get("U17C_BTNS", "Select,Up,Down").split(",")
IDLE = int(os.environ.get("U17C_IDLE", 0))
QUICK = int(os.environ.get("U17C_QUICK", 0))            # stop the scan once two merged variants of the shortest length are in hand (after this many variants)
F = {"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11}
sj, nj = segj(SEG), segj(NXT)
SEGBM = SEGBM or sj["bookmark"]
NXTBM = NXTBM or nj["bookmark"]
sg = seg(SEG)
if IDLE:
    sg = sg[:T0] + [""] * IDLE + sg[T0:]
nxt = seg(NXT)
n = len(sg)
log = Log(f"u17c_sync_{OUT}.txt")
e = BizHawk(log_name=f"u17c_sync_{OUT}.log", fields=F)
SKIP = 7


def phase():
    c = core_of(e.save("u17c_phase_" + OUT))
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


def tail_input(i):
    return sg[i] if i < n else sg[n - 2 + (i - n) % 2]        # past the built end the tail goes on in its own pattern


def add(b, btn):
    return b if btn in b.split("+") else (b + "+" + btn).lstrip("+")


SEEN = {}
LCP = {}                                                      # (segment length, class = ts mod 15 // 5, frame parity) -> variants


def finish(i0, presses):
    stage, s = 0, None
    i = i0
    while i < n + 40:
        b = tail_input(i)
        if i in presses:
            b = add(b, presses[i])
        s = e.step(bt(b), 1)
        i += 1
        stage = placed_stage(stage, s.level, s.hp, s.x | s.xh << 8, LVL)
        if stage == 3:
            break
    else:
        return None
    ph = phase()
    LCP[(i, ph[1] % 15 // 5, ph[3])] = LCP.get((i, ph[1] % 15 // 5, ph[3]), 0) + 1
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


def describe(ph):
    return f"PC ${ph[0]:04X} ts {ph[1]} parity {ph[3]}"


e.load(SEGBM)
for b in sg[:T0]:
    e.step(bt(b), 1)
base = e.msave()
base0 = e.msave()
r0 = finish(T0, {})
log(f"{SEG} from {SEGBM} as built (+{IDLE} idle at {T0}): set down at segment length {r0[0]} (built {n}); alignment {describe(r0[1])}; next-level frames 8..{NA} identical: {r0[2]} of {FULL}"
    f"{'  -> MERGED' if r0[2] == FULL else ''}")
res = [(r0[0], r0[2] == FULL, {}, r0[1][:2])]
hits = 1 if r0[2] == FULL else 0
for i in (range(T0, n - 1) if os.environ.get("U17C_ONLYTWO") != "1" else []):
    for btn in BTNS:
        if btn in sg[i].split("+") or banned1(add(sg[i], btn)):
            continue
        e.mload(base)
        r = finish(i, {i: btn})
        if r is None:
            continue
        ok = r[2] == FULL
        res.append((r[0], ok, {i: btn}, r[1][:2]))
        if ok:
            hits += 1
            log(f"  MERGED: {btn} on tail frame {i - T0 + 1} (segment index {i}) -> segment {r[0]} inputs; alignment {describe(r[1])}")
    e.mload(base)
    e.step(bt(sg[i]), 1)
    nb = e.msave()
    e.mfree(base)
    base = nb
    if (i - T0) % 100 == 99:
        log(f"    ... tail frame {i - T0 + 1}: {len(res)} variants, {hits} in sync, {len(SEEN)} alignments seen")
    if QUICK and len(res) >= QUICK:
        lmin = min(r[0] for r in res)                        # (a length of the other frame parity can never merge: accept one more)
        if sum(1 for r in res if r[1] and r[0] <= lmin + 1) >= 2:
            log(f"    quick stop at tail frame {i - T0 + 1}: {len(res)} variants, shortest length seen {lmin}, merged at {min(r[0] for r in res if r[1])}")
            break


def table_():
    return sorted(((f"${k[0][0]:04X}", k[0][1], "same parity" if k[0][3] == PH0[3] else "ODD shift", v) for k, v in SEEN.items()), key=lambda t: t[:3])


log(f"variants {len(res)}; merged {hits}; alignments at the cut -> identical frames (of {FULL}; -1 = all identical but not merged): {table_()}")
lens = {}
for ln, ok, pr, ph in res:
    lens.setdefault(ln, [0, 0])[1 if ok else 0] += 1
log("segment length -> (out of sync, in sync):", sorted(lens.items()))
log(f"(segment length, class, parity) -> variants (reference: class {PH0[1] % 15 // 5}, parity {PH0[3]}): {sorted(LCP.items())}")
EXACT = os.environ.get("U17C_EXACT") == "1"
good = sorted((r for r in res if r[1] and (not EXACT or tuple(r[3]) == PH0[:2])), key=lambda r: (r[0], len(r[2])))
log(f"exact alignment (PC ${PH0[0]:04X} ts {PH0[1]}): {sum(1 for r in res if r[1] and tuple(r[3]) == PH0[:2])} variants, shortest "
    f"{min([r[0] for r in res if r[1] and tuple(r[3]) == PH0[:2]], default=None)}; any merged alignment: shortest {min([r[0] for r in res if r[1]], default=None)}")
if not good and (os.environ.get("U17C_TWO") == "1" or os.environ.get("U17C_ONLYTWO") == "1"):
    rng = random.Random(int(os.environ.get("U17C_SEED", 1)))
    idx = list(range(T0, n - 1))
    for t in range(int(os.environ.get("U17C_PAIRS", 1500))):
        i1, i2 = sorted(rng.sample(idx, 2))
        pr = {i1: rng.choice(BTNS), i2: rng.choice(BTNS)}
        if any(banned1(add(sg[i], b)) for i, b in pr.items()):
            continue
        e.mload(base0)
        r = finish(T0, pr)
        if r and r[2] == FULL and (not EXACT or tuple(r[1][:2]) == PH0[:2]):
            res.append((r[0], True, pr, r[1][:2]))
            log(f"  MERGED (pair): {pr} -> segment {r[0]} inputs; alignment {describe(r[1])}")
            if sum(1 for x in res if x[1]) >= int(os.environ.get("U17C_MAXHITS", 8)):
                break
        if t % 200 == 199:
            log(f"    ... {t + 1} pairs, {sum(1 for x in res if x[1])} merged, {len(SEEN)} alignments seen")
    log(f"after the pairs: alignments -> identical frames: {table_()}")
    good = sorted((r for r in res if r[1] and (not EXACT or tuple(r[3]) == PH0[:2])), key=lambda r: (r[0], len(r[2])))
write_json(FIX / f"u17c_sync_{OUT}.json", {"segment": SEG, "entry": SEGBM, "next": NXT, "ref": NXTBM, "T0": T0, "idle": IDLE, "table": table_(), "ref_phase": [PH0[0], PH0[1], PH0[3]],
                                            "results": [[ln, ok, {str(k): v for k, v in pr.items()}, list(ph)] for ln, ok, pr, ph in res if ok or not pr]})
if good:
    ln, ok, pr, ph = good[0]
    full = [add(tail_input(i), pr[i]) if i in pr else tail_input(i) for i in range(ln)]
    e.load(SEGBM)
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0b")
    d = dict(sj)
    d.update(bookmark=SEGBM, inputs=full, built_from=SEG, sync_press={str(k): v for k, v in pr.items()}, in_phase_with=NXT, alignment=list(ph), idle_inserted=[T0, IDLE])
    if "placed" in d:
        d["placed"] = d["placed"] - len(sj["inputs"]) + ln
    write_seg(OUT, d)
    lr, ud, st, sel = banned(full)
    log(f"wrote pbeam_{OUT}.json: {ln} inputs ({ln - len(sj['inputs']):+d} vs {SEG}), presses {pr}; alignment PC ${ph[0]:04X} ts {ph[1]}; Left+Right {lr}, Up+Down {ud}, Start {st}, Select frames {sel}; "
        f"end {toad(e.ram(0, 0x800))}; bookmark {OUT}_end0b")
else:
    log("NO in-sync variant found")
e.close()
