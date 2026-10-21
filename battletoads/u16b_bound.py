"""u16b (chain B): the A / B alternating page mash at a level boundary (recipe 3), kept only when the next segment
replays unchanged behind it.

    python u16b_bound.py <segment> <next segment> <window start index> <next level byte> <out> [NA=300]
        window start index = 0-based index into the segment's inputs from which everything is replaced by the mash
        (L4c5: 4932 = up14 frame 9665;  L6c: 2392 = up14 frame 12281)
Variants: A,B / B,A; the mash starting 0..3 frames later (empty frames first); one Select on one of the last 40 frames
before the window.  For each: the frame the toad is set down in the next level (level byte, then health 0 and x 0,
then health > 0 and x > 0), and how many of the next segment's frames 12..NA come out bit-identical to that segment's
own reference run (whole RAM, stack page excluded), trying the next segment 0 / +1 / -1 frames against the cut.
The shortest fully identical variant is written as logs/pbeam_<out>.json (bookmark <out>_end0).  Never Start in the
pattern.  No memory writes."""
import json
import os
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json, FIX, banned

SEG, NXT, W0, LVL, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 300
F = {"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11}
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))
if os.environ.get("U16B_BM"):                                 # replay the segment from another entry bookmark (the new lineage's)
    sj["bookmark"] = os.environ["U16B_BM"]
nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]
nxt = [b.replace(",", "+") for b in nj["inputs"]]
e = BizHawk(log_name=f"u16b_bound_{OUT}.log", fields=F)
cut = lambda m: m[:0x100] + m[0x200:]
SKIP = 11

from u16b_phase import sig as _core
PHASE = os.environ.get("U16B_PHASE", "1") != "0"


def phase():
    """(PC, timestamp in 1/15 CPU clocks, registers) of the core right now (a savestate is written and parsed)"""
    c = _core(e, "u16b_phase_" + OUT)
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1   # PC, timestamp, registers, frame-count parity


SEEN = {}                                                     # (phase, RAM at the cut) -> identical frames: the outcome depends on nothing else


e.load(nj["bookmark"])
PH0 = phase() if PHASE else None
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase() if PHASE else None                              # the reference's alignment NA frames in (merged = identical for ever)
PRE = int(os.environ.get("U16B_PRE", 40))                     # frames before the window that may get one extra press
OFFS = [int(v) for v in os.environ.get("U16B_OFFS", "0").split(",")]   # the next segment 0 / +1 / -1 frames against the cut
PREBTNS = os.environ.get("U16B_PREBTNS", "Select").split(",")  # ... and which buttons (the toad may still be in play there)
e.load(sj["bookmark"])
for b in seg[:W0 - PRE]:
    e.step(bt(b), 1)
base = e.msave()
print(f"{SEG}: {len(seg)} inputs, window from index {W0} (old tail: {len(seg) - W0} inputs); old tail buttons {sorted(set(seg[W0:]))}", flush=True)


def variant(first, delay, sel):
    """-> (inputs from W0-PRE to the cut, identical frames, offset used)"""
    best = None
    for off in OFFS:
        e.mload(base)
        ins, stage = [], 0
        xj, xb = sel if isinstance(sel, tuple) else ((sel, "Select") if sel is not None else (None, None))
        for j in range(PRE):
            b = seg[W0 - PRE + j]
            if xj == j and xb not in b.split("+"):
                b = (b + "+" + xb).lstrip("+")
            s = e.step(bt(b), 1)
            ins.append(b)
        pat = [first, "B" if first == "A" else "A"]
        for j in range(1500):
            b = "" if j < delay else pat[(j - delay) % 2]
            if xj == PRE + j and xb not in b.split("+"):
                b = (b + "+" + xb).lstrip("+")
            s = e.step(bt(b), 1)
            ins.append(b)
            if stage == 0 and s.level == LVL:
                stage = 1
            if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
                stage = 2
            if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
                break
        else:
            return None
        if off == 1:
            e.step((), 1)
            ins.append("")
        elif off == -1:                                       # cut one frame sooner: replay to one input less
            ins = ins[:-1]
            e.mload(base)
            for b in ins:
                e.step(bt(b), 1)
        variant.ph = phase() if PHASE else None
        key = (variant.ph, cut(e.ram(0, 0x800))) if PHASE else None
        if key is not None and key in SEEN:
            same = SEEN[key]
        else:
            same = 0
            for j in range(len(REF)):
                e.step(bt(nxt[j]), 1)
                if j < SKIP:
                    continue
                if cut(e.ram(0, 0x800)) != REF[j]:
                    break
                same += 1
            if PHASE and same == len(REF) - SKIP and phase() != PHN:
                same = -1                                      # tracks the old run but is still out of step
            if key is not None:
                SEEN[key] = same
        if best is None or same > best[1]:
            best = (ins, same, off)
        if same == len(REF) - SKIP:
            break
    return best


