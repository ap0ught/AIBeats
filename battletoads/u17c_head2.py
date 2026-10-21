"""Track C: the page at the head of a segment, second stage: the hidden alignment is moved by ONE harmless press while the toad
is still in play, i.e. on one of the last frames of the PREVIOUS segment (presses on the page itself do not move it).

    python u17c_head2.py <previous segment> <segment> <next level byte> <out previous (C...)> <out (C...)> [S=70] [NA=240] [buttons=Select]
        needs logs/fix/u17c_head_<out>.json (u17c_head.py: the BFS heads and P)
    variants: one extra press on one of the previous segment's last S frames x every BFS head with an even gain
    test: the previous segment (from ITS bookmark) + head, then the segment's inputs after P: frames 8..NA identical to the
          reference and the alignment NA frames in equal to the reference's
    -> logs/pbeam_<out previous>.json, logs/pbeam_<out>.json, states/<out previous>_end0b.State, logs/fix/u17c_head2_<out>.txt"""
import json
import os
import sys

from u17c_lib import *
from u16b_phase import core_of

PREV, SEG, LVL, OUTP, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
S = int(sys.argv[6]) if len(sys.argv) > 6 else 70
NA = int(sys.argv[7]) if len(sys.argv) > 7 else 240
BTNS = (sys.argv[8] if len(sys.argv) > 8 else "Select").split(",")
log = Log(f"u17c_head2_{OUT}.txt")
hj = json.load(open(FIX / f"u17c_head_{OUT}.json"))
P = hj["P"]
heads = sorted({tuple(r[4]) for r in hj["results"] if r[3] == "bfs" and (P - r[0]) % 2 == 0 and r[0] < P}, key=len)
pj, sj = segj(PREV), segj(SEG)
pv, sg = seg(PREV), seg(SEG)
e = BizHawk(log_name=f"u17c_head2_{OUT}.log")


def phase():
    c = core_of(e.save("u17c_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1


SBM = os.environ.get("U17C_HEAD_BM") or sj["bookmark"]       # the TRUE chain state at the segment's entry (an old bookmark can differ in the pad bytes)
e.load(SBM)
for b in sg[:P]:
    e.step(bt(b), 1)
PH0 = phase()
mP = bytes(e.ram(0, 0x800))
REF = []
for b in sg[P:P + NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
FULL = NA - 7
log(f"reference {SEG} from {SBM}: placement on input {P}, alignment PC ${PH0[0]:04X} ts {PH0[1]} parity {PH0[3]}; {len(heads)} BFS heads with an even gain, lengths {sorted(set(len(h) for h in heads))}")
# sanity: the previous segment from its own bookmark ends in the segment's bookmark state
e.load(pj["bookmark"])
for b in pv:
    e.step(bt(b), 1)
m_end = bytes(e.ram(0, 0x800))
e.load(sj["bookmark"])
d0 = diff(m_end, bytes(e.ram(0, 0x800)))
log(f"{PREV} from {pj['bookmark']} ends in {sj['bookmark']}'s RAM: {len(d0)} bytes differ {[hex(a) for a in d0[:10]]}")
e.load(pj["bookmark"])
T0 = len(pv) - S
for b in pv[:T0]:
    e.step(bt(b), 1)
base = e.msave()
SEEN, res, hit = {}, [], None


def test(press, head):
    """press = (index in the previous segment, button) or None"""
    e.mload(base)
    for i in range(T0, len(pv)):
        b = pv[i]
        if press and press[0] == i:
            if press[1] in b.split("+") or banned1(b + "+" + press[1]):
                return None
            b = (b + "+" + press[1]).lstrip("+")
        e.step(bt(b), 1)
    stage = 0
    for b in head:
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        stage = placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)
    if stage != 3:
        return None
    ph = phase()
    k = (ph, cut(e.ram(0, 0x800)))
    if k not in SEEN:
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
        SEEN[k] = same
    return ph, SEEN[k]


for head in heads[:8]:
    for press in [None] + [(i, btn) for i in range(len(pv) - 1, T0 - 1, -1) for btn in BTNS]:
        r = test(press, head)
        if r is None:
            continue
        res.append((len(head), press, r[0][:2] + (r[0][3],), r[1]))
        if r[1] == FULL:
            hit = (press, head)
            log(f"  MERGED: press {press} in {PREV} + head of {len(head)} frames (presses {[(i, b) for i, b in enumerate(head) if b]}); alignment PC ${r[0][0]:04X} ts {r[0][1]}")
            break
    if hit:
        break
tab = {}
for ln, press, ph, same in res:
    tab.setdefault((ln, ph), set()).add(same)
log(f"variants {len(res)}; (head length, (PC, ts, parity)) -> identical frames (of {FULL}): {sorted((k, sorted(v)) for k, v in tab.items())}")
if hit:
    press, head = hit
    newp = list(pv)
    if press:
        newp[press[0]] = (newp[press[0]] + "+" + press[1]).lstrip("+")
    full = list(head) + sg[P:]
    # one piece: previous segment from its bookmark, then the whole new segment against the old segment's own end state
    e.load(sj["bookmark"])
    for b in sg:
        e.step(bt(b), 1)
    ref_end = bytes(e.ram(0, 0x800))
    e.load(pj["bookmark"])
    for b in newp:
        e.step(bt(b), 1)
    e.save(OUTP + "_end0b")
    for b in full:
        e.step(bt(b), 1)
    m = bytes(e.ram(0, 0x800))
    dd = diff(m, ref_end)
    log(f"one piece: {PREV}' ({len(newp)}) + {SEG}' ({len(full)}, {len(full) - len(sg):+d}); end {toad(m)}; RAM bytes differing from {SEG}'s own end: {len(dd)} {[hex(a) for a in dd[:10]]}")
    if not dd:
        e.save(OUT + "_end0b")
        d1 = dict(pj); d1.update(inputs=newp, built_from=PREV, sync_press=list(press) if press else None)
        write_seg(OUTP, d1)
        d2 = dict(sj); d2.update(bookmark=OUTP + "_end0b", inputs=full, built_from=SEG, head=[P, len(head)], head_presses=[(i, b) for i, b in enumerate(head) if b])
        write_seg(OUT, d2)
        log(f"wrote pbeam_{OUTP}.json ({len(newp)}) and pbeam_{OUT}.json ({len(full)}); banned {banned(newp + full)}")
else:
    log("NO merging variant")
e.close()
