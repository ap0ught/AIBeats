"""Final builder: the card page at the HEAD of a segment, shortened by 2 frames, with the hidden alignment repaired by ONE extra
press of ANY legal button on a frame of the PREVIOUS segment (track C tried Select only, on the last 90 frames).

    python u17f_head.py <segments before, comma separated> <previous segment> <segment> <next level byte> <out tag> [S] [buttons] [NA=240]
        e.g.  python u17f_head.py C1b,C3u L3skipu B4 4 Fk4 596 Select,A
        The state at the previous segment's start is made by a power-on replay (assemble.py's intro + the segments before): the
        TRUE route state, not an old bookmark (track C's trap: bookmark L3skipu_end_r differs in the pad bytes).
        S = how many of the previous segment's last frames get a press (default: all of it)
        heads: the BFS heads of track C (logs/fix/u17c_head_<U17F_HEADS, default C4>.json, even gain) + an A,B mash on every frame
    test: (previous segment + press) + head: the toad must be set down on the head's last frame; then the segment's inputs after
          its own placement P: frames 8..NA identical to the reference (the segment behind the unchanged previous segment, same
          power-on state) AND the alignment NA frames in equal to the reference's.
    -> logs/fix/u17f_head_<out tag>.txt / .json     (segments are written by u17f_headmk.py from a chosen line)
No memory writes; never Start."""
import hashlib
import json
import os
import sys

from u17f_lib import *
from u16b_phase import core_of

BEFORE, PREV, SEG, LVL, OUT = [x for x in sys.argv[1].split(",") if x not in ("", "-")], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
pv, sg = seg(PREV), seg(SEG)
S = int(sys.argv[6]) if len(sys.argv) > 6 else len(pv)
BTNS = (sys.argv[7] if len(sys.argv) > 7 else "Select,Up,Down,Left,Right,A,B").split(",")
NA = int(sys.argv[8]) if len(sys.argv) > 8 else 240
LO = int(os.environ.get("U17F_LO", 0))                       # only press indices >= LO / < HI (to split the work)
HI = int(os.environ.get("U17F_HI", len(pv)))
log = Log(f"u17f_head_{OUT}.txt")
HF = os.environ.get("U17F_HEADS", "u17c_head_C4")              # heads file: logs/fix/<name>.json (track C's u17c_head_*.json or my u17f_bfs_*.json)
hj = json.load(open(FIX / f"{HF}.json"))
HLEN = int(os.environ.get("U17F_HEADLEN", 0))                # 0: every head 2, 4 ... frames shorter than the reference's; else exactly this length
REFBEFORE = [x for x in os.environ.get("U17F_REFBEFORE", sys.argv[1]).split(",") if x not in ("", "-")]   # the chain the REFERENCE segment stands behind (when BEFORE itself is a shifted variant)
GSKIP = int(os.environ.get("U17F_GSKIP", 0))                 # greedy: so many frames at the page's start take no input at all (the warp before the Level 3 card: 150)
FREE = os.environ.get("U17F_FREE") == "1"                    # the next level does not read the dice (Level 3): a placement counts as good when its RAM equals the
#                                                              reference placement's except the dice / timers / pad bytes; listed with its route shift, odd or even
REFPREV = os.environ.get("U17F_REFPREV", PREV)
e = BizHawk(log_name=f"u17f_head_{OUT}.log")