FULL = NA - SKIP
res = []
cands = [(f, d, None) for d in (0, 1, 2, 3) for f in ("A", "B")] + [("A", 0, (j, btn)) for j in range(PRE - 1, -1, -1) for btn in PREBTNS]
TAIL = len(seg) - W0                                           # one extra press inside the mash itself (the page / warp card: harmless)
cands += [("A", 0, (PRE + j, btn)) for j in range(TAIL - 1, -1, -1) for btn in ("Select", "Up", "Down")]
for first, delay, sel in cands:
    r = variant(first, delay, sel)
    if r is None:
        continue
    ins, same, off = r
    ln = W0 - PRE + len(ins)
    res.append((same == FULL, ln, first, delay, sel, off, same))
    ph = variant.ph
    pht = "" if not ph else (f" phase PC ${ph[0]:04X} ts {ph[1]} (ref ${PH0[0]:04X} {PH0[1]}" + (f": {(ph[1] - PH0[1]) / 15:+.2f} cycles)" if ph[0] == PH0[0] else ")"))
    print(f"  first {first} delay {delay} Select {sel}: segment {ln} inputs ({ln - len(seg):+d}), next-level frames identical {same}/{FULL} (offset {off}){pht}{'  IN SYNC' if same == FULL else ''}", flush=True)
    good = sorted(x[1] for x in res if x[0])
    if len(good) >= 10 and sel is not None:
        break
print("phases seen at the cut -> identical frames:", sorted(((f"${k[0][0]:04X}", k[0][1], "same parity" if k[0][3] == PH0[3] else "ODD shift", v) for k, v in SEEN.items()), key=lambda t: t[:3]), flush=True)
good = sorted((x for x in res if x[0]), key=lambda x: (x[1], x[4] is not None, x[3]))
write_json(FIX / f"u16b_bound_{OUT}.json", {"segment": SEG, "next": NXT, "results": [list(r[:4]) + [list(r[4]) if isinstance(r[4], tuple) else r[4]] + list(r[5:]) for r in res]})
if good:
    _, ln, first, delay, sel, off, same = good[0]
    ins, same, off = variant(first, delay, sel)
    full = seg[:W0 - PRE] + ins
    e.load(sj["bookmark"])
    for b in full:
        s = e.step(bt(b), 1)
    e.save(OUT + "_end0")
    d = dict(sj)
    d.update(inputs=full, built_from=SEG, mash=[first, delay, sel, off])
    write_json(LOGS_DIR / f"pbeam_{OUT}.json", d)
    print(f"wrote pbeam_{OUT}.json: {len(full)} inputs ({len(full) - len(seg):+d} vs {SEG}); mash first {first}, delay {delay}, Select {sel}, offset {off}; "
          f"banned presses {sum(1 for x in full if banned(x))} (the old segment: {sum(1 for x in seg if banned(x))}); bookmark {OUT}_end0", flush=True)
else:
    print("no variant keeps the next segment in sync", flush=True)
e.close()