def phase():
    c = core_of(e.save("u17f_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1


def st_next(stage):
    m = e.ram(0, 0x800)
    return placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)


for b in route_inputs(REFBEFORE):
    e.step(bt(b), 1)
S0 = e.msave()                                               # the true state at the previous segment's start (reference chain)
for b in seg(REFPREV):
    e.step(bt(b), 1)
stage, P = 0, None
for i, b in enumerate(sg[:400]):
    e.step(bt(b), 1)
    stage = st_next(stage)
    if stage == 3:
        P = i + 1
        break
assert P, "the reference is never set down"
PH0 = phase()
MP = bytes(e.ram(0, 0x800))                                  # the reference's RAM on its placement frame
ALLOWED = set(range(0x100, 0x200)) | {0x0B, 0x0C, 0x1A, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x75, 0x565} | set(range(0x740, 0x760))
BEST = [1]
REF = []
for b in sg[P:P + NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
FULL = NA - 7
heads = sorted({tuple(r[4]) for r in hj["results"] if r[3] == "bfs" and ((P - r[0]) % 2 == 0 and r[0] < P if not HLEN else r[0] == HLEN)}, key=lambda h: (len(h), h))
heads = [h for h in heads if h[-1] == ""] or heads           # (the last frame's button does not matter: keep the plain ones)
if REFBEFORE != BEFORE:                                      # the variant chain: its own power-on replay to the previous segment's start
    e2 = e
    e.mfree(S0)
    e.close()
    e = BizHawk(log_name=f"u17f_head_{OUT}.log")
    for b in route_inputs(BEFORE):
        e.step(bt(b), 1)
    S0 = e.msave()
MASH = tuple("AB"[i % 2] for i in range(P + 6))             # cut on the placement
log(f"reference {SEG} behind intro + {' '.join(REFBEFORE)} + {REFPREV}: placement on input {P}, alignment PC ${PH0[0]:04X} ts {PH0[1]} parity {PH0[3]}; {NA} frames in: PC ${PHN[0]:04X} ts "
    f"{PHN[1]} parity {PHN[3]}; heads: {[(len(h), [(i, b) for i, b in enumerate(h) if b]) for h in heads]} + A,B mash; presses {BTNS} on {PREV} indices {max(LO, len(pv) - S)}..{HI - 1}; variant chain intro + {' '.join(BEFORE)} + {PREV}; heads file {HF}")
T0 = max(LO, len(pv) - S)
e.mload(S0)
for b in pv[:T0]:
    e.step(bt(b), 1)
base = e.msave()
SEEN, tab, hits, nvar = {}, {}, [], 0


GREEDY = os.environ.get("U17F_GREEDY") == "1"               # no fixed heads: for every variant the page is pressed through card by card (below)
REFLEN = len(route_inputs(REFBEFORE)) + len(seg(REFPREV)) + P   # the reference's frame of the placement (route frame count)
VARLEN = len(route_inputs(BEFORE)) + len(pv)


def sig():
    m = e.ram(0, 0x800)
    return m[0x10], m[0x51A] == 0, (m[0x3FD] | m[0x3EE] << 8) == 0


def greedy(maxlen=90, skip=0):
    """from the loaded state: each frame nothing, unless A (or else B) changes (level byte, health 0, x 0) within two frames -> the page's
    cards are answered on the first frame they take a press.  Returns the head up to the placement, or None."""
    head, stage, nopp = [], 0, 0                             # skip = k: the k-th card is answered one frame late (one wait frame: the other parity)
    for _ in range(GSKIP):
        e.step((), 1)
        head.append("")
        stage = st_next(stage)
    for _ in range(maxlen):
        s0 = e.msave()
        e.step((), 1)
        e.step((), 1)
        idle = sig()                                         # (the third card shows a press one frame late: look two frames ahead)
        choice = ""
        for b in ("A", "B"):
            e.mload(s0)
            e.step((b,), 1)
            e.step((), 1)
            if sig() != idle:
                choice = b
                break
        if choice:
            nopp += 1
            if nopp == skip:
                choice = ""
        e.mload(s0)
        e.step((choice,) if choice else (), 1)
        e.mfree(s0)
        head.append(choice)
        stage = st_next(stage)
        if stage == 3:
            return head
    return None


CACHE, NCACHED = {}, [0]


def test(press):
    """press = (index in the previous segment, button) or None; the emulator stands on `base` (index T0 or the rolling base)"""
    global nvar
    out = []
    i0 = press[2] if press else T0
    for i in range(i0, len(pv)):
        b = pv[i]
        if press and press[0] == i:
            b = (b + "+" + press[1]).lstrip("+")
        e.step(bt(b), 1)
    kend = (phase(), hashlib.sha1(cut(e.ram(0, 0x800))).digest())
    if kend in CACHE:                                        # the same state and alignment at the page's start: the same page, the same merge
        for key_, hit in CACHE[kend]:
            tab[key_] = tab.get(key_, 0) + 1
            if hit:
                hits.append((press[:2] if press else None,) + hit)
                if hit[4] < BEST[0]:
                    BEST[0] = hit[4]
                    log(f"  (cached) press {press[:2] if press else None} in {PREV} + head of {hit[1]} frames: route shift {hit[4]:+d}")
        nvar += 1
        NCACHED[0] += 1
        return out
    CACHE[kend] = []
    end = e.msave()
    odd0 = False
    for hn, head in enumerate(heads + [MASH] if not GREEDY else ["greedy", "wait1", "wait2", "wait3"]):
        if GREEDY and hn > 0 and (FREE or not odd0):
            break
        e.mload(end)
        stage, ln = 0, None
        if GREEDY:
            head = greedy(skip=hn)
            if head is None:
                tab[(hn, "never set down")] = tab.get((hn, "never set down"), 0) + 1
                CACHE[kend].append(((hn, "never set down"), None))
                continue
            ln = len(head)
            if FREE:
                ph = phase()
                dd = [a_ for a_ in diff(bytes(e.ram(0, 0x800)), MP) if a_ not in ALLOWED]
                key_ = (hn, ln, f"${ph[0]:04X}", ph[1], ph[3], "same toad" if not dd else f"RAM differs {[hex(a_) for a_ in dd[:6]]}")
                tab[key_] = tab.get(key_, 0) + 1
                CACHE[kend].append((key_, (hn, ln, list(head[:ln]), list(ph[:2]), VARLEN + ln - REFLEN) if not dd else None))
                if not dd:
                    hits.append((press[:2] if press else None, hn, ln, list(head[:ln]), list(ph[:2]), VARLEN + ln - REFLEN))
                    if VARLEN + ln - REFLEN < BEST[0]:
                        BEST[0] = VARLEN + ln - REFLEN
                        log(f"  FREE: press {press[:2] if press else None} in {PREV} + head of {ln} frames (presses {[(i, b) for i, b in enumerate(head) if b]}); alignment PC ${ph[0]:04X} ts {ph[1]} parity {ph[3]}; "
                            f"route shift {VARLEN + ln - REFLEN:+d}")
                continue
            if (VARLEN + ln - REFLEN) % 2:                   # an odd shift can never merge: count it, then the three one-wait-frame heads
                ph = phase()
                key_ = (hn, ln, f"${ph[0]:04X}", ph[1], ph[3], "odd shift")
                tab[key_] = tab.get(key_, 0) + 1
                CACHE[kend].append((key_, None))
                odd0 = odd0 or hn == 0
                continue
        else:
            for k, b in enumerate(head):
                e.step(bt(b), 1)
                stage = st_next(stage)
                if stage == 3:
                    ln = k + 1
                    break
            if ln is None or (hn < len(heads) and ln != len(head)):
                tab[(hn, "not set down on the head's last frame")] = tab.get((hn, "not set down on the head's last frame"), 0) + 1
                CACHE[kend].append(((hn, "not set down on the head's last frame"), None))
                continue
        ph = phase()
        k_ = (ph, cut(e.ram(0, 0x800)))
        if k_ not in SEEN:
            same = 0
            for j in range(len(REF)):
                e.step(bt(sg[P + j]), 1)
                if j < 7:
                    continue
                if cut(e.ram(0, 0x800)) != REF[j]:
                    break
                same += 1
            if same == FULL and phase() != PHN:
                same = -1
            SEEN[k_] = same
        same = SEEN[k_]
        key_ = (hn, ln, f"${ph[0]:04X}", ph[1], ph[3], same)
        tab[key_] = tab.get(key_, 0) + 1
        out.append((hn, ln, ph[:2], same))
        CACHE[kend].append((key_, (hn, ln, list(head[:ln]), list(ph[:2]), VARLEN + ln - REFLEN) if same == FULL else None))
        if same == FULL:
            BEST[0] = min(BEST[0], VARLEN + ln - REFLEN)
            hits.append((press[:2] if press else None, hn, ln, list(head[:ln]), list(ph[:2]), VARLEN + ln - REFLEN))
            log(f"  MERGED: press {press[:2] if press else None} in {PREV} + head {hn} of {ln} frames (presses {[(i, b) for i, b in enumerate(head[:ln]) if b][:6]}); alignment PC ${ph[0]:04X} ts {ph[1]} parity {ph[3]}"
                f"; route shift against the reference {VARLEN + ln - REFLEN:+d}{'  ** SHORTER **' if VARLEN + ln < REFLEN else ''}")
    e.mfree(end)
    nvar += 1
    return out


e.mload(base)
r0 = test(None)
log(f"no extra press: {r0}")
STEP = int(os.environ.get("U17F_STEP", 1))                   # only every STEP-th index gets presses (a quick survey)
for i in range(T0, min(HI, len(pv))):
    for btn in (BTNS if (i - T0) % STEP == 0 else []):
        b = pv[i]
        if btn in b.split("+") or banned1(b + "+" + btn):
            continue
        e.mload(base)
        test((i, btn, i))
    e.mload(base)
    e.step(bt(pv[i]), 1)
    nb = e.msave()
    e.mfree(base)
    base = nb
    if (i - T0) % 50 == 49:
        log(f"    ... {PREV} index {i}: {nvar} variants ({NCACHED[0]} from the cache), {len(hits)} merged, {sum(1 for h in hits if h[5] < 0)} of them shorter (best shift {min([h[5] for h in hits], default=None)}); alignments seen {len(SEEN)}; "
            f"table {sorted(tab.items(), key=lambda t: str(t[0]))}")
        write_json(FIX / f"u17f_head_{OUT}.json", {"before": BEFORE, "prev": PREV, "segment": SEG, "P": P, "ref_phase": [PH0[0], PH0[1], PH0[3]], "hits": hits,
                                                    "table": [[list(map(str, k_)), v] for k_, v in tab.items()]})
log(f"variants {nvar}; (head, length, PC, ts, parity, identical frames of {FULL}) -> variants:")
for k_, v in sorted(tab.items(), key=lambda t: str(t[0])):
    log(f"    {k_}: {v}")
write_json(FIX / f"u17f_head_{OUT}.json", {"before": BEFORE, "prev": PREV, "segment": SEG, "P": P, "ref_phase": [PH0[0], PH0[1], PH0[3]], "hits": hits,
                                            "table": [[list(map(str, k_)), v] for k_, v in tab.items()]})
short = sorted([h for h in hits if h[5] < 0], key=lambda h: h[5])
log(f"merged {len(hits)}, shorter than the reference route: {len(short)}" + (f"; best: {short[0]}" if short else ""))
e.close()
